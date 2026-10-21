"""Construction de la couche Silver pour une source Bronze.

Bloc S-1 : GTFS Yélo (S02) → standardized, cleaned, deduplicated, quality.
Usage, depuis la racine :
    python scripts/build_silver.py --source S02 --bronze data/bronze/gtfs/larochelle/S02_2026-10-21
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.cleaning import gtfs  # noqa: E402
from src.cleaning.audit import Suivi, verifier_conservation  # noqa: E402
from src.evaluation.qualite import indicateurs_gtfs  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import construire_run_id, lire_manifeste, verifier_manifeste  # noqa: E402

SILVER = RACINE / "data" / "silver"
CONFIG = RACINE / "config" / "silver.yaml"


def construire_gtfs(source_id: str, bronze_relatif: str, territoire: str) -> dict:
    run_id = construire_run_id()
    bronze = RACINE / bronze_relatif
    anomalies = verifier_manifeste(bronze)
    if anomalies:
        raise RuntimeError(f"{source_id} : Bronze non conforme, Silver refusé : {anomalies}")
    manifeste = lire_manifeste(bronze)
    fichier = manifeste["fichiers"][0]
    archive = bronze / fichier["nom"]
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    feed = gtfs.lire_table_gtfs(archive, "feed_info.txt")
    date_donnee = (f"validite {feed['feed_start_date'].iloc[0]}-{feed['feed_end_date'].iloc[0]}"
                   if feed is not None else "feed_info absent")
    origine = {"source_id": source_id, "dossier": bronze_relatif, "run_id": manifeste["run_id"],
               "fichier": fichier["nom"], "sha256": fichier["sha256"]}

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
        ("quality", f"rejets_{source_id}.parquet", journal[journal["niveau"] == "rejet"],
         ["regle_id", "id_origine", "valeur_constatee"]),
        ("quality", f"alertes_{source_id}.parquet", journal[journal["niveau"] != "rejet"],
         ["regle_id", "id_origine", "etape"]),
        ("quality", f"qualite_indicateurs_{source_id}.parquet", qualite, ["q_id", "libelle"]),
    ]
    bilan = {"run_id": run_id, "tables": {}}
    for dossier, nom, table, cle in sorties:
        description = ecrire_table(table, SILVER / dossier / nom, cle)
        mettre_a_jour_manifeste(SILVER / dossier, nom, {
            "run_id": run_id, "origine_bronze": origine, "table": description,
            "parametres": {"coordonnees": config["coordonnees"], "gtfs": config["gtfs"]},
        })
        bilan["tables"][f"{dossier}/{nom}"] = description["lignes"]
    bilan["rejets_par_regle"] = journal.groupby(["niveau", "regle_id"]).size().to_dict()
    bilan["qualite"] = qualite[["q_id", "libelle", "valeur", "unite"]].values.tolist()
    return bilan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Construction Silver d'une source.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--bronze", required=True, help="Dossier Bronze daté, relatif à la racine.")
    parser.add_argument("--territoire", default="larochelle")
    args = parser.parse_args(argv)
    if args.source != "S02":
        print(f"{args.source} : pas encore pris en charge (bloc S-1 = S02).")
        return 2
    bilan = construire_gtfs(args.source, args.bronze, args.territoire)
    print(f"run_id : {bilan['run_id']}")
    for table, lignes in bilan["tables"].items():
        print(f"  {table:<55} {lignes:>6} lignes")
    print("Règles déclenchées :")
    for (niveau, regle), nombre in sorted(bilan["rejets_par_regle"].items()):
        print(f"  {niveau:<10} {regle:<6} {nombre}")
    print("Qualité :")
    for q_id, libelle, valeur, unite in bilan["qualite"]:
        print(f"  {q_id:<6} {libelle:<45} {valeur} {unite}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
