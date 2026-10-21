"""Tests de src/ingestion/gbfs.py (fonctions pures, sans réseau)."""
import pytest

from src.ingestion.gbfs import controler_stations, lister_flux


def test_flux_v3():
    index = {"version": "3.0", "data": {"feeds": [
        {"name": "system_information", "url": "https://a.fr/si"},
        {"name": "station_information", "url": "https://a.fr/st"},
    ]}}
    assert lister_flux(index) == {"system_information": "https://a.fr/si", "station_information": "https://a.fr/st"}


def test_flux_v2_prefere_le_francais():
    index = {"data": {
        "en": {"feeds": [{"name": "system_information", "url": "https://a.fr/en"}]},
        "fr": {"feeds": [{"name": "system_information", "url": "https://a.fr/fr"}]},
    }}
    assert lister_flux(index) == {"system_information": "https://a.fr/fr"}


def test_flux_v2_autre_langue():
    index = {"data": {"en": {"feeds": [{"name": "system_information", "url": "https://a.fr/en"}]}}}
    assert lister_flux(index) == {"system_information": "https://a.fr/en"}


def test_index_sans_data():
    with pytest.raises(ValueError, match="data"):
        lister_flux({"version": "3.0"})


def test_controles_stations_completes():
    contenu = {"data": {"stations": [{"lat": 46.1, "lon": -1.1, "capacity": 2}]}}
    assert [c["resultat"] for c in controler_stations(contenu)] == ["ok", "ok", "ok"]


def test_controles_stations_incompletes():
    contenu = {"data": {"stations": [
        {"lat": 46.1, "lon": -1.1, "capacity": 2},
        {"lat": None, "lon": -1.1},
    ]}}
    resultats = {c["id"]: (c["resultat"], c["valeur"]) for c in controler_stations(contenu)}
    assert resultats["stations_coordonnees"] == ("alerte", "1/2")
    assert resultats["stations_capacite"] == ("alerte", "1/2")


def test_aucune_station():
    assert controler_stations({"data": {"stations": []}})[0]["resultat"] == "echec"
