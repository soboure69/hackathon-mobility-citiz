"""Tests de l'optimisation budgétaire : couverture sans double compte, budget, glouton contre optimum."""
import pandas as pd
import pytest

from src.optimization import couverture as opt


def donnees(liens, pops, cout=1.0, scores=None):
    sites = sorted({s for s, _ in liens})
    return opt.Donnees(
        sites=pd.DataFrame({"candidat_id": sites, "cout": cout,
                            "score01": [(scores or {}).get(s, 0.5) for s in sites]}),
        carreaux=pd.DataFrame({"cell_id": list(pops), "pop": [float(p) for p in pops.values()],
                               "commune_insee": "17001", "prioritaire": False}),
        liens=pd.DataFrame(liens, columns=["candidat_id", "cell_id"]),
    )


def piege():
    # B couvre x et y (10) ; A1 couvre x et a (9) ; A2 couvre y et b (9). Deux stations au plus.
    return donnees([("B", "x"), ("B", "y"), ("A1", "x"), ("A1", "a"), ("A2", "y"), ("A2", "b")],
                   {"x": 5, "y": 5, "a": 4, "b": 4})


def test_optimum_bat_le_glouton_quand_il_le_faut():
    d = piege()
    exact = opt.resoudre(d, budget=2.0)
    glouton = opt.ordre_ajout(d, list(d.sites["candidat_id"]), 2.0)
    assert exact["choisis"] == ["A1", "A2"] and exact["k6"] == 18.0
    assert float(glouton["pop_nouvelle_cumulee"].iloc[-1]) == 14.0      # B puis A1 : 10 + 4
    assert exact["optimum_prouve"]


def test_chaque_carreau_compte_une_fois():
    d = piege()
    assert opt.population_couverte(d, ["B", "A1", "A2"]) == 18.0         # x et y ne comptent pas deux fois


def test_budget_respecte_et_fraction_de_station_impossible():
    d = piege()
    r = opt.resoudre(d, budget=2.5)                                       # 2,5 stations : on en ouvre 2
    assert len(r["choisis"]) == 2 and r["k6"] == 18.0 and r["optimum_prouve"]


def test_somme_des_gains_marginaux_egale_k6():
    d = piege()
    r = opt.resoudre(d, budget=2.0)
    ordre = opt.ordre_ajout(d, r["choisis"], float("inf"))
    assert float(ordre["pop_nouvelle_marginale"].sum()) == r["k6"]
    assert list(ordre["ordre_ajout"]) == [1, 2]


def test_le_score_ne_vaut_jamais_un_habitant():
    # Deux sites d'impact égal : le score départage. Un site meilleur en score mais moins utile ne gagne pas.
    d = donnees([("S1", "a"), ("S2", "b"), ("S3", "c")], {"a": 0.5, "b": 0.5, "c": 0.4},
                scores={"S1": 0.1, "S2": 0.9, "S3": 1.0})
    assert opt.epsilon(d) * d.sites["score01"].sum() < 0.4               # ε · Σ s < plus petit carreau
    assert opt.resoudre(d, budget=1.0)["choisis"] == ["S2"]


def test_preparer_ne_garde_que_les_carreaux_non_desservis():
    candidats = pd.DataFrame({"candidat_id": ["S1", "S2"], "type_equipement": "citiz", "retenu": [True, False],
                              "score": [80.0, 90.0]})
    paires = pd.DataFrame({"candidat_id": ["S1", "S1", "S2"], "cell_id": ["a", "b", "a"]})
    acces = pd.DataFrame({"cell_id": ["a", "b"], "pop": [10.0, 20.0], "commune_insee": ["17001", "17002"],
                          "desservi_citiz": [True, False]})
    d = opt.preparer(candidats, paires, acces, "citiz", 8500, {"17002"})
    assert list(d.sites["candidat_id"]) == ["S1"]                        # S2 non retenu
    assert list(d.carreaux["cell_id"]) == ["b"] and bool(d.carreaux["prioritaire"].iloc[0])
