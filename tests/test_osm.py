"""Tests de l'emprise S05, sans réseau."""
import geopandas as gpd
import networkx as nx
import pytest
from osmnx._errors import ResponseStatusCodeError
from shapely.geometry import Point, box

from src.ingestion import osm
from src.ingestion.osm import construire_emprise, ecrire_emprise


def carre_lambert93():
    # Carré de 1 km de côté, en Lambert-93, près de La Rochelle.
    return gpd.GeoDataFrame(geometry=[box(380000, 6570000, 381000, 6571000)], crs=2154)


def test_emprise_en_4326_et_elargie():
    emprise = construire_emprise(carre_lambert93(), 500)
    assert emprise.crs.to_epsg() == 4326
    retour = emprise.to_crs(2154).geometry.iloc[0]
    assert retour.contains(Point(379600, 6570500))  # à 400 m du bord : dans le tampon
    assert not retour.contains(Point(379400, 6570500))  # à 600 m : hors tampon


def test_tampon_negatif_refuse():
    with pytest.raises(ValueError):
        construire_emprise(carre_lambert93(), -1)


def test_emprise_jamais_ecrasee(tmp_path):
    emprise = construire_emprise(carre_lambert93(), 0)
    ecrire_emprise(emprise, tmp_path / "emprise.geojson")
    with pytest.raises(FileExistsError):
        ecrire_emprise(emprise, tmp_path / "emprise.geojson")


def test_overpass_sature_puis_reussi(tmp_path, monkeypatch):
    graphe = nx.MultiDiGraph(crs="epsg:4326")
    graphe.add_node(1, x=-1.15, y=46.16)
    graphe.add_node(2, x=-1.14, y=46.16)
    graphe.add_edge(1, 2, length=770.0)
    reponses = [ResponseStatusCodeError("502 saturé"), graphe]

    def faux_overpass(*args, **kwargs):
        element = reponses.pop(0)
        if isinstance(element, Exception):
            raise element
        return element

    monkeypatch.setattr(osm.ox, "graph_from_polygon", faux_overpass)
    pauses = []
    stats = osm.telecharger_graphe_pieton(
        construire_emprise(carre_lambert93(), 0), tmp_path / "g.graphml", attendre=pauses.append,
    )
    assert stats["tentatives"] == 2
    assert pauses == [60.0]
    assert (tmp_path / "g.graphml").is_file()
