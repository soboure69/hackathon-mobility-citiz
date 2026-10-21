"""Gold / exports : tables de restitution pour l'application Streamlit (compatibles Power BI).

Décisions P-1 à P-6 du 21/10/2026 (powerbi/conception_rapport.md), P-1 révisée : Streamlit.
Contrôles X-01 à X-07 bloquants. Usage, depuis la racine :
    python scripts/build_exports.py --territoire larochelle
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

from src.export import exports as ex  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id  # noqa: E402

DATA = RACINE / "data"
GOLD = DATA / "gold"
SORTIE = GOLD / "exports"
TOL = 1e-6
EMPRISE = {"lat": (45.9, 46.4), "lon": (-1.5, -0.7)}   # X-03, emprise large de l'EPCI

CLES = {
    "dim_mode": ["mode"], "dim_commune": ["commune_insee"], "dim_cellule": ["cell_id"], "dim_offre": ["offre_id"],
    "dim_candidat": ["candidat_id"], "dim_scenario": ["scenario_id"], "dim_source": ["source_id"],
    "fact_acces_mode": ["cell_id", "mode"], "fact_kpi_commune": ["commune_insee", "mode"], "fact_kpi_territoire": ["mode"],
    "fact_distribution": ["mode", "n_options"], "fact_equite_quintile": ["quintile", "mode"],
    "fact_contribution": ["candidat_id", "critere"], "fact_selection": ["scenario_id", "candidat_id"],
    "fact_carte_scenario": ["scenario_id", "point_id"], "fact_cellules_gagnees": ["scenario_id", "cell_id"],
    "fact_qualite": ["indicateur_id"], "fact_courbe": ["n_stations"], "fact_sensibilite": ["variable", "facteur"],
    "ref_hypotheses": ["hypothese_id"], "ref_risques": ["risque_id"], "meta_execution": ["dossier", "table"],
}
# X-02 : (table, colonne) → (dimension, clé)
LIENS = [
    ("dim_cellule", "commune_insee", "dim_commune"), ("fact_kpi_commune", "commune_insee", "dim_commune"),
    ("dim_candidat", "commune_insee", "dim_commune"), ("fact_acces_mode", "mode", "dim_mode"),
    ("fact_kpi_commune", "mode", "dim_mode"), ("fact_kpi_territoire", "mode", "dim_mode"), ("dim_offre", "mode", "dim_mode"),
    ("fact_distribution", "mode", "dim_mode"), ("fact_equite_quintile", "mode", "dim_mode"),
    ("fact_acces_mode", "cell_id", "dim_cellule"), ("fact_cellules_gagnees", "cell_id", "dim_cellule"),
    ("fact_contribution", "candidat_id", "dim_candidat"), ("fact_selection", "candidat_id", "dim_candidat"),
    ("fact_selection", "scenario_id", "dim_scenario"), ("fact_carte_scenario", "scenario_id", "dim_scenario"),
    ("fact_cellules_gagnees", "scenario_id", "dim_scenario"),
]


def controler(t: dict[str, pd.DataFrame]) -> None:
    for nom, table in t.items():                                                         # X-01
        assert not table.duplicated(subset=CLES[nom]).any(), f"X-01 {nom} : clé {CLES[nom]} non unique"
    for nom, col, dim in LIENS:                                                          # X-02
        cle = CLES[dim][0]
        orphelins = set(t[nom][col].dropna()) - set(t[dim][cle])
        assert not orphelins, f"X-02 {nom}.{col} : {len(orphelins)} valeur(s) absente(s) de {dim}, ex. {sorted(orphelins)[:3]}"
    for nom, table in t.items():                                                         # X-03, X-07
        if "lat" in table:
            for axe, (bas, haut) in EMPRISE.items():
                v = table[axe].dropna()
                assert v.between(bas, haut).all(), f"X-03 {nom}.{axe} hors emprise"
        assert "geometry" not in table.columns, f"X-07 {nom} : colonne geometry"
    tous = t["fact_acces_mode"].query("mode == 'tous'")["pop"].sum()                     # X-04
    ref = float(t["fact_kpi_territoire"].query("mode == 'tous'")["pop_totale"].iloc[0])
    assert abs(tous - ref) < TOL, f"X-04 population {tous} ≠ {ref}"
    gagnes = t["fact_cellules_gagnees"].groupby("scenario_id")["pop"].sum()             # X-05
    k6 = t["dim_scenario"].set_index("scenario_id")["k6"]
    ecart = (gagnes.reindex(k6.index).fillna(0) - k6).abs().max()
    assert ecart < TOL, f"X-05 Σ carreaux gagnés ≠ K6 (écart {ecart})"
    s = t["dim_scenario"]                                                                # X-06
    assert len(s) == 12 and (s["variante"] == "equite").sum() == 3 and s["est_reference"].sum() == 1, "X-06 scénarios"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exports de restitution.")
    parser.add_argument("--territoire", default="larochelle")
    t_nom = parser.parse_args(argv).territoire
    cfg = yaml.safe_load((RACINE / "config" / "app.yaml").read_text(encoding="utf-8"))
    score_cfg = yaml.safe_load((RACINE / "config" / "score.yaml").read_text(encoding="utf-8"))
    silver_cfg = yaml.safe_load((RACINE / "config" / "silver.yaml").read_text(encoding="utf-8"))
    epci = str(silver_cfg["territoires"][t_nom]["siren"])
    seuil = float(score_cfg["equite"]["seuil_commune_prioritaire"])
    type_eq = cfg["type_equipement"]
    run_id = construire_run_id()
    entrees: dict[str, str] = {}

    def lire(chemin: Path, geo: bool = False):
        entrees[str(chemin.relative_to(RACINE))] = calculer_sha256(chemin)
        return gpd.read_parquet(chemin) if geo else pd.read_parquet(chemin)

    g = lambda dossier, nom, geo=False: lire(GOLD / dossier / f"{nom}_{t_nom}.parquet", geo)  # noqa: E731
    acces = g("accessibility", "acces_cellule", True)
    kpi = g("accessibility", "kpi_couverture")
    offre = g("accessibility", "desserte_offre", True)
    candidats = g("candidates", "candidats", True)
    sensibilite = g("candidates", "sensibilite_ponderations")
    distribution = g("dashboards", "agg_distribution_acces")
    equite = g("dashboards", "agg_equite")
    qualite = g("analytics", "qualite_donnees")
    scenarios, kpi_sc = g("optimization", "scenarios"), g("optimization", "kpi_scenario")
    selection, cellules = g("optimization", "selection_scenario", True), g("optimization", "cellules_couvertes_scenario")
    courbe = g("optimization", "courbe_budget_impact")
    communes = lire(DATA / "silver" / "cleaned" / "admin_communes_5epci.parquet", geo=True)
    registre = pd.read_excel(RACINE / "docs" / "registre_des_sources.xlsx", sheet_name="sources")
    entrees["docs/registre_des_sources.xlsx"] = calculer_sha256(RACINE / "docs" / "registre_des_sources.xlsx")
    risques_md = (RACINE / "docs" / "suivi_risques.md").read_text(encoding="utf-8")
    entrees["docs/suivi_risques.md"] = calculer_sha256(RACINE / "docs" / "suivi_risques.md")
    manifestes = {d: json.loads((GOLD / d / "_manifest.json").read_text(encoding="utf-8"))
                  for d in ["accessibility", "analytics", "candidates", "dashboards", "optimization"]}

    t: dict[str, pd.DataFrame] = {}
    t["dim_mode"] = ex.dim_mode()
    t["dim_commune"] = ex.dim_commune(communes, kpi, acces, epci, seuil)
    prioritaires = set(t["dim_commune"].loc[t["dim_commune"]["prioritaire"], "commune_insee"])
    t["dim_cellule"] = ex.dim_cellule(acces, prioritaires)
    t["dim_offre"] = ex.dim_offre(offre)
    t["dim_candidat"] = ex.dim_candidat(candidats, type_eq)
    t["dim_scenario"] = ex.dim_scenario(scenarios, kpi_sc, cfg["scenario_reference"])
    t["dim_source"] = ex.dim_source(registre)
    t["fact_acces_mode"] = ex.fact_acces_mode(acces)
    t["fact_kpi_commune"] = ex.fact_kpi(kpi, "commune")
    t["fact_kpi_territoire"] = ex.fact_kpi(kpi, "epci")
    t["fact_distribution"] = ex.fact_distribution(distribution)
    t["fact_equite_quintile"] = ex.fact_equite_quintile(equite)
    t["fact_contribution"] = ex.fact_contribution(t["dim_candidat"], candidats, type_eq)
    t["fact_selection"] = ex.fact_selection(selection)
    t["fact_carte_scenario"] = ex.fact_carte_scenario(t["fact_selection"], t["dim_offre"], list(t["dim_scenario"]["scenario_id"]), type_eq)
    t["fact_cellules_gagnees"] = ex.fact_cellules_gagnees(cellules)
    t["fact_qualite"] = ex.fact_qualite(qualite)
    t["fact_courbe"] = ex.fact_courbe(courbe)
    t["fact_sensibilite"] = ex.fact_sensibilite(sensibilite, type_eq)
    t["ref_hypotheses"] = ex.ref_hypotheses(cfg["hypotheses"])
    t["ref_risques"] = ex.ref_risques(risques_md)
    t["meta_execution"] = ex.meta_execution(manifestes)
    controler(t)

    print(f"run_id : {run_id}   contrôles X-01 à X-07 : ok")
    for nom, table in t.items():
        table = table.copy()
        table["run_id"] = run_id
        fichier = f"{nom}_{t_nom}.parquet"
        description = ecrire_table(table, SORTIE / fichier, CLES[nom])
        mettre_a_jour_manifeste(SORTIE, fichier, {"run_id": run_id, "entrees": entrees, "table": description}, couche="gold")
        print(f"  exports/{fichier:<42}{description['lignes']:>6} lignes")
    for nom, gdf in {"communes": ex.geojson_communes(communes, t["dim_commune"]), "carreaux": ex.geojson_carreaux(acces)}.items():
        fichier = SORTIE / f"{nom}_{t_nom}.geojson"
        fichier.write_text(gdf.to_json(drop_id=True, to_wgs84=False), encoding="utf-8")
        mettre_a_jour_manifeste(SORTIE, fichier.name, {"run_id": run_id, "entrees": entrees,
                                                       "table": {"nom": fichier.name, "lignes": len(gdf), "crs": "EPSG:4326",
                                                                 "sha256": calculer_sha256(fichier)}}, couche="gold")
        print(f"  exports/{fichier.name:<42}{len(gdf):>6} entités")
    m = t["meta_execution"]
    if m["modifie"].any():
        print(f"ATTENTION : {int(m['modifie'].sum())} table(s) Gold produite(s) par du code non commité (-modifie).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
