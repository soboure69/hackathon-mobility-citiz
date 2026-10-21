"""Tests de l'étape silver/spatial, sur un petit réseau construit par le test."""
import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from src.cleaning.audit import Suivi
from src.geospatial import rattachement


def reseau():
    noeuds = gpd.GeoDataFrame({"node_id": [1, 2, 3, 4]},
                              geometry=[Point(0, 0), Point(100, 0), Point(200, 0), Point(300, 0)], crs=2154)
    aretes = gpd.GeoDataFrame({"u": [1, 2, 3], "v": [2, 3, 4],
                               "statut_transformation": ["standardise", "standardise", "exclu"]},
                              geometry=[None, None, None], crs=2154)
    return noeuds, aretes


def test_noeud_atteint_seulement_par_busway_non_routable():
    noeuds, aretes = reseau()
    assert list(rattachement.noeuds_routables(noeuds, aretes)["node_id"]) == [1, 2, 3]


def test_rattachement_au_plus_proche_routable():
    noeuds, aretes = reseau()
    routables = rattachement.noeuds_routables(noeuds, aretes)
    ids, distances = rattachement.rattacher(gpd.GeoSeries([Point(110, 30), Point(320, 0)], crs=2154), routables)
    assert list(ids) == [2, 3]                 # le nœud 4 (busway seul) n'est jamais choisi
    assert round(float(distances[1])) == 120


def test_rattachement_refuse_un_autre_crs():
    noeuds, aretes = reseau()
    with pytest.raises(RuntimeError, match="2154"):
        rattachement.rattacher(gpd.GeoSeries([Point(0, 0)], crs=4326), noeuds)


def offre(mode, ids, points):
    return gpd.GeoDataFrame({"offre_id": [f"{mode}_{i}" for i in ids], "mode": mode, "source_id": "S99",
                             "id_origine": ids, "nom": ids, "run_id": "R"}, geometry=points, crs=2154)


def test_offre_points_union_emprise_et_rg08():
    noeuds, aretes = reseau()
    routables = rattachement.noeuds_routables(noeuds, aretes)
    suivi = Suivi("RUN")
    points = rattachement.construire_offre_points(
        [offre("bus", ["a"], [Point(0, 10)]), offre("velo", ["b"], [Point(150, 900)])],
        routables, box(-50, -50, 400, 50), suivi, 400.0, "RUN")
    resultat = points.set_index("offre_id")
    assert bool(resultat.loc["bus_a", "dans_emprise"]) and not bool(resultat.loc["velo_b", "dans_emprise"])
    assert list(suivi.table()["id_origine"]) == ["b"]          # à 900 m du réseau : RG-08
    assert len(points) == 2                                     # rien n'est retiré


def test_offre_id_en_double_refuse():
    noeuds, aretes = reseau()
    routables = rattachement.noeuds_routables(noeuds, aretes)
    with pytest.raises(RuntimeError, match="double"):
        rattachement.construire_offre_points([offre("bus", ["a"], [Point(0, 0)])] * 2, routables,
                                             box(0, 0, 1, 1), Suivi("R"), 400.0, "R")
