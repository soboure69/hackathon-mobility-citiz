"""Gold / accessibilité : table des paires carreau × option à moins du budget de marche.

Trois jeux de paires : réseau (référence), réseau sans arêtes trunk (sensibilité RC-01),
vol d'oiseau (repli MVP). Aucun KPI final ici.
Usage, depuis la racine :  python scripts/build_paires.py --territoire larochelle
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.evaluation.qualite import ligne  # noqa: E402
from src.geospatial import accessibilite  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id  # noqa: E402

SILVER = RACINE / "data" / "silver"
GOLD = RACINE / "data" / "gold"
CONFIG = RACINE / "config" / "silver.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paires carreau × option.")
    parser.add_argument("--territoire", default="larochelle")
    t = parser.parse_args(argv).territoire
    budget = float(yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["spatial"]["distance_max_marche_m"])
    run_id = construire_run_id()

    entrees = {}
    def lire(relatif):
        chemin = SILVER / relatif
        entrees[relatif] = calculer_sha256(chemin)
        return gpd.read_parquet(chemin)
    cellules = lire(f"spatial/cellules_{t}.parquet")
    offres = lire(f"spatial/offre_points_{t}.parquet")
    aretes = lire(f"cleaned/osm_walk_edges_{t}.parquet")

    reference = accessibilite.paires_reseau(cellules, offres, accessibilite.graphe_routable(aretes), budget, "reference")
    sans_trunk = accessibilite.paires_reseau(cellules, offres, accessibilite.graphe_routable(aretes, sans_trunk=True),
                                             budget, "sans_trunk")
    vol = accessibilite.paires_vol_oiseau(cellules, offres, budget)
    paires = pd.concat([reference, sans_trunk, vol], ignore_index=True)
    for colonne in ("dist_acces_cellule_m", "dist_reseau_m", "dist_acces_option_m", "dist_totale_m"):
        paires[colonne] = pd.to_numeric(paires[colonne]).astype("Float64")
    paires["run_id"] = run_id

    # Contrôles de cohérence (J-03 à J-06)
    if (paires["dist_totale_m"] > budget + 1e-6).any():
        raise RuntimeError("J-03 : une paire dépasse le budget de marche.")
    inconnus = set(paires["cell_id"]) - set(cellules["cell_id"]) | set(paires["offre_id"]) - set(offres["offre_id"])
    if inconnus:
        raise RuntimeError(f"J-04 : identifiants inconnus dans les paires : {sorted(inconnus)[:5]}")
    commun = reference.merge(vol, on=["cell_id", "offre_id"], suffixes=("_r", "_v"))
    detour = (commun["dist_totale_m_r"] / commun["dist_totale_m_v"].where(commun["dist_totale_m_v"] > 0)).dropna()
    paires_ref = set(zip(reference["cell_id"], reference["offre_id"]))
    perdues = paires_ref - set(zip(sans_trunk["cell_id"], sans_trunk["offre_id"]))
    carreaux_ref = set(reference["cell_id"])
    carreaux_perdus = carreaux_ref - set(sans_trunk["cell_id"])

    q = []
    for (methode, variante), groupe in paires.groupby(["methode", "variante"]):
        nom = f"{methode}/{variante}"
        q += [ligne("paires", "J-05", f"{nom} : paires", len(groupe), "paires", run_id),
              ligne("paires", "J-05", f"{nom} : carreaux atteignant au moins une option", groupe["cell_id"].nunique(), "carreaux", run_id),
              ligne("paires", "J-05", f"{nom} : options atteintes par au moins un carreau", groupe["offre_id"].nunique(), "options", run_id)]
    q += [
        ligne("paires", "J-06", "paires réseau aussi trouvées à vol d'oiseau", round(len(commun) / len(reference), 4), "part", run_id),
        ligne("paires", "J-06", "détour réseau / vol d'oiseau, médiane", round(float(detour.median()), 3), "rapport", run_id),
        ligne("paires", "RC-01", "sensibilité : paires perdues sans les arêtes trunk", len(perdues), "paires", run_id),
        ligne("paires", "RC-01", "sensibilité : part des paires perdues", round(len(perdues) / len(paires_ref), 5), "part", run_id),
        ligne("paires", "RC-01", "sensibilité : carreaux qui perdent toute option", len(carreaux_perdus), "carreaux", run_id),
    ]
    qualite = pd.DataFrame(q).astype("string")

    print(f"run_id : {run_id}")
    for dossier, nom, table, cle in [
        ("accessibility", f"paires_cellule_offre_{t}.parquet", paires, ["cell_id", "offre_id", "methode", "variante"]),
        ("analytics", "qualite_indicateurs_paires.parquet", qualite, ["q_id", "libelle"]),
    ]:
        description = ecrire_table(table, GOLD / dossier / nom, cle)
        mettre_a_jour_manifeste(GOLD / dossier, nom, {"run_id": run_id, "entrees_silver": entrees,
                                                      "table": description, "parametres": {"budget_m": budget}},
                                couche="gold")
        print(f"  {dossier}/{nom:<45} {description['lignes']:>7} lignes")
    for _, l in qualite.iterrows():
        print(f"  {l['q_id']:<6} {l['libelle']:<60} {l['valeur']} {l['unite']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
