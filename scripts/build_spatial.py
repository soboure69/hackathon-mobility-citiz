"""Étape silver/spatial : carreaux et options rattachés au réseau piéton routable.

Entrées : tables Silver cleaned/ et deduplicated/ (empreintes notées dans le manifeste).
Usage, depuis la racine :  python scripts/build_spatial.py --territoire larochelle
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.cleaning.audit import Suivi  # noqa: E402
from src.evaluation.qualite import ligne  # noqa: E402
from src.geospatial import rattachement  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id  # noqa: E402

SILVER = RACINE / "data" / "silver"
CONFIG = RACINE / "config" / "silver.yaml"


def lire(relatif: str, entrees: dict) -> gpd.GeoDataFrame:
    chemin = SILVER / relatif
    if not chemin.exists():
        raise RuntimeError(f"Table Silver absente : {relatif}")
    entrees[relatif] = calculer_sha256(chemin)
    return gpd.read_parquet(chemin)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Étape silver/spatial.")
    parser.add_argument("--territoire", default="larochelle")
    args = parser.parse_args(argv)
    t = args.territoire
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    reglage = config["spatial"]
    run_id = construire_run_id()

    # Le tampon de l'emprise doit être celui de la requête OSM (S05).
    manifeste_cleaned = json.loads((SILVER / "cleaned" / "_manifest.json").read_text(encoding="utf-8"))
    tampon_s05 = manifeste_cleaned["tables"][f"osm_walk_edges_{t}.parquet"]["parametres"]["parametres_bronze"]["tampon_m"]
    if float(tampon_s05) != float(reglage["tampon_m"]):
        raise RuntimeError(f"Tampon {reglage['tampon_m']} m ≠ tampon de la requête S05 ({tampon_s05} m).")

    entrees: dict[str, str] = {}
    noeuds = lire(f"cleaned/osm_walk_nodes_{t}.parquet", entrees)
    aretes = lire(f"cleaned/osm_walk_edges_{t}.parquet", entrees)
    carreaux = lire("cleaned/filosofi_carreaux_5epci.parquet", entrees)
    epci = lire("cleaned/admin_epci_5epci.parquet", entrees)
    communes = lire("cleaned/admin_communes_5epci.parquet", entrees)
    communes_t = communes[communes["territoire"] == t]
    offres = [lire(f"deduplicated/offre_arrets_{t}.parquet", entrees),
              lire(f"deduplicated/offre_citiz_{t}.parquet", entrees),
              lire(f"deduplicated/offre_velo_{t}.parquet", entrees)]

    routables = rattachement.noeuds_routables(noeuds, aretes)
    emprise = epci.loc[epci["territoire"] == t].geometry.union_all().buffer(float(reglage["tampon_m"]))
    suivi = Suivi(run_id)
    dmax = float(reglage["distance_max_marche_m"])
    cellules = rattachement.construire_cellules(carreaux, t, routables, suivi, dmax, run_id)
    points = rattachement.construire_offre_points(offres, routables, emprise, suivi, dmax, run_id)
    cellules = rattachement.completer_admin_cellules(cellules, communes_t)
    points = rattachement.rattacher_admin_options(points, communes_t)
    if cellules["code_departement"].isna().any():
        raise RuntimeError("Carreau sans département : commune RF-01 absente des communes Admin Express.")

    journal = suivi.table()
    q = [
        ligne("spatial", "Q7", "nœuds routables (composante principale sans busway)", len(routables), "nœuds", run_id),
        ligne("spatial", "Q4", "carreaux rattachés", len(cellules), "carreaux", run_id),
        ligne("spatial", "Q4", "rattachement des carreaux, médiane", round(float(cellules["dist_snap_m"].median()), 1), "m", run_id),
        ligne("spatial", "Q4", "rattachement des carreaux, maximum", round(float(cellules["dist_snap_m"].max()), 1), "m", run_id),
        ligne("spatial", "J-02", "carreaux dont le centroïde est dans la commune attribuée (RF-01)",
              round(float(cellules["centroide_dans_commune"].mean()), 4), "part", run_id),
        ligne("spatial", "J-02", "carreaux dont le centroïde est hors de l'EPCI",
              int(cellules["commune_centroide"].isna().sum()), "carreaux", run_id),
        ligne("spatial", "J-01", "options rattachées à une commune de l'EPCI",
              round(float((~points["hors_epci"]).mean()), 4), "part", run_id),
        ligne("spatial", "RG-08", "population des carreaux à plus du budget du réseau",
              round(float(cellules.loc[cellules["dist_snap_m"] > dmax, "pop"].sum())), "habitants", run_id),
    ]
    for mode, groupe in points.groupby("mode"):
        q += [
            ligne("spatial", "Q4", f"{mode} : options rattachées", len(groupe), "options", run_id),
            ligne("spatial", "Q4", f"{mode} : rattachement, médiane", round(float(groupe["dist_snap_m"].median()), 1), "m", run_id),
            ligne("spatial", "Q4", f"{mode} : rattachement, maximum", round(float(groupe["dist_snap_m"].max()), 1), "m", run_id),
            ligne("spatial", "RG-05", f"{mode} : options hors emprise", int((~groupe["dans_emprise"]).sum()), "options", run_id),
        ]
    qualite = pd.DataFrame(q).astype("string")

    sorties = [
        ("spatial", f"cellules_{t}.parquet", cellules, ["cell_id"]),
        ("spatial", f"offre_points_{t}.parquet", points, ["offre_id"]),
        ("quality", "alertes_spatial.parquet", journal, ["regle_id", "id_origine", "etape"]),
        ("quality", "qualite_indicateurs_spatial.parquet", qualite, ["q_id", "libelle"]),
    ]
    print(f"run_id : {run_id}")
    for dossier, nom, table, cle in sorties:
        description = ecrire_table(table, SILVER / dossier / nom, cle)
        mettre_a_jour_manifeste(SILVER / dossier, nom, {
            "run_id": run_id, "entrees_silver": entrees, "table": description, "parametres": reglage})
        print(f"  {dossier}/{nom:<45} {description['lignes']:>6} lignes")
    print("Règles :", journal.groupby(["niveau", "regle_id"]).size().to_dict() or "aucune")
    for _, l in qualite.iterrows():
        print(f"  {l['q_id']:<6} {l['libelle']:<55} {l['valeur']} {l['unite']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
