"""Couverture maximale sous budget (MVP Citiz) : modèle PuLP / CBC et glouton de contrôle.

max Σ_j p_j y_j + ε Σ_i s_i x_i
s.c. y_j ≤ Σ_{i ∈ N(j)} x_i      (un carreau n'est couvert que si une station l'atteint)
     Σ_i c_i x_i ≤ B             (budget)
     Σ_i x_i ≤ min(N_max, ⌊B / c_min⌋)   (inégalité valide)
     x_i ∈ {0, 1}, 0 ≤ y_j ≤ 1
J = carreaux NON desservis par le type aujourd'hui : on ne compte que des habitants nouveaux.
ε = min(p_j > 0) / (2 Σ s_i) : le score ne peut jamais valoir un carreau, même le moins peuplé.
"""
from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass
from functools import cached_property

import pandas as pd
import pulp


@dataclass
class Donnees:
    sites: pd.DataFrame            # candidat_id, cout, score01
    carreaux: pd.DataFrame         # cell_id, pop, prioritaire
    liens: pd.DataFrame            # candidat_id, cell_id (carreaux de J seulement)

    @cached_property
    def couverture(self) -> dict[str, set]:
        return self.liens.groupby("candidat_id")["cell_id"].agg(set).to_dict()


def preparer(candidats: pd.DataFrame, paires: pd.DataFrame, acces: pd.DataFrame, type_equipement: str,
             cout: float, communes_prioritaires: set[str]) -> Donnees:
    retenus = candidats[(candidats["type_equipement"] == type_equipement) & candidats["retenu"]]
    sites = pd.DataFrame({"candidat_id": retenus["candidat_id"].to_numpy(), "cout": float(cout),
                          "score01": (retenus["score"].astype(float) / 100).to_numpy()})
    non_desservis = acces[~acces[f"desservi_{type_equipement}"].astype(bool)]
    liens = paires[paires["candidat_id"].isin(sites["candidat_id"]) & paires["cell_id"].isin(non_desservis["cell_id"])]
    liens = liens[["candidat_id", "cell_id"]].drop_duplicates()
    carreaux = non_desservis[non_desservis["cell_id"].isin(liens["cell_id"])][["cell_id", "pop", "commune_insee"]].copy()
    carreaux["prioritaire"] = carreaux["commune_insee"].isin(communes_prioritaires)
    return Donnees(sites.reset_index(drop=True), carreaux.reset_index(drop=True), liens.reset_index(drop=True))


def epsilon(donnees: Donnees) -> float:
    pop_min = float(donnees.carreaux.loc[donnees.carreaux["pop"] > 0, "pop"].min())
    return pop_min / (2 * max(float(donnees.sites["score01"].sum()), 1e-9))


def resoudre(donnees: Donnees, budget: float, n_max: int | None = None, temps_max_s: int = 120,
             ecart_relatif: float = 0.0, part_prioritaire_min: float | None = None) -> dict:
    """Résout le modèle exact. Renvoie statut, sites choisis, K6, durée.

    `part_prioritaire_min` (variante équité, C-5) : au moins cette part des habitants nouvellement
    couverts doit vivre dans une commune prioritaire.
    """
    modele = pulp.LpProblem("couverture_max_budget", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"x_{n}", cat="Binary") for n, i in enumerate(donnees.sites["candidat_id"])}
    y = {j: pulp.LpVariable(f"y_{n}", lowBound=0, upBound=1) for n, j in enumerate(donnees.carreaux["cell_id"])}
    pop = dict(zip(donnees.carreaux["cell_id"], donnees.carreaux["pop"].astype(float)))
    score = dict(zip(donnees.sites["candidat_id"], donnees.sites["score01"]))
    cout = dict(zip(donnees.sites["candidat_id"], donnees.sites["cout"]))
    eps = epsilon(donnees)
    modele += pulp.lpSum(pop[j] * y[j] for j in y) + eps * pulp.lpSum(score[i] * x[i] for i in x)
    for j, sites_j in donnees.liens.groupby("cell_id")["candidat_id"]:
        modele += y[j] <= pulp.lpSum(x[i] for i in sites_j)
    modele += pulp.lpSum(cout[i] * x[i] for i in x) <= budget
    if part_prioritaire_min is not None:
        # Sans le lien y_j ≥ x_i, le solveur pourrait « oublier » des habitants couverts hors des
        # communes prioritaires (y_j < 1) pour gonfler la part prioritaire. On impose donc y_j = 1
        # dès qu'un site ouvert atteint le carreau : la part est calculée sur la couverture réelle.
        for i, j in donnees.liens[["candidat_id", "cell_id"]].itertuples(index=False):
            modele += y[j] >= x[i]
        prio = dict(zip(donnees.carreaux["cell_id"], donnees.carreaux["prioritaire"].astype(bool)))
        modele += (pulp.lpSum(pop[j] * y[j] for j in y if prio[j])
                   >= part_prioritaire_min * pulp.lpSum(pop[j] * y[j] for j in y))
    # Inégalité valide : on ne peut pas ouvrir plus de ⌊B / c_min⌋ stations. Elle ne retire aucune
    # solution entière, mais elle empêche la relaxation d'« acheter » une fraction de station
    # (sans elle, 170 000 € / 4 000 € = 42,5 stations et l'optimum n'est pas prouvé en 120 s).
    plafond = math.floor((budget + 1e-9) / float(donnees.sites["cout"].min()))
    modele += pulp.lpSum(x.values()) <= (plafond if n_max is None else min(plafond, n_max))
    debut = time.perf_counter()
    statut = modele.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=temps_max_s, gapRel=ecart_relatif, threads=1))
    duree = time.perf_counter() - debut
    choisis = sorted(i for i, v in x.items() if (v.value() or 0) > 0.5)
    # PuLP peut afficher « Optimal » alors que CBC s'est arrêté au temps limite : on lit le statut de la solution.
    prouvee = modele.sol_status == pulp.LpSolutionOptimal
    return {"statut": pulp.LpStatus[statut], "statut_solution": pulp.LpSolution[modele.sol_status],
            "optimum_prouve": prouvee, "ecart_relatif_garanti": ecart_relatif if prouvee else None,
            "choisis": choisis, "k6": population_couverte(donnees, choisis),
            "k6_prioritaire": population_couverte(donnees, choisis, prioritaire_seulement=True),
            "duree_s": duree, "epsilon": eps}


def population_couverte(donnees: Donnees, choisis: list[str], prioritaire_seulement: bool = False) -> float:
    """K6 du portefeuille : carreaux distincts atteints, chacun compté une fois."""
    couverture = donnees.couverture
    atteints = set().union(*(couverture.get(i, set()) for i in choisis)) if choisis else set()
    masque = donnees.carreaux["cell_id"].isin(atteints)
    if prioritaire_seulement:
        masque &= donnees.carreaux["prioritaire"].astype(bool)
    return float(donnees.carreaux.loc[masque, "pop"].sum())


def ordre_ajout(donnees: Donnees, candidats_autorises: list[str], budget: float) -> pd.DataFrame:
    """Glouton : à chaque tour, le site au meilleur gain marginal par euro (égalité : score, puis identifiant).

    Version « paresseuse » (CELF) : un gain marginal ne peut que baisser quand on ajoute des
    stations, donc on ne recalcule que le site en tête de file. Même résultat, beaucoup plus rapide.
    Appliqué à tous les sites, c'est l'heuristique de contrôle ; appliqué aux sites de l'optimum,
    il donne l'ordre d'ajout et les gains marginaux (dont la somme vaut K6).
    """
    couverture = donnees.couverture
    pop = dict(zip(donnees.carreaux["cell_id"], donnees.carreaux["pop"].astype(float)))
    cout = dict(zip(donnees.sites["candidat_id"], donnees.sites["cout"]))
    score = dict(zip(donnees.sites["candidat_id"], donnees.sites["score01"]))
    couverts: set = set()

    def gain(i: str) -> float:
        return sum(pop[j] for j in couverture.get(i, set()) - couverts)

    file = [(-gain(i) / cout[i], -score[i], i, 0) for i in candidats_autorises]
    heapq.heapify(file)
    depense, tour, lignes = 0.0, 0, []
    while file:
        ratio, moins_score, i, tour_calcul = heapq.heappop(file)
        if depense + cout[i] > budget + 1e-9:
            continue                                   # trop cher maintenant : définitivement écarté
        if tour_calcul != tour:                         # gain périmé : on le recalcule et on le remet en file
            heapq.heappush(file, (-gain(i) / cout[i], moins_score, i, tour))
            continue
        g = -ratio * cout[i]
        if g <= 0:
            break
        depense += cout[i]
        couverts |= couverture.get(i, set())
        tour += 1
        lignes.append({"candidat_id": i, "ordre_ajout": tour, "cout": cout[i], "pop_nouvelle_marginale": g,
                       "cout_cumule": depense, "pop_nouvelle_cumulee": sum(pop[j] for j in couverts)})
    return pd.DataFrame(lignes, columns=["candidat_id", "ordre_ajout", "cout", "pop_nouvelle_marginale",
                                         "cout_cumule", "pop_nouvelle_cumulee"])
