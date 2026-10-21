"""KPI Gold d'accessibilité et de couverture, au carreau de 200 m.

Entrée unique des distances : paires réseau / variante de référence (accès + réseau + accès ≤ 400 m).
Règles anti-double comptage :
- la population n'est portée que par le carreau ; un carreau compte une fois par mode et une fois en tout ;
- un mode compte une fois par carreau, quel que soit le nombre d'options de ce mode (n_modes) ;
- la population « par option » existe en deux versions : non exclusive (K5, recouvrements)
  et exclusive (chaque carreau donné à son option la plus proche, somme = population couverte).
Le score de potentiel et l'optimisation ne sont pas ici.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MODES = ("bus", "citiz", "velo")


def paires_reference(paires: pd.DataFrame) -> pd.DataFrame:
    reference = paires[(paires["methode"] == "reseau") & (paires["variante"] == "reference")].copy()
    if reference.duplicated(subset=["cell_id", "offre_id"]).any():
        raise RuntimeError("Paires de référence en double.")
    return reference


def quintile_pondere(valeur: pd.Series, poids: pd.Series) -> pd.Series:
    """Quintile de niveau de vie pondéré par la population : chaque quintile ≈ 20 % des habitants."""
    valide = valeur.notna() & (poids > 0)
    ordre = valeur[valide].sort_values(kind="mergesort").index
    cumul = poids[ordre].cumsum() / poids[ordre].sum()
    quintiles = pd.Series(pd.NA, index=valeur.index, dtype="Int64")
    quintiles[ordre] = np.minimum(np.ceil(cumul.to_numpy() * 5), 5).astype(int)
    return quintiles


def acces_cellule(cellules: pd.DataFrame, paires: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par carreau : options par mode (K1), modes distincts, desserte, distance minimale."""
    reference = paires_reference(paires)
    table = cellules.copy()
    total = reference.groupby("cell_id").agg(n_options_total=("offre_id", "nunique"),
                                             dist_min_m=("dist_totale_m", "min"),
                                             n_modes=("mode", "nunique"))
    table = table.merge(total, left_on="cell_id", right_index=True, how="left")
    for mode in MODES:
        du_mode = reference[reference["mode"] == mode].groupby("cell_id").agg(
            **{f"n_options_{mode}": ("offre_id", "nunique"), f"dist_min_{mode}_m": ("dist_totale_m", "min")})
        table = table.merge(du_mode, left_on="cell_id", right_index=True, how="left")
        table[f"n_options_{mode}"] = table[f"n_options_{mode}"].fillna(0).astype("Int64")
        table[f"desservi_{mode}"] = table[f"n_options_{mode}"] > 0
    table["n_options_total"] = table["n_options_total"].fillna(0).astype("Int64")
    table["n_modes"] = table["n_modes"].fillna(0).astype("Int64")
    table["desservi"] = table["n_options_total"] > 0
    for colonne in ["dist_min_m", *[f"dist_min_{m}_m" for m in MODES]]:
        table[colonne] = table[colonne].astype("Float64")
    table["options_pour_1000_hab"] = (table["n_options_total"] / table["pop"].where(table["pop"] >= 1) * 1000).astype("Float64")
    table["classe_acces"] = pd.cut(table["n_options_total"].astype(float), [-0.5, 0.5, 2.5, 5.5, np.inf],
                                   labels=["0", "1-2", "3-5", "6+"]).astype("string")
    table["niveau_vie_moyen"] = (table["ind_snv"] / table["ind"].where(table["ind"] > 0)).astype("Float64")
    table["quintile_niveau_vie"] = quintile_pondere(table["niveau_vie_moyen"], table["pop"])
    return table


def desserte_offre(offres: pd.DataFrame, cellules: pd.DataFrame, paires: pd.DataFrame) -> pd.DataFrame:
    """K5 par option : population à ≤ 5 min (non exclusive) et population exclusive (option la plus proche).

    Exclusif : pour chaque carreau et chaque mode, une seule option, la plus proche ; en cas
    d'égalité, l'offre_id le plus petit. La somme des populations exclusives d'un mode égale
    la population couverte par ce mode.
    """
    reference = paires_reference(paires).merge(cellules[["cell_id", "pop"]], on="cell_id")
    non_exclusive = reference.groupby("offre_id").agg(pop_5min=("pop", "sum"), n_carreaux=("cell_id", "nunique"))
    plus_proche = (reference.sort_values(["cell_id", "mode", "dist_totale_m", "offre_id"])
                   .drop_duplicates(subset=["cell_id", "mode"]))
    exclusive = plus_proche.groupby("offre_id").agg(pop_exclusive=("pop", "sum"),
                                                   n_carreaux_exclusifs=("cell_id", "nunique"))
    table = offres.merge(non_exclusive, left_on="offre_id", right_index=True, how="left") \
                  .merge(exclusive, left_on="offre_id", right_index=True, how="left")
    for colonne in ("pop_5min", "pop_exclusive"):
        table[colonne] = table[colonne].fillna(0.0).astype("Float64")
    for colonne in ("n_carreaux", "n_carreaux_exclusifs"):
        table[colonne] = table[colonne].fillna(0).astype("Int64")
    table["atteinte"] = table["n_carreaux"] > 0
    return table


def couverture(acces: pd.DataFrame, niveaux: dict[str, str]) -> pd.DataFrame:
    """Agrégation par périmètre (nom → colonne) et par mode. Toujours une somme de carreaux distincts."""
    lignes = []
    for type_perimetre, colonne in niveaux.items():
        for perimetre, groupe in acces.groupby(colonne, dropna=False):
            pop_totale = float(groupe["pop"].sum())
            for mode in ("tous", *MODES):
                desservi = groupe["desservi"] if mode == "tous" else groupe[f"desservi_{mode}"]
                n = groupe["n_options_total"] if mode == "tous" else groupe[f"n_options_{mode}"]
                pop_desservie = float(groupe.loc[desservi, "pop"].sum())
                lignes.append({
                    "perimetre_type": type_perimetre, "perimetre_id": str(perimetre), "mode": mode,
                    "pop_totale": pop_totale, "pop_desservie": pop_desservie,
                    "pop_non_desservie": pop_totale - pop_desservie,
                    "taux_couverture": pop_desservie / pop_totale if pop_totale else None,
                    "n_carreaux": len(groupe), "n_carreaux_desservis": int(desservi.sum()),
                    "options_moyennes_par_habitant": float((n.astype(float) * groupe["pop"]).sum() / pop_totale) if pop_totale else None,
                    "pop_au_moins_2_modes": float(groupe.loc[groupe["n_modes"] >= 2, "pop"].sum()) if mode == "tous" else None,
                })
    table = pd.DataFrame(lignes)
    for colonne in ("pop_totale", "pop_desservie", "pop_non_desservie", "taux_couverture",
                    "options_moyennes_par_habitant", "pop_au_moins_2_modes"):
        table[colonne] = table[colonne].astype("Float64")
    return table


def distribution(acces: pd.DataFrame) -> pd.DataFrame:
    """Population par nombre d'options accessibles (histogramme de la page 2), par mode."""
    lignes = []
    for mode in ("tous", *MODES):
        n = acces["n_options_total"] if mode == "tous" else acces[f"n_options_{mode}"]
        for valeur, groupe in acces.groupby(n.astype(int)):
            lignes.append({"mode": mode, "n_options": int(valeur), "pop": float(groupe["pop"].sum()),
                           "n_carreaux": len(groupe)})
    table = pd.DataFrame(lignes)
    table["pop"] = table["pop"].astype("Float64")
    return table


def equite(acces: pd.DataFrame) -> pd.DataFrame:
    """Couverture par quintile de niveau de vie (K12, situation actuelle, sans scénario)."""
    lignes = []
    for quintile, groupe in acces.groupby("quintile_niveau_vie", dropna=False):
        pop = float(groupe["pop"].sum())
        for mode in ("tous", *MODES):
            desservi = groupe["desservi"] if mode == "tous" else groupe[f"desservi_{mode}"]
            lignes.append({"quintile_niveau_vie": "non renseigné" if pd.isna(quintile) else str(int(quintile)),
                           "mode": mode, "pop": pop, "pop_desservie": float(groupe.loc[desservi, "pop"].sum()),
                           "taux_couverture": float(groupe.loc[desservi, "pop"].sum()) / pop if pop else None})
    table = pd.DataFrame(lignes)
    for colonne in ("pop", "pop_desservie", "taux_couverture"):
        table[colonne] = table[colonne].astype("Float64")
    return table


def population_nouvellement_couverte(acces: pd.DataFrame, cellules_atteintes: set, mode: str | None = None) -> float:
    """K6 : population des carreaux NON desservis aujourd'hui qui seraient atteints par un scénario.

    `cellules_atteintes` : carreaux à ≤ 5 min des nouvelles implantations (paires candidat × carreau, E7).
    Un carreau déjà desservi n'apporte rien ; chaque carreau compte une fois.
    """
    desservi = acces["desservi"] if mode is None else acces[f"desservi_{mode}"]
    nouveaux = (~desservi) & acces["cell_id"].isin(cellules_atteintes)
    return float(acces.loc[nouveaux, "pop"].sum())
