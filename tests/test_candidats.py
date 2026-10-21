"""Tests du score de potentiel (K10) : sites, variables, normalisation, score, sensibilité, équité."""
import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from src.scoring import candidats as cand

POIDS = {"impact": 0.4, "besoin": 0.2, "complementarite_bus": 0.15, "logement_collectif": 0.15, "petits_menages": 0.1}


def test_un_site_par_noeud_carreau_le_plus_peuple():
    cellules = pd.DataFrame({"cell_id": ["a", "b", "c"], "node_id": [1, 1, 2], "pop": [10.0, 50.0, 5.0],
                             "commune_insee": ["17001"] * 3})
    noeuds = gpd.GeoDataFrame({"node_id": [1, 2, 3]}, geometry=[Point(0, 0), Point(100, 0), Point(200, 0)], crs=2154)
    sites = cand.generer_sites(cellules, noeuds).set_index("node_id")
    assert list(sites.index) == [1, 2] and sites.loc[1, "cell_id_origine"] == "b"


def test_zone_atteinte_et_variables():
    graphe = nx.Graph()
    graphe.add_edge(1, 2, length=300.0)
    sites = pd.DataFrame({"candidat_id": ["S"], "node_id": [1]})
    cellules = pd.DataFrame({"cell_id": ["a", "b"], "node_id": [1, 2], "dist_snap_m": [20.0, 50.0]})
    paires = cand.paires_sites(sites, cellules, graphe, 400.0)
    assert sorted(paires["cell_id"]) == ["a", "b"]                 # b : 50 + 300 = 350 ≤ 400
    acces = pd.DataFrame({"cell_id": ["a", "b"], "pop": [100.0, 300.0], "men": [40.0, 100.0],
                          "men_coll": [40.0, 50.0], "men_1ind": [20.0, 30.0], "ind": [100.0, 300.0],
                          "ind_snv": [2e6, 6e6], "desservi": [True, False], "desservi_bus": [True, False],
                          "desservi_citiz": [True, False]})
    v = cand.variables(sites, paires, acces, "citiz").iloc[0]
    assert v["pop_rayon"] == 400.0 and v["pop_nouvelle"] == 300.0
    assert v["taux_redondance"] == pytest.approx(0.25)
    assert v["besoin"] == pytest.approx(0.75) and v["logement_collectif"] == pytest.approx(90 / 140)


def test_normalisation_par_rang_robuste_aux_extremes():
    n = cand.normaliser(pd.Series([1.0, 2.0, 3.0, 1_000_000.0]))
    assert list(n) == [0.25, 0.5, 0.75, 1.0]


def test_score_somme_des_contributions_et_bornes():
    table = pd.DataFrame({"candidat_id": list("abc"), "impact": [10.0, 20.0, 30.0], "besoin": [0.1, 0.5, 0.2],
                          "complementarite_bus": [0.9, 0.1, 0.5], "logement_collectif": [0.2, 0.3, 0.4],
                          "petits_menages": [0.3, 0.2, 0.1]})
    note = cand.noter(table, POIDS)
    contributions = note[[f"contribution_{v}" for v in cand.VARIABLES]].sum(axis=1)
    assert np.allclose(contributions, note["score"]) and note["score"].between(0, 100).all()
    rang = cand.classer(note)
    assert rang[note["score"].idxmax()] == 1 and sorted(rang) == [1, 2, 3]


def test_ponderations_doivent_sommer_a_un():
    with pytest.raises(ValueError):
        cand.noter(pd.DataFrame({v: [1.0] for v in cand.VARIABLES}), {**POIDS, "impact": 0.5})


def test_sensibilite_reproductible():
    rng = np.random.default_rng(0)
    table = pd.DataFrame({v: rng.random(50) for v in cand.VARIABLES})
    f1, t1 = cand.sensibilite(table, POIDS, 50, 20, 7, 5)
    f2, _ = cand.sensibilite(table, POIDS, 50, 20, 7, 5)
    assert f1.equals(f2) and f1.between(0, 1).all() and len(t1) == 10
    assert cand.spearman(np.array([1, 2, 3]), np.array([10, 20, 30])) == pytest.approx(1.0)


def test_garde_fou_equite():
    table = pd.DataFrame({"rang": range(1, 11), "commune_insee": ["A"] * 8 + ["P", "P"]})
    choix = cand.selection_equite(table, {"P"}, top_n=4, quota=0.5)
    retenus = table[choix.notna()]
    assert len(retenus) == 4 and (retenus["commune_insee"] == "P").sum() == 2
