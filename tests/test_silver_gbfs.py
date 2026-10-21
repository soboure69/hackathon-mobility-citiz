"""Tests du bloc Silver S-2 (GBFS), sur des stations construites par le test."""
from src.cleaning import gbfs
from src.cleaning.audit import Suivi, verifier_conservation

EMPRISE = {"lat_min": 41.0, "lat_max": 51.5, "lon_min": -5.5, "lon_max": 10.0, "precision_min_decimales": 4}

STATIONS = [
    {"station_id": "A", "name": [{"text": "Arsenal", "language": "fr"}], "lat": 46.1595, "lon": -1.1486, "capacity": 2},
    {"station_id": "B", "name": "Gare", "lat": 46.1530, "lon": -1.1450, "num_vehicles_available": 3},
    {"station_id": "C", "name": [{"text": "Minimes 1", "language": "fr"}], "lat": 46.1413, "lon": -1.1703, "capacity": 4},
    {"station_id": "D", "name": [{"text": "Minimes 2", "language": "fr"}], "lat": 46.1413, "lon": -1.1703, "capacity": 4},
    {"station_id": "T", "name": [{"text": "Station test", "language": "fr"}], "lat": 50.1399, "lon": 14.1499, "capacity": 1},
]


def construire():
    suivi = Suivi("RUN")
    standard, ignores = gbfs.standardiser_stations(STATIONS, source_id="S99", fichier_origine="f",
                                                   sha256_origine="h", date_donnee="d", run_id="RUN")
    propre = gbfs.nettoyer_stations(standard, suivi, EMPRISE)
    offre = gbfs.construire_offre(propre, suivi, mode="velo", source_id="S99")
    return suivi, standard, propre, offre, ignores


def test_nom_v3_et_v2():
    assert gbfs.texte_localise([{"text": "En", "language": "en"}, {"text": "Fr", "language": "fr"}]) == "Fr"
    assert gbfs.texte_localise([{"text": "En", "language": "en"}]) == "En"
    assert gbfs.texte_localise("Gare") == "Gare"


def test_disponibilites_non_reprises():
    _, standard, _, _, ignores = construire()
    assert ignores == ["num_vehicles_available"]
    assert "num_vehicles_available" not in standard.columns


def test_station_hors_metropole_rejetee_et_conservation():
    suivi, standard, propre, _, _ = construire()
    rejets = suivi.table().query("niveau == 'rejet'")
    assert list(rejets["id_origine"]) == ["T"] and list(rejets["regle_id"]) == ["RG-02"]
    verifier_conservation(len(standard), len(propre), len(rejets), "cleaned")


def test_capacite_absente_signalee_pas_inventee():
    suivi, _, _, offre, _ = construire()
    alertes = suivi.table()
    assert list(alertes.loc[alertes["regle_id"] == "RC-07", "id_origine"]) == ["B"]
    assert offre.set_index("id_origine")["capacite"].isna().sum() == 1


def test_coordonnees_partagees_gardees():
    suivi, _, _, offre, _ = construire()
    assert sorted(suivi.table().query("regle_id == 'RG-07'")["id_origine"]) == ["C", "D"]
    assert sorted(offre["offre_id"]) == ["velo_S99_A", "velo_S99_B", "velo_S99_C", "velo_S99_D"]
    assert offre.crs.to_epsg() == 2154
