"""Tests des jointures : option → commune, carreau → admin, paires carreau × option."""
import geopandas as gpd
import networkx as nx
import pandas as pd
import pytest
from shapely.geometry import Point, box

from src.geospatial import accessibilite, rattachement


def communes():
    return gpd.GeoDataFrame({"code_insee": ["17001", "17002"], "epci_siren": ["111111111"] * 2,
                             "code_departement": ["17", "17"], "code_region": ["75", "75"]},
                            geometry=[box(0, 0, 1000, 1000), box(1000, 0, 2000, 1000)], crs=2154)


def test_option_rattachee_a_sa_commune_ou_hors_epci():
    points = gpd.GeoDataFrame({"offre_id": ["a", "b"]}, geometry=[Point(500, 500), Point(5000, 500)], crs=2154)
    resultat = rattachement.rattacher_admin_options(points, communes()).set_index("offre_id")
    assert resultat.loc["a", "commune_insee"] == "17001" and not resultat.loc["a", "hors_epci"]
    assert pd.isna(resultat.loc["b", "commune_insee"]) and resultat.loc["b", "hors_epci"]


def test_recouvrement_de_communes_detecte():
    doublees = pd.concat([communes(), communes().iloc[[0]].assign(code_insee="17999")])
    points = gpd.GeoDataFrame({"offre_id": ["a"]}, geometry=[Point(500, 500)], crs=2154)
    with pytest.raises(RuntimeError, match="recouvrement"):
        rattachement.rattacher_admin_options(points, doublees)


def test_carreau_departement_et_concordance_du_centroide():
    cellules = gpd.GeoDataFrame({"cell_id": ["c1", "c2"], "commune_insee": ["17001", "17001"],
                                 "x_centroide": [500.0, 1500.0], "y_centroide": [500.0, 500.0]},
                                geometry=[box(400, 400, 600, 600), box(1400, 400, 1600, 600)], crs=2154)
    resultat = rattachement.completer_admin_cellules(cellules, communes()).set_index("cell_id")
    assert list(resultat["code_departement"]) == ["17", "17"]
    assert bool(resultat.loc["c1", "centroide_dans_commune"])
    assert not bool(resultat.loc["c2", "centroide_dans_commune"])      # attribut 17001, centroïde dans 17002


def petit_cas():
    # Réseau en ligne : nœuds 1-2-3-4, 100 m entre chaque ; l'arête 3-4 est une trunk (RC-01).
    aretes = gpd.GeoDataFrame({"u": [1, 2, 3], "v": [2, 3, 4], "length_m": [100.0, 100.0, 100.0],
                               "statut_transformation": ["standardise"] * 3,
                               "regles_appliquees": ["", "", "RC-01"]}, geometry=[None] * 3, crs=2154)
    cellules = pd.DataFrame({"cell_id": ["c1", "c4"], "node_id": [1, 4], "dist_snap_m": [50.0, 10.0],
                             "x_centroide": [-50.0, 300.0], "y_centroide": [0.0, 10.0]})
    offres = gpd.GeoDataFrame({"offre_id": ["o"], "mode": ["bus"], "node_id": [3], "dist_snap_m": [20.0]},
                              geometry=[Point(200, 20)], crs=2154)
    return aretes, cellules, offres


def test_paires_reseau_budget_et_somme_des_distances():
    aretes, cellules, offres = petit_cas()
    paires = accessibilite.paires_reseau(cellules, offres, accessibilite.graphe_routable(aretes), 400.0, "reference")
    resultat = paires.set_index("cell_id")
    assert set(resultat.index) == {"c1", "c4"}
    assert float(resultat.loc["c1", "dist_totale_m"]) == 270.0   # 50 (accès) + 200 (réseau) + 20 (accès)
    assert float(resultat.loc["c4", "dist_totale_m"]) == 130.0   # 10 + 100 + 20


def test_paires_reseau_incluent_les_acces():
    aretes, cellules, offres = petit_cas()
    paires = accessibilite.paires_reseau(cellules, offres, accessibilite.graphe_routable(aretes), 300.0, "reference")
    assert sorted(paires["cell_id"]) == ["c1", "c4"]        # 270 et 130 ≤ 300
    paires = accessibilite.paires_reseau(cellules, offres, accessibilite.graphe_routable(aretes), 250.0, "reference")
    assert sorted(paires["cell_id"]) == ["c4"]              # 270 > 250 : l'accès compte dans le budget


def test_variante_sans_trunk():
    aretes, cellules, offres = petit_cas()
    paires = accessibilite.paires_reseau(cellules, offres, accessibilite.graphe_routable(aretes, sans_trunk=True),
                                         400.0, "sans_trunk")
    assert "c4" not in set(paires["cell_id"])               # seul chemin vers 4 : l'arête trunk


def test_vol_oiseau():
    _, cellules, offres = petit_cas()
    paires = accessibilite.paires_vol_oiseau(cellules, offres, 300.0)
    assert sorted(paires["cell_id"]) == ["c1", "c4"]
    assert (paires["methode"] == "vol_oiseau").all()
