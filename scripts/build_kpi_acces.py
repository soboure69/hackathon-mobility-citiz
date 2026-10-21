"""Gold / KPI d'accessibilité et de couverture (carreau, option, commune, EPCI, équité).

Entrées : silver/spatial (carreaux, options), gold/accessibility/paires (réseau, référence).
Les invariants K-T1 à K-T8 arrêtent le script s'ils sont violés.
Usage, depuis la racine :  python scripts/build_kpi_acces.py --territoire larochelle
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.features import kpi_acces as k  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id  # noqa: E402

SILVER, GOLD = RACINE / "data" / "silver", RACINE / "data" / "gold"
TOLERANCE = 1e-6


def verifier(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise RuntimeError(f"{code} : {message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KPI Gold d'accessibilité.")
    parser.add_argument("--territoire", default="larochelle")
    t = parser.parse_args(argv).territoire
    run_id = construire_run_id()
    entrees = {}

    def lire(chemin: Path, geo: bool = True):
        entrees[str(chemin.relative_to(RACINE / "data"))] = calculer_sha256(chemin)
        return gpd.read_parquet(chemin) if geo else pd.read_parquet(chemin)

    cellules = lire(SILVER / "spatial" / f"cellules_{t}.parquet")
    offres = lire(SILVER / "spatial" / f"offre_points_{t}.parquet")
    paires = lire(GOLD / "accessibility" / f"paires_cellule_offre_{t}.parquet", geo=False)
    qualite = lire(GOLD / "analytics" / f"qualite_donnees_{t}.parquet", geo=False)

    acces = k.acces_cellule(cellules, paires)
    centroides = gpd.GeoSeries(gpd.points_from_xy(acces["x_centroide"], acces["y_centroide"]), crs=2154).to_crs(4326)
    acces["lon_centroide_wgs84"], acces["lat_centroide_wgs84"] = centroides.x.values, centroides.y.values
    acces["run_id"] = run_id
    acces = gpd.GeoDataFrame(acces, geometry="geometry", crs=cellules.crs)
    desserte = gpd.GeoDataFrame(k.desserte_offre(offres, cellules, paires), geometry="geometry", crs=offres.crs)
    desserte["run_id"] = run_id
    couverture = k.couverture(acces, {"epci": "epci_siren", "commune": "commune_insee"})
    couverture["run_id"] = run_id
    distribution, equite = k.distribution(acces), k.equite(acces)
    distribution["run_id"], equite["run_id"] = run_id, run_id

    # ---------- Invariants ----------
    verifier((couverture["pop_desservie"] <= couverture["pop_totale"] + TOLERANCE).all(), "K-T1", "population desservie > totale")
    epci = couverture[couverture["perimetre_type"] == "epci"].set_index("mode")
    communes = couverture[couverture["perimetre_type"] == "commune"].groupby("mode")[["pop_totale", "pop_desservie"]].sum()
    verifier(((communes - epci[["pop_totale", "pop_desservie"]]).abs() < TOLERANCE).all().all(), "K-T2",
             "la somme des communes ne redonne pas l'EPCI")
    for mode in k.MODES:
        exclusif = float(desserte.loc[desserte["mode"] == mode, "pop_exclusive"].sum())
        verifier(abs(exclusif - float(epci.loc[mode, "pop_desservie"])) < TOLERANCE, "K-T3",
                 f"{mode} : Σ population exclusive ≠ population couverte")
    verifier((acces["n_options_total"] == sum(acces[f"n_options_{m}"] for m in k.MODES)).all(), "K-T4",
             "options totales ≠ somme des options par mode")
    verifier((acces["n_modes"] == sum(acces[f"desservi_{m}"].astype(int) for m in k.MODES)).all(), "K-T5",
             "n_modes ≠ nombre de modes desservis")
    cm01 = float(qualite.set_index("indicateur_id").loc["CM-01", "valeur"])
    verifier(abs(float(epci.loc["tous", "taux_couverture"]) - cm01) < TOLERANCE, "K-T6",
             "taux de couverture ≠ CM-01 du tableau qualité")
    verifier((acces["dist_min_m"].dropna() <= 400 + TOLERANCE).all(), "K-T7", "distance minimale > 400 m")
    sans = ~acces["cell_id"].isin(set(paires["cell_id"][(paires["methode"] == "reseau") & (paires["variante"] == "reference")]))
    verifier((acces.loc[sans, "n_options_total"] == 0).all() and not acces.loc[sans, "desservi"].any(), "K-T8",
             "un carreau sans paire est déclaré desservi")

    sorties = [
        ("accessibility", f"acces_cellule_{t}.parquet", acces, ["cell_id"]),
        ("accessibility", f"desserte_offre_{t}.parquet", desserte, ["offre_id"]),
        ("accessibility", f"kpi_couverture_{t}.parquet", couverture, ["perimetre_type", "perimetre_id", "mode"]),
        ("dashboards", f"agg_distribution_acces_{t}.parquet", distribution, ["mode", "n_options"]),
        ("dashboards", f"agg_equite_{t}.parquet", equite, ["quintile_niveau_vie", "mode"]),
    ]
    print(f"run_id : {run_id}   invariants K-T1 à K-T8 : ok")
    for dossier, nom, table, cle in sorties:
        description = ecrire_table(table, GOLD / dossier / nom, cle)
        mettre_a_jour_manifeste(GOLD / dossier, nom, {"run_id": run_id, "entrees": entrees, "table": description,
                                                      "parametres": {"paires": "reseau / reference", "budget_m": 400}},
                                couche="gold")
        print(f"  {dossier}/{nom:<42} {description['lignes']:>6} lignes")

    print("\nEPCI :")
    for mode, l in epci.iterrows():
        print(f"  {mode:<6} desservie {l['pop_desservie']:>9,.0f} / {l['pop_totale']:,.0f}  taux {l['taux_couverture']:.3f}"
              f"  non desservie {l['pop_non_desservie']:>8,.0f}  options/hab {l['options_moyennes_par_habitant']:.2f}".replace(",", " "))
    print(f"  au moins 2 modes : {epci.loc['tous', 'pop_au_moins_2_modes']:,.0f} habitants".replace(",", " "))
    tous = couverture[(couverture["perimetre_type"] == "commune") & (couverture["mode"] == "tous")].sort_values("taux_couverture")
    print("\nCommunes, taux tous modes (les 5 plus faibles et les 3 plus forts) :")
    for _, l in pd.concat([tous.head(5), tous.tail(3)]).iterrows():
        print(f"  {l['perimetre_id']}  {l['taux_couverture']:.3f}  pop {l['pop_totale']:>8,.0f}".replace(",", " "))
    print("\nÉquité (tous modes) :")
    for _, l in equite[equite["mode"] == "tous"].iterrows():
        print(f"  quintile {l['quintile_niveau_vie']:<14} pop {l['pop']:>8,.0f}  taux {l['taux_couverture']:.3f}".replace(",", " "))
    citiz = equite[equite["mode"] == "citiz"][["quintile_niveau_vie", "taux_couverture"]].values.tolist()
    print("  Citiz :", [(q, round(float(v), 3)) for q, v in citiz])
    return 0


if __name__ == "__main__":
    sys.exit(main())
