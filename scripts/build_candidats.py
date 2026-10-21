"""Gold / candidats : sites candidats, exclusions, score multicritère (K10), sensibilité, équité.

Pas d'optimisation budgétaire ici. Le score n'est pas une prédiction de fréquentation.
Usage, depuis la racine :  python scripts/build_candidats.py --territoire larochelle
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

from src.geospatial.accessibilite import graphe_routable  # noqa: E402
from src.geospatial.rattachement import noeuds_routables  # noqa: E402
from src.scoring import candidats as cand  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id  # noqa: E402

DATA = RACINE / "data"
SILVER, GOLD = DATA / "silver", DATA / "gold"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Candidats et score de potentiel.")
    parser.add_argument("--territoire", default="larochelle")
    t = parser.parse_args(argv).territoire
    reglage = yaml.safe_load((RACINE / "config" / "score.yaml").read_text(encoding="utf-8"))
    budget = float(yaml.safe_load((RACINE / "config" / "silver.yaml").read_text(encoding="utf-8"))["spatial"]["distance_max_marche_m"])
    poids = reglage["ponderations"]
    run_id = construire_run_id()
    entrees = {}

    def lire(chemin: Path):
        entrees[str(chemin.relative_to(DATA))] = calculer_sha256(chemin)
        return gpd.read_parquet(chemin)

    cellules = lire(SILVER / "spatial" / f"cellules_{t}.parquet")
    noeuds = lire(SILVER / "cleaned" / f"osm_walk_nodes_{t}.parquet")
    aretes = lire(SILVER / "cleaned" / f"osm_walk_edges_{t}.parquet")
    acces = lire(GOLD / "accessibility" / f"acces_cellule_{t}.parquet")
    couverture = pd.read_parquet(GOLD / "accessibility" / f"kpi_couverture_{t}.parquet")
    epci = lire(SILVER / "cleaned" / "admin_epci_5epci.parquet")
    communes = lire(SILVER / "cleaned" / "admin_communes_5epci.parquet")
    contour = epci.loc[epci["territoire"] == t].geometry.union_all()

    sites = cand.generer_sites(cellules, noeuds_routables(noeuds, aretes))
    paires = cand.paires_sites(sites, cellules, graphe_routable(aretes), budget)
    sites["dans_epci"] = sites.geometry.within(contour)
    sites["acces_voiture"] = cand.acces_voiture(sites, aretes, reglage["exclusion"]["voies_voiture"])
    taux_commune = couverture[(couverture["perimetre_type"] == "commune") & (couverture["mode"] == "tous")] \
        .set_index("perimetre_id")["taux_couverture"].astype(float)
    prioritaires = set(taux_commune[taux_commune < reglage["equite"]["seuil_commune_prioritaire"]].index)

    morceaux, sensibilites = [], []
    for mode in reglage["types_equipement"]:
        table = cand.variables(sites, paires, acces, mode)
        table["type_equipement"] = mode
        motif = pd.Series(pd.NA, index=table.index, dtype="string")
        motif[~table["dans_epci"]] = "hors EPCI"
        if mode in reglage["exclusion"]["acces_voiture_requis"]:
            motif[motif.isna() & ~table["acces_voiture"]] = "pas d'accès voiture"
        motif[motif.isna() & (table["pop_nouvelle"].fillna(0) <= 0)] = "aucun habitant nouvellement couvert"
        motif[motif.isna() & (table["taux_redondance"] > reglage["exclusion"]["redondance_max"])] = "redondance excessive"
        table["motif_exclusion"] = motif
        table["retenu"] = motif.isna()

        retenus = cand.noter(table[table["retenu"]], poids)
        retenus["rang"] = cand.classer(retenus)
        retenus["rang_commune"] = retenus.groupby("commune_insee")["score"].rank(ascending=False, method="first").astype("Int64")
        s = reglage["sensibilite"]
        frequence, un_facteur = cand.sensibilite(retenus, poids, s["tirages"], s["concentration"], s["graine"], s["top_n"])
        retenus["frequence_top_n"] = frequence
        retenus["commune_prioritaire"] = retenus["commune_insee"].isin(prioritaires)
        e = reglage["equite"]
        retenus["rang_equite"] = cand.selection_equite(retenus, prioritaires, e["top_n"], e["quota_communes_prioritaires"])
        un_facteur.insert(0, "type_equipement", mode)
        sensibilites.append(un_facteur)
        table = table.join(retenus[[c for c in retenus.columns if c not in table.columns]])
        morceaux.append(table)

    candidats = gpd.GeoDataFrame(pd.concat(morceaux, ignore_index=True), geometry="geometry", crs=noeuds.crs)
    candidats["commune_prioritaire"] = candidats["commune_insee"].isin(prioritaires)
    wgs = candidats.geometry.to_crs(4326)
    candidats["lon_wgs84"], candidats["lat_wgs84"] = wgs.x.values, wgs.y.values
    candidats["run_id"] = run_id
    for colonne in ("rang", "rang_commune", "rang_equite", "n_carreaux_zone"):
        candidats[colonne] = candidats[colonne].astype("Int64")
    sensibilite = pd.concat(sensibilites, ignore_index=True)
    paires["run_id"] = run_id

    # ---------- Invariants ----------
    retenus = candidats[candidats["retenu"]]
    contributions = retenus[[f"contribution_{v}" for v in cand.VARIABLES]].sum(axis=1)
    assert ((retenus["score"] >= 0) & (retenus["score"] <= 100)).all(), "S-T1 : score hors [0, 100]"
    assert (abs(contributions - retenus["score"]) < 1e-9).all(), "S-T2 : Σ contributions ≠ score"
    assert (retenus["pop_nouvelle"] > 0).all() and retenus["dans_epci"].all(), "S-T3 : candidat retenu invalide"
    assert (candidats["pop_nouvelle"].fillna(0) <= candidats["pop_rayon"].fillna(0) + 1e-6).all(), "S-T4 : K6 > population atteinte"
    for mode, groupe in retenus.groupby("type_equipement"):
        assert sorted(groupe["rang"]) == list(range(1, len(groupe) + 1)), f"S-T5 : rangs {mode} non continus"

    print(f"run_id : {run_id}   sites : {len(sites)}   paires site × carreau : {len(paires)}")
    for dossier, nom, table, cle in [
        ("candidates", f"candidats_{t}.parquet", candidats, ["candidat_id", "type_equipement"]),
        ("candidates", f"paires_candidat_cellule_{t}.parquet", paires, ["candidat_id", "cell_id"]),
        ("candidates", f"sensibilite_ponderations_{t}.parquet", sensibilite, ["type_equipement", "variable", "facteur"]),
    ]:
        description = ecrire_table(table, GOLD / dossier / nom, cle)
        mettre_a_jour_manifeste(GOLD / dossier, nom, {"run_id": run_id, "entrees": entrees, "table": description,
                                                      "parametres": reglage}, couche="gold")
        print(f"  {dossier}/{nom:<44} {description['lignes']:>7} lignes")

    noms = dict(zip(communes["code_insee"], communes["nom_officiel"]))
    for mode in reglage["types_equipement"]:
        groupe = candidats[candidats["type_equipement"] == mode]
        print(f"\n{mode} : {int(groupe['retenu'].sum())} retenus / {len(groupe)} ; exclusions :",
              groupe["motif_exclusion"].value_counts().to_dict())
    print("\nTop 10 Citiz (score, nouvelle population, commune, fréquence dans le top 20 sous pondérations tirées) :")
    top = retenus[retenus["type_equipement"] == "citiz"].sort_values("rang").head(10)
    for _, l in top.iterrows():
        print(f"  {int(l['rang']):>2}. {l['candidat_id']:<34} score {l['score']:5.1f}  +{l['pop_nouvelle']:>6.0f} hab  "
              f"{noms.get(l['commune_insee'], l['commune_insee'])[:22]:<22} robustesse {l['frequence_top_n']:.2f}")
    print("\nSensibilité (Citiz, un facteur à la fois) : Spearman min",
          round(float(sensibilite.loc[sensibilite['type_equipement'] == 'citiz', 'spearman'].min()), 3),
          "; recouvrement du top 20 min",
          round(float(sensibilite.loc[sensibilite['type_equipement'] == 'citiz', 'recouvrement_top_n'].min()), 2))
    eq = retenus[(retenus["type_equipement"] == "citiz") & retenus["rang_equite"].notna()]
    print(f"Top 20 Citiz avec garde-fou d'équité : {int(eq['commune_prioritaire'].sum())} sites en commune prioritaire "
          f"(contre {int(top.head(20)['commune_prioritaire'].sum()) if len(top) else 0} dans le top 10 brut ; "
          f"{int(retenus[(retenus['type_equipement'] == 'citiz') & (retenus['rang'] <= 20)]['commune_prioritaire'].sum())} dans le top 20 brut)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
