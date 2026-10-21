"""Construction de la couche Silver pour une source Bronze.

S-1 : GTFS Yélo (S02). S-2 : GBFS Citiz (S01) et Yélo vélo (S08).
Usage, depuis la racine :
    python scripts/build_silver.py --source S02 --bronze data/bronze/gtfs/larochelle/S02_2026-10-21
    python scripts/build_silver.py --source S01 --bronze data/bronze/gbfs/larochelle/S01_2026-10-21
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.cleaning import gbfs as silver_gbfs  # noqa: E402
from src.cleaning import gtfs  # noqa: E402
from src.cleaning.audit import Suivi, verifier_conservation  # noqa: E402
from src.evaluation.qualite import indicateurs_gbfs, indicateurs_gtfs  # noqa: E402
from src.ingestion.gbfs import trouver_stations  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import construire_run_id, lire_manifeste, verifier_manifeste  # noqa: E402

SILVER = RACINE / "data" / "silver"
CONFIG = RACINE / "config" / "silver.yaml"


def ouvrir_bronze(source_id: str, bronze_relatif: str) -> tuple[Path, dict, dict]:
    """Vérifie le dossier Bronze avant toute lecture. Renvoie (dossier, manifeste, origine)."""
    bronze = RACINE / bronze_relatif
    anomalies = verifier_manifeste(bronze)
    if anomalies:
        raise RuntimeError(f"{source_id} : Bronze non conforme, Silver refusé : {anomalies}")
    manifeste = lire_manifeste(bronze)
    if manifeste["source_id"] != source_id:
        raise RuntimeError(f"Le dossier {bronze_relatif} contient {manifeste['source_id']}, pas {source_id}.")
    origine = {"source_id": source_id, "dossier": bronze_relatif, "run_id": manifeste["run_id"],
               "fichiers": {f["nom"]: f["sha256"] for f in manifeste["fichiers"]}}
    return bronze, manifeste, origine


def ecrire_sorties(sorties: list, *, run_id: str, origine: dict, parametres: dict) -> dict[str, int]:
    lignes = {}
    for dossier, nom, table, cle in sorties:
        description = ecrire_table(table, SILVER / dossier / nom, cle)
        mettre_a_jour_manifeste(SILVER / dossier, nom, {
            "run_id": run_id, "origine_bronze": origine, "table": description, "parametres": parametres,
        })
        lignes[f"{dossier}/{nom}"] = description["lignes"]
    return lignes


def journaux(source_id: str, journal) -> list:
    return [
        ("quality", f"rejets_{source_id}.parquet", journal[journal["niveau"] == "rejet"],
         ["regle_id", "id_origine", "valeur_constatee"]),
        ("quality", f"alertes_{source_id}.parquet", journal[journal["niveau"] != "rejet"],
         ["regle_id", "id_origine", "etape"]),
    ]


def construire_gtfs(source_id: str, bronze_relatif: str, territoire: str, config: dict) -> dict:
    run_id = construire_run_id()
    bronze, manifeste, origine = ouvrir_bronze(source_id, bronze_relatif)
    fichier = manifeste["fichiers"][0]
    archive = bronze / fichier["nom"]

    feed = gtfs.lire_table_gtfs(archive, "feed_info.txt")
    date_donnee = (f"validite {feed['feed_start_date'].iloc[0]}-{feed['feed_end_date'].iloc[0]}"
                   if feed is not None else "feed_info absent")
    suivi = Suivi(run_id)
    standard = gtfs.standardiser_stops(archive, source_id=source_id, fichier_origine=f"{bronze_relatif}/{fichier['nom']}",
                                       sha256_origine=fichier["sha256"], date_donnee=date_donnee, run_id=run_id)
    propre = gtfs.nettoyer_stops(standard, suivi, gtfs.quais_desservis(archive), config["coordonnees"])
    n_rejets = suivi.compter("rejet", "cleaned")
    verifier_conservation(len(standard), len(propre), n_rejets, "cleaned")
    offre, correspondances = gtfs.dedupliquer_zones(propre, suivi, source_id=source_id,
                                                    seuil_rg06_m=config["gtfs"]["seuil_rg06_m"])
    gtfs.controler_correspondances(propre, correspondances)

    journal = suivi.table()
    qualite = indicateurs_gtfs(source_id=source_id, run_id=run_id, standard=standard, propre=propre,
                               offre=offre, correspondances=correspondances, n_rejets=n_rejets, feed_info=feed)
    sorties = [
        ("standardized", f"gtfs_stops_{territoire}.parquet", standard, ["stop_id", "id_origine"]),
        ("cleaned", f"gtfs_stops_{territoire}.parquet", propre, ["stop_id"]),
        ("deduplicated", f"offre_arrets_{territoire}.parquet", offre, ["offre_id"]),
        ("deduplicated", f"dedup_correspondances_{source_id}.parquet", correspondances, ["id_origine"]),
        *journaux(source_id, journal),
        ("quality", f"qualite_indicateurs_{source_id}.parquet", qualite, ["q_id", "libelle"]),
    ]
    parametres = {"coordonnees": config["coordonnees"], "gtfs": config["gtfs"]}
    return {"run_id": run_id, "tables": ecrire_sorties(sorties, run_id=run_id, origine=origine, parametres=parametres),
            "regles": journal.groupby(["niveau", "regle_id"]).size().to_dict(),
            "qualite": qualite[["q_id", "libelle", "valeur", "unite"]].values.tolist()}


def construire_gbfs(source_id: str, bronze_relatif: str, territoire: str, config: dict) -> dict:
    run_id = construire_run_id()
    bronze, manifeste, origine = ouvrir_bronze(source_id, bronze_relatif)
    reglage = config["gbfs"][source_id]
    noms = {f["nom"]: f for f in manifeste["fichiers"]}

    # Flux complet : station_information.json. Export figé (S08) : stations embarquées dans gbfs.json.
    nom_fichier = "station_information.json" if "station_information.json" in noms else "gbfs.json"
    contenu = json.loads((bronze / nom_fichier).read_text(encoding="utf-8"))
    stations = (contenu["data"]["stations"] if nom_fichier == "station_information.json"
                else trouver_stations(contenu) or [])
    last_updated = contenu.get("last_updated")

    suivi = Suivi(run_id)
    standard, ignores = silver_gbfs.standardiser_stations(
        stations, source_id=source_id, fichier_origine=f"{bronze_relatif}/{nom_fichier}",
        sha256_origine=noms[nom_fichier]["sha256"], date_donnee=f"last_updated {last_updated}", run_id=run_id)
    propre = silver_gbfs.nettoyer_stations(standard, suivi, config["coordonnees"])
    n_rejets = suivi.compter("rejet", "cleaned")
    verifier_conservation(len(standard), len(propre), n_rejets, "cleaned")
    offre = silver_gbfs.construire_offre(propre, suivi, mode=reglage["mode"], source_id=source_id)

    journal = suivi.table()
    qualite = indicateurs_gbfs(source_id=source_id, run_id=run_id, standard=standard, offre=offre,
                               n_rejets=n_rejets, last_updated=last_updated, champs_ignores=ignores,
                               n_rg07=int((journal["regle_id"] == "RG-07").sum()))
    nom = reglage["nom"]
    sorties = [
        ("standardized", f"gbfs_stations_{nom}_{territoire}.parquet", standard, ["station_id", "id_origine"]),
        ("cleaned", f"gbfs_stations_{nom}_{territoire}.parquet", propre, ["station_id"]),
        ("deduplicated", f"offre_{reglage['mode']}_{territoire}.parquet", offre, ["offre_id"]),
        *journaux(source_id, journal),
        ("quality", f"qualite_indicateurs_{source_id}.parquet", qualite, ["q_id", "libelle"]),
    ]
    parametres = {"coordonnees": config["coordonnees"], "gbfs": reglage,
                  "fichier_lu": nom_fichier, "champs_non_repris_rc14": ignores}
    return {"run_id": run_id, "tables": ecrire_sorties(sorties, run_id=run_id, origine=origine, parametres=parametres),
            "regles": journal.groupby(["niveau", "regle_id"]).size().to_dict(),
            "qualite": qualite[["q_id", "libelle", "valeur", "unite"]].values.tolist()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Construction Silver d'une source.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--bronze", required=True, help="Dossier Bronze daté, relatif à la racine.")
    parser.add_argument("--territoire", default="larochelle")
    args = parser.parse_args(argv)
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    if args.source == "S02":
        bilan = construire_gtfs(args.source, args.bronze, args.territoire, config)
    elif args.source in config.get("gbfs", {}):
        bilan = construire_gbfs(args.source, args.bronze, args.territoire, config)
    else:
        print(f"{args.source} : pas encore pris en charge.")
        return 2

    print(f"run_id : {bilan['run_id']}")
    for table, lignes in bilan["tables"].items():
        print(f"  {table:<55} {lignes:>6} lignes")
    print("Règles déclenchées :" if bilan["regles"] else "Règles déclenchées : aucune")
    for (niveau, regle), nombre in sorted(bilan["regles"].items()):
        print(f"  {niveau:<10} {regle:<6} {nombre}")
    print("Qualité :")
    for q_id, libelle, valeur, unite in bilan["qualite"]:
        print(f"  {q_id:<6} {libelle:<45} {valeur} {unite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
