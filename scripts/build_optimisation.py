"""Gold / optimisation (Citiz) : 3 scénarios × 3 hypothèses de coût, variante équité, courbe budget → impact.

Décisions D-1 à D-5 et variante C-5 du 21/10/2026 (docs/optimisation.md). Contrôles O-T1 à O-T8 bloquants.
Usage, depuis la racine :  python scripts/build_optimisation.py --territoire larochelle
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

from src.optimization import couverture as opt  # noqa: E402
from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste  # noqa: E402
from src.utils.manifest import calculer_sha256, construire_run_id  # noqa: E402

DATA = RACINE / "data"
GOLD = DATA / "gold"
TOL = 1e-6


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optimisation budgétaire (MVP).")
    parser.add_argument("--territoire", default="larochelle")
    t = parser.parse_args(argv).territoire
    cfg = yaml.safe_load((RACINE / "config" / "optimisation.yaml").read_text(encoding="utf-8"))
    seuil_prioritaire = yaml.safe_load((RACINE / "config" / "score.yaml").read_text(encoding="utf-8"))["equite"]["seuil_commune_prioritaire"]
    type_eq = cfg["type_equipement"]
    run_id = construire_run_id()
    entrees = {}

    def lire(chemin: Path, geo: bool = False):
        entrees[str(chemin.relative_to(DATA))] = calculer_sha256(chemin)
        return gpd.read_parquet(chemin) if geo else pd.read_parquet(chemin)

    candidats = lire(GOLD / "candidates" / f"candidats_{t}.parquet", geo=True)
    paires = lire(GOLD / "candidates" / f"paires_candidat_cellule_{t}.parquet")
    acces = lire(GOLD / "accessibility" / f"acces_cellule_{t}.parquet", geo=True)
    couverture = lire(GOLD / "accessibility" / f"kpi_couverture_{t}.parquet")
    communes = couverture[(couverture["perimetre_type"] == "commune") & (couverture["mode"] == "tous")]
    prioritaires = set(communes.loc[communes["taux_couverture"].astype(float) < seuil_prioritaire, "perimetre_id"])
    pop_totale = float(acces["pop"].sum())
    pop_type_avant = float(acces.loc[acces[f"desservi_{type_eq}"].astype(bool), "pop"].sum())
    pop_tous_avant = float(acces.loc[acces["desservi"].astype(bool), "pop"].sum())
    sans_option = set(acces.loc[~acces["desservi"].astype(bool), "cell_id"])
    infos = candidats[candidats["type_equipement"] == type_eq].set_index("candidat_id")

    scenarios, selections, kpis, cellules = [], [], [], []
    gap = cfg["solveur"]["ecart_relatif"]

    def traiter(sid: str, nom: str, budget: float, hypothese: str, cout: dict, part_min: float | None) -> dict:
        d = opt.preparer(candidats, paires, acces, type_eq, cout["montant"], prioritaires)
        r = opt.resoudre(d, budget, cfg["n_max"], cfg["solveur"]["temps_max_s"], gap, part_min)
        ordre = opt.ordre_ajout(d, r["choisis"], float("inf"))
        k7 = float(cout["montant"]) * len(r["choisis"])
        atteints = set().union(*(d.couverture.get(i, set()) for i in r["choisis"])) if r["choisis"] else set()
        nouveaux = d.carreaux[d.carreaux["cell_id"].isin(atteints)]
        # Le glouton ignore la contrainte d'équité : il ne sert de contrôle (O-T5) qu'en variante efficacité.
        if part_min is None:
            glouton = opt.ordre_ajout(d, list(d.sites["candidat_id"]), budget)
            k6_glouton = float(glouton["pop_nouvelle_cumulee"].iloc[-1]) if len(glouton) else 0.0
        else:
            k6_glouton = None

        # Contrôles O-T1 à O-T7
        assert r["optimum_prouve"], f"O-T6 {sid} : solution non prouvée ({r['statut_solution']})"
        assert k7 <= budget + TOL, f"O-T1 {sid} : budget dépassé"
        assert abs(float(ordre["pop_nouvelle_marginale"].sum()) - r["k6"]) < TOL, f"O-T2 {sid} : Σ marginaux ≠ K6"
        assert r["k6"] <= float(d.carreaux["pop"].sum()) + TOL, f"O-T3 {sid}"
        assert not nouveaux["cell_id"].duplicated().any(), f"O-T4 {sid}"
        if k6_glouton is not None:
            assert r["k6"] >= k6_glouton - TOL, f"O-T5 {sid} : optimum < glouton"
        else:
            assert r["k6_prioritaire"] >= part_min * r["k6"] - TOL, f"O-T7 {sid} : part prioritaire réelle < {part_min:.0%}"

        variante = "efficacite" if part_min is None else "equite"
        scenarios.append({"scenario_id": sid, "scenario": nom, "variante": variante, "hypothese_cout": hypothese,
                          "budget": float(budget), "cout_station": float(cout["montant"]), "cout_etiquette": cout["etiquette"],
                          "type_equipement": type_eq, "objectif": cfg["objectif"],
                          "contraintes": "couverture, budget" + ("" if part_min is None else f", équité ≥ {part_min:.0%}"),
                          "part_prioritaire_min": part_min, "seuil_commune_prioritaire": seuil_prioritaire,
                          "solveur": "PuLP / CBC", "statut": r["statut"], "statut_solution": r["statut_solution"],
                          "ecart_relatif_garanti": r["ecart_relatif_garanti"], "valeur_k6": r["k6"],
                          "k6_glouton": k6_glouton, "epsilon": r["epsilon"], "duree_s": round(r["duree_s"], 3)})
        gain_tous = float(nouveaux.loc[nouveaux["cell_id"].isin(sans_option), "pop"].sum())
        ligne = {"scenario_id": sid, "variante": variante, "n_stations": len(r["choisis"]), "k6_pop_nouvellement_couverte": r["k6"],
                 "k7_cout_total": k7, "k8_cout_par_habitant": k7 / r["k6"] if r["k6"] else None,
                 "cout_etiquette": cout["etiquette"],
                 f"couverture_{type_eq}_avant": pop_type_avant / pop_totale,
                 f"couverture_{type_eq}_apres": (pop_type_avant + r["k6"]) / pop_totale,
                 "couverture_tous_modes_avant": pop_tous_avant / pop_totale,
                 "couverture_tous_modes_apres": (pop_tous_avant + gain_tous) / pop_totale,
                 "pop_sans_option_gagnee": gain_tous,
                 "pop_gagnee_communes_prioritaires": r["k6_prioritaire"],
                 "k12_part_gains_communes_prioritaires": r["k6_prioritaire"] / r["k6"] if r["k6"] else None,
                 "scenario_reference": None, "k6_reference": None, "prix_equite_habitants": None, "prix_equite_part": None}
        kpis.append(ligne)
        sel = ordre.assign(scenario_id=sid, cout_etiquette=cout["etiquette"])
        sel = sel.join(infos[["commune_insee", "score", "rang", "commune_prioritaire", "lon_wgs84", "lat_wgs84", "geometry"]],
                       on="candidat_id")
        selections.append(sel)
        cellules.append(nouveaux.assign(scenario_id=sid, gain_tous_modes=nouveaux["cell_id"].isin(sans_option))
                        [["scenario_id", "cell_id", "pop", "commune_insee", "prioritaire", "gain_tous_modes"]])
        return ligne

    for nom, budget in cfg["scenarios"].items():
        for hypothese, cout in cfg["couts"].items():
            traiter(f"SC_{nom}_{hypothese}", nom, budget, hypothese, cout, None)

    # Variante équité (C-5) : même budget, même coût, contrainte de part prioritaire. Prix = K6 perdu.
    eq = cfg.get("equite")
    if eq:
        k6_par_id = {l["scenario_id"]: l["k6_pop_nouvellement_couverte"] for l in kpis}
        for nom, budget in cfg["scenarios"].items():
            ref = f"SC_{nom}_{eq['cout']}"
            ligne = traiter(f"{ref}_equite", nom, budget, eq["cout"], cfg["couts"][eq["cout"]], float(eq["part_min"]))
            k6_ref = k6_par_id[ref]
            # O-T8 : ajouter une contrainte ne peut pas faire mieux (à l'écart garanti près des deux optimums).
            assert ligne["k6_pop_nouvellement_couverte"] <= k6_ref * (1 + gap) + TOL, f"O-T8 {ref}_equite : K6 > référence"
            prix = k6_ref - ligne["k6_pop_nouvellement_couverte"]
            ligne.update({"scenario_reference": ref, "k6_reference": k6_ref,
                          "prix_equite_habitants": prix, "prix_equite_part": prix / k6_ref if k6_ref else None})

    central = float(cfg["couts"]["central"]["montant"])
    d = opt.preparer(candidats, paires, acces, type_eq, central, prioritaires)
    courbe = []
    for n in range(1, cfg["courbe"]["stations_max"] + 1):
        r = opt.resoudre(d, n * central, None, cfg["solveur"]["temps_max_s"], cfg["solveur"]["ecart_relatif"])
        assert r["optimum_prouve"], f"O-T6 courbe {n} stations : solution non prouvée"
        courbe.append({"budget": n * central, "n_stations": len(r["choisis"]), "k6": r["k6"],
                       "k8_cout_par_habitant": n * central / r["k6"] if r["k6"] else None})
    courbe = pd.DataFrame(courbe)
    courbe["gain_marginal"] = courbe["k6"].diff().fillna(courbe["k6"])

    tables = {
        "scenarios": (pd.DataFrame(scenarios), ["scenario_id"]),
        "selection_scenario": (gpd.GeoDataFrame(pd.concat(selections, ignore_index=True), geometry="geometry", crs=candidats.crs),
                               ["scenario_id", "candidat_id"]),
        "kpi_scenario": (pd.DataFrame(kpis), ["scenario_id"]),
        "courbe_budget_impact": (courbe, ["budget"]),
        "cellules_couvertes_scenario": (pd.concat(cellules, ignore_index=True), ["scenario_id", "cell_id"]),
    }
    print(f"run_id : {run_id}   contrôles O-T1 à O-T8 : ok")
    for nom, (table, cle) in tables.items():
        table = table.copy()
        table["run_id"] = run_id
        description = ecrire_table(table, GOLD / "optimization" / f"{nom}_{t}.parquet", cle)
        mettre_a_jour_manifeste(GOLD / "optimization", f"{nom}_{t}.parquet",
                                {"run_id": run_id, "entrees": entrees, "table": description, "parametres": cfg}, couche="gold")
        print(f"  optimization/{nom}_{t}.parquet{'':<6}{description['lignes']:>5} lignes")

    k = pd.DataFrame(kpis).set_index("scenario_id")
    print("\nScénario                      stations      K6     K7 (€)   K8 (€/hab)  Citiz avant→après   tous modes avant→après  part prioritaires")
    for sid, l in k.iterrows():
        print(f"  {sid:<30}{l['n_stations']:>4}  {l['k6_pop_nouvellement_couverte']:>8,.0f}  {l['k7_cout_total']:>9,.0f}  {l['k8_cout_par_habitant']:>9,.2f}"
              f"   {l[f'couverture_{type_eq}_avant']:.3f}→{l[f'couverture_{type_eq}_apres']:.3f}"
              f"        {l['couverture_tous_modes_avant']:.3f}→{l['couverture_tous_modes_apres']:.3f}"
              f"          {l['k12_part_gains_communes_prioritaires']:.3f}".replace(",", " "))
    print("\nCourbe (coût central) : gain marginal de la 1re, 5e, 10e, 20e, 30e station :",
          [round(float(courbe.loc[courbe['n_stations'] == n, 'gain_marginal'].iloc[0])) for n in (1, 5, 10, 20, 30)])
    efficacite = [s for s in scenarios if s["variante"] == "efficacite"]
    egal = sum(1 for s in efficacite if abs(s["valeur_k6"] - s["k6_glouton"]) < TOL)
    print(f"Glouton = optimum dans {egal} scénarios sur {len(efficacite)} ; ailleurs, l'optimum fait mieux.")
    prix = k[k["variante"] == "equite"]
    if len(prix):
        print(f"\nPrix de l'équité (≥ {float(cfg['equite']['part_min']):.0%} des gains en communes prioritaires, coût {cfg['equite']['cout']}) :")
        for sid, l in prix.iterrows():
            print(f"  {sid:<30} K6 {l['k6_pop_nouvellement_couverte']:>8,.0f} contre {l['k6_reference']:>8,.0f}"
                  f"  → {l['prix_equite_habitants']:>6,.0f} habitants ({l['prix_equite_part']:.1%})"
                  f"   gains prioritaires {l['pop_gagnee_communes_prioritaires']:>6,.0f}"
                  f"   K8 {l['k8_cout_par_habitant']:.2f} €".replace(",", " "))
        print(f"  (écart garanti {gap:.1%} sur chaque optimum : prix connu à ± {gap:.1%} de K6 près)")
    print(f"Durée solveur max : {max(s['duree_s'] for s in scenarios):.2f} s ; écart garanti : {cfg['solveur']['ecart_relatif']:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
