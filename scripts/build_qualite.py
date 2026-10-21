"""Gold / qualité : tableau unique qualité, couverture des données, couverture de mobilité.

Lit les manifestes et tables Silver et Gold, vérifie les empreintes Bronze, calcule chaque
indicateur avec sa formule, son seuil (config/qualite.yaml) et son statut.
Usage, depuis la racine :
    python scripts/build_qualite.py --territoire larochelle [--date-reference AAAA-MM-JJ]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import geopandas as gpd
import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.evaluation.protocole_qualite import Releve, completude, couverture_mobilite, jours_depuis, part  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id, lire_manifeste, verifier_manifeste  # noqa: E402

DATA = RACINE / "data"
SILVER, GOLD = DATA / "silver", DATA / "gold"
SOURCES_OFFRE = {"S02": "bus", "S01": "citiz", "S08": "velo"}


def manifestes(couche: Path) -> dict[str, dict]:
    """{ 'dossier/table': entrée du manifeste } pour toute une couche."""
    entrees = {}
    for chemin in sorted(couche.glob("*/_manifest.json")):
        for nom, entree in json.loads(chemin.read_text(encoding="utf-8"))["tables"].items():
            entrees[f"{chemin.parent.name}/{nom}"] = entree
    return entrees


def lignes(entrees: dict, cle: str) -> int:
    return int(entrees[cle]["table"]["lignes"]) if cle in entrees else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tableau qualité Gold.")
    parser.add_argument("--territoire", default="larochelle")
    parser.add_argument("--date-reference", default=None, help="AAAA-MM-JJ ; par défaut, aujourd'hui (Paris).")
    args = parser.parse_args(argv)
    t = args.territoire
    reference = (date.fromisoformat(args.date_reference) if args.date_reference
                 else datetime.now(ZoneInfo("Europe/Paris")).date())
    seuils = yaml.safe_load((RACINE / "config" / "qualite.yaml").read_text(encoding="utf-8"))["seuils"]
    run_id = construire_run_id()
    r = Releve(seuils, reference, run_id)
    silver, gold = manifestes(SILVER), manifestes(GOLD)

    cellules = gpd.read_parquet(SILVER / "spatial" / f"cellules_{t}.parquet")
    offres = gpd.read_parquet(SILVER / "spatial" / f"offre_points_{t}.parquet")
    paires = pd.read_parquet(GOLD / "accessibility" / f"paires_cellule_offre_{t}.parquet")
    noeuds = gpd.read_parquet(SILVER / "cleaned" / f"osm_walk_nodes_{t}.parquet")
    correspondances = pd.read_parquet(SILVER / "deduplicated" / "dedup_correspondances_S02.parquet")
    communes = gpd.read_parquet(SILVER / "cleaned" / "admin_communes_5epci.parquet")
    communes = communes[communes["territoire"] == t]

    # ---------- QUALITÉ : complétude ----------
    std = {"S02": f"standardized/gtfs_stops_{t}.parquet", "S01": f"standardized/gbfs_stations_citiz_{t}.parquet",
           "S08": f"standardized/gbfs_stations_yelo_{t}.parquet"}
    for source, relatif in std.items():
        table = pd.read_parquet(SILVER / relatif)
        lat, lon = ("stop_lat", "stop_lon") if source == "S02" else ("lat", "lon")
        r.ajouter(f"QC-COMP-01:{source}", "complétude", "qualite", source, relatif, "coordonnées renseignées",
                  "lignes avec lat et lon / lignes", completude(table, [lat, lon]), "part")
        if source != "S02":
            r.ajouter(f"QC-COMP-02:{source}", "complétude", "qualite", source, relatif, "capacité renseignée",
                      "stations avec capacity / stations", completude(table, ["capacity"]), "part")
    r.ajouter("QC-COMP-03", "complétude", "qualite", "S03", t, "population renseignée par carreau",
              "carreaux avec ind / carreaux", completude(cellules, ["pop"]), "part")

    # ---------- QUALITÉ : validité, cohérence de conservation ----------
    paires_sources = {"S02": (f"gtfs_stops_{t}",), "S01": (f"gbfs_stations_citiz_{t}",),
                      "S08": (f"gbfs_stations_yelo_{t}",), "S03": ("filosofi_carreaux_5epci",),
                      "S04": ("admin_communes_5epci", "admin_epci_5epci"),
                      "S05": (f"osm_walk_nodes_{t}", f"osm_walk_edges_{t}")}
    for source, tables in paires_sources.items():
        entree = sum(lignes(silver, f"standardized/{n}.parquet") for n in tables)
        sortie = sum(lignes(silver, f"cleaned/{n}.parquet") for n in tables)
        rejets = lignes(silver, f"quality/rejets_{source}.parquet")
        r.ajouter(f"QC-VAL-01:{source}", "validité", "qualite", source, ", ".join(tables), "lignes valides",
                  "1 − rejets / lignes standardisées", 1 - part(rejets, entree), "part")
        r.ajouter(f"QC-COH-01:{source}", "cohérence", "qualite", source, ", ".join(tables),
                  "conservation des lignes (CS-01)", "1 si standardisées = nettoyées + rejets",
                  float(entree == sortie + rejets), "booléen")

    # ---------- QUALITÉ : unicité ----------
    for nom, table, cle in [("cellules", cellules, ["cell_id"]), ("offre_points", offres, ["offre_id"]),
                            ("osm_walk_nodes", noeuds, ["node_id"]),
                            ("paires", paires, ["cell_id", "offre_id", "methode", "variante"])]:
        r.ajouter(f"QC-UNI-01:{nom}", "unicité", "qualite", "toutes", nom, f"clé {'+'.join(cle)} unique",
                  "1 − lignes en double / lignes", 1 - part(int(table.duplicated(subset=cle).sum()), len(table)), "part")
    r.ajouter("QC-UNI-02", "unicité", "qualite", "S02", "gtfs", "réduction par dédoublonnage (quais → zones)",
              "1 − options bus / quais", 1 - part(int((offres["mode"] == "bus").sum()), len(correspondances)), "part")

    # ---------- QUALITÉ : cohérence ----------
    r.ajouter("QC-COH-02", "cohérence", "qualite", "S03+S04", t, "centroïde dans la commune attribuée (J-02)",
              "carreaux concordants / carreaux", float(cellules["centroide_dans_commune"].mean()), "part")
    ref = paires[(paires["methode"] == "reseau") & (paires["variante"] == "reference")]
    vol = paires[paires["methode"] == "vol_oiseau"]
    sans = paires[paires["variante"] == "sans_trunk"]
    cles_ref = set(zip(ref["cell_id"], ref["offre_id"]))
    r.ajouter("QC-COH-03", "cohérence", "qualite", "S05", "paires", "paires réseau retrouvées à vol d'oiseau (J-06)",
              "paires réseau ∩ vol d'oiseau / paires réseau",
              part(len(cles_ref & set(zip(vol["cell_id"], vol["offre_id"]))), len(cles_ref)), "part")
    r.ajouter("QC-COH-04", "cohérence", "qualite", "S05", "paires", "sensibilité RC-01 : paires perdues sans trunk",
              "paires référence absentes sans trunk / paires référence",
              part(len(cles_ref - set(zip(sans["cell_id"], sans["offre_id"]))), len(cles_ref)), "part")
    pop_s03 = float(gpd.read_parquet(SILVER / "cleaned" / "filosofi_carreaux_5epci.parquet",
                                     columns=["territoire", "ind", "geometry"]).query("territoire == @t")["ind"].sum())
    r.ajouter("QC-COH-05", "cohérence", "qualite", "S03", t, "anti-double comptage : population ventilée une fois",
              "1 si Σ pop carreaux (spatial) = Σ ind Filosofi du territoire et carreaux uniques",
              float(abs(float(cellules["pop"].sum()) - pop_s03) < 1e-6 and not cellules["cell_id"].duplicated().any()),
              "booléen")

    # ---------- QUALITÉ : fraîcheur (dates lues dans les manifestes Bronze) ----------
    bronze = {}
    for entree in silver.values():
        origine = entree.get("origine_bronze")
        if origine:
            bronze[origine["source_id"]] = origine["dossier"]
    versions = {s: lire_manifeste(RACINE / d)["version_producteur"] for s, d in bronze.items()}
    for source in ("S01", "S08"):
        dates = versions[source]["last_updated"]
        r.ajouter(f"QC-FRA-GBFS:{source}", "fraîcheur", "qualite", source, "last_updated", "âge du flux GBFS",
                  "date de référence − last_updated le plus ancien", max(jours_depuis(v, reference) for v in dates.values()), "jours")
    r.ajouter("QC-FRA-OSM", "fraîcheur", "qualite", "S05", "date_requete", "âge du graphe piéton",
              "date de référence − date de la requête", jours_depuis(versions["S05"]["date_requete"], reference), "jours")
    r.ajouter("QC-FRA-GTFS", "fraîcheur", "qualite", "S02", "feed_info", "validité GTFS restante",
              "feed_end_date − date de référence", -jours_depuis(versions["S02"]["feed_end_date"], reference), "jours")
    r.ajouter("QC-FRA-ADMIN", "fraîcheur", "qualite", "S04", "édition", "âge de l'édition Admin Express",
              "date de référence − 2026-01-01 (édition déclarée)", jours_depuis("2026-01-01", reference), "jours",
              versions["S04"].get("edition_declaree"))
    r.ajouter("QC-FRA-FILOSOFI", "fraîcheur", "qualite", "S03", "millésime", "âge du millésime Filosofi",
              "année de référence − millésime", reference.year - int(versions["S03"]["millesime"]), "années")

    # ---------- QUALITÉ : traçabilité ----------
    conformes = sum(1 for d in bronze.values() if not verifier_manifeste(RACINE / d))
    r.ajouter("QC-TRA-01", "traçabilité", "qualite", "toutes", "bronze", "dossiers Bronze conformes à leur manifeste",
              "dossiers sans anomalie / dossiers lus par Silver", part(conformes, len(bronze)), "part",
              ", ".join(f"{s}={d.split('/')[-1]}" for s, d in sorted(bronze.items())))
    toutes = {**{f"silver/{k}": (SILVER / k, v) for k, v in silver.items()},
              **{f"gold/{k}": (GOLD / k, v) for k, v in gold.items()}}
    empreintes = sum(1 for chemin, v in toutes.values() if chemin.exists() and calculer_sha256(chemin) == v["table"]["sha256"])
    r.ajouter("QC-TRA-02", "traçabilité", "qualite", "toutes", "silver+gold", "tables conformes à leur empreinte",
              "tables dont le SHA-256 = manifeste / tables", part(empreintes, len(toutes)), "part")
    propres = sum(1 for _, v in toutes.values() if not str(v["run_id"]).endswith("-modifie"))
    r.ajouter("QC-TRA-03", "traçabilité", "qualite", "toutes", "silver+gold", "tables produites par du code commité",
              "tables dont le run_id n'a pas -modifie / tables", part(propres, len(toutes)), "part")

    # ---------- KPI DE JOINTURE ----------
    r.ajouter("QC-JOI-01", "jointure", "qualite", "S04", t, "options rattachées à une commune de l'EPCI (J-01)",
              "options avec commune / options", float((~offres["hors_epci"]).mean()), "part")
    r.ajouter("QC-JOI-02", "jointure", "qualite", "S05", t, "population rattachée au réseau à ≤ 400 m",
              "Σ pop (dist_snap ≤ 400) / Σ pop", part(float(cellules.loc[cellules["dist_snap_m"] <= 400, "pop"].sum()),
                                                       float(cellules["pop"].sum())), "part")
    r.ajouter("QC-JOI-03", "jointure", "qualite", "S05", t, "options rattachées au réseau à ≤ 400 m",
              "options (dist_snap ≤ 400) / options", float((offres["dist_snap_m"] <= 400).mean()), "part")
    r.ajouter("QC-JOI-04", "jointure", "qualite", "S02", "gtfs", "quais rattachés par parent_station (Q4)",
              "quais méthode parent_station / quais", float((correspondances["methode"] == "parent_station").mean()), "part")
    r.ajouter("QC-JOI-05", "jointure", "qualite", "S05", t, "nœuds dans la composante principale (Q7)",
              "nœuds de la composante 0 / nœuds", float(noeuds["composante_principale"].mean()), "part")

    # ---------- COUVERTURE DES DONNÉES ----------
    r.ajouter("CD-01", "couverture des données", "couverture_donnees", "S03", t, "communes de l'EPCI avec au moins un carreau",
              "communes avec carreau / communes", part(len(set(cellules["commune_insee"]) & set(communes["code_insee"])),
                                                      len(communes)), "part")
    pop_legale = float(communes["population"].sum())
    r.ajouter("CD-02", "couverture des données", "couverture_donnees", "S03+S04", t, "population décrite par Filosofi",
              "Σ ind Filosofi 2021 / Σ population légale Admin Express", part(float(cellules["pop"].sum()), pop_legale), "rapport")
    r.ajouter("CD-03", "couverture des données", "couverture_donnees", "S05", t, "population dans le rayon du réseau piéton",
              "= QC-JOI-02 vu comme couverture", part(float(cellules.loc[cellules["dist_snap_m"] <= 400, "pop"].sum()),
                                                      float(cellules["pop"].sum())), "part")
    modes = sorted(offres["mode"].unique())
    r.ajouter("CD-04", "couverture des données", "couverture_donnees", "registre", t, "modes de mobilité décrits par une source",
              "modes ingérés (autres modes TC : S19, à rechercher)", len(modes), "modes", ", ".join(modes) + " ; train et navettes : non recherchés (R24)")
    imputes = cellules["est_impute"].astype(bool)
    r.ajouter("CD-05", "couverture des données", "couverture_donnees", "S03", t, "population imputée (secret statistique, Q8)",
              "Σ pop carreaux i_est_200 = 1 / Σ pop", part(float(cellules.loc[imputes, "pop"].sum()), float(cellules["pop"].sum())),
              "part", f"carreaux imputés : {imputes.mean():.1%}")

    # ---------- COUVERTURE DE MOBILITÉ (5 min, réseau, variante de référence) ----------
    desservie, totale, taux = couverture_mobilite(cellules, paires)
    r.ajouter("CM-01", "couverture de mobilité", "couverture_mobilite", "toutes", t, "population à ≤ 5 min d'au moins une option",
              "Σ pop des carreaux ayant ≥ 1 paire réseau / Σ pop (chaque carreau une fois)", taux, "part",
              f"{desservie:,.0f} / {totale:,.0f} habitants".replace(",", " "))
    for numero, mode in zip(("CM-02", "CM-03", "CM-04"), ("bus", "citiz", "velo")):
        d, _, x = couverture_mobilite(cellules, paires, mode)
        r.ajouter(f"{numero}:{mode}", "couverture de mobilité", "couverture_mobilite", mode, t,
                  f"population à ≤ 5 min d'une option {mode}", "même formule, paires du mode seul", x, "part",
                  f"{d:,.0f} habitants".replace(",", " "))
    r.ajouter("CM-05", "couverture de mobilité", "couverture_mobilite", "toutes", t, "population sans option à ≤ 5 min",
              "Σ pop totale − Σ pop desservie (CM-01)", totale - desservie, "habitants")
    vol_cells = set(vol["cell_id"])
    r.ajouter("CM-06", "couverture de mobilité", "couverture_mobilite", "toutes", t, "comparaison : même mesure à vol d'oiseau",
              "Σ pop des carreaux ayant ≥ 1 paire vol d'oiseau / Σ pop", part(float(cellules.loc[cellules["cell_id"].isin(vol_cells), "pop"].sum()), totale),
              "part", "surestimation, non utilisée pour les KPI")

    tableau = r.table()
    description = ecrire_table(tableau, GOLD / "analytics" / f"qualite_donnees_{t}.parquet", ["indicateur_id"])
    mettre_a_jour_manifeste(GOLD / "analytics", f"qualite_donnees_{t}.parquet",
                            {"run_id": run_id, "date_reference": reference.isoformat(), "table": description,
                             "parametres": {"seuils": "config/qualite.yaml"}}, couche="gold")
    print(f"run_id : {run_id}   date de référence : {reference}")
    for _, l in tableau.iterrows():
        valeur = "" if pd.isna(l["valeur"]) else f"{l['valeur']:.4g}"
        print(f"  [{l['statut']:<6}] {l['indicateur_id']:<22} {l['libelle'][:52]:<52} {valeur:>10} {l['unite']}")
    print(f"  → {description['lignes']} indicateurs ; alertes : {int((tableau['statut'] == 'alerte').sum())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
