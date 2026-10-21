"""Tests de l'emprise S05, sans réseau."""
import geopandas as gpd
import pytest
from shapely.geometry import Point, box

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
