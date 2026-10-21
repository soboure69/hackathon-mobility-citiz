"""Tests du bloc Silver S-1 sur un petit GTFS construit par le test (aucune donnée réelle)."""
import zipfile

import pytest

from src.cleaning import gtfs
from src.cleaning.audit import Suivi, verifier_conservation
from src.cleaning.normalisation import normaliser_nom

EMPRISE = {"lat_min": 41.0, "lat_max": 51.5, "lon_min": -5.5, "lon_max": 10.0, "precision_min_decimales": 4}

STOPS = """stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station
Z1,Place Test,46.160000,-1.150000,1,
Q1,Place Test A,46.160100,-1.150100,0,Z1
Q2,Place Test B,46.160200,-1.150200,0,Z1
Q8,Place Test C,46.16,-1.150300,0,Z1
Z2,Zone morte,46.170000,-1.160000,1,
Q3,Zone morte A,46.170100,-1.160100,0,Z2
Q4,Quai orphelin,46.180000,-1.170000,0,
Q5,Sans coordonnees,,,0,Z1
Q6,Inverse,-1.150000,46.160000,0,Z1
Q7,Doublon un,46.161000,-1.151000,0,Z1
Q7,Doublon deux,46.162000,-1.152000,0,Z1
E1,Entree,46.160500,-1.150500,2,Z1
"""
CALENDAR = "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\nS1,1,0,0,0,0,0,0,20261001,20261231\n"
TRIPS = "route_id,service_id,trip_id\nR1,S1,T1\n"
STOP_TIMES = "trip_id,arrival_time,departure_time,stop_id,stop_sequence\nT1,08:00:00,08:00:00,Q1,1\nT1,08:05:00,08:05:00,Q4,2\nT1,08:10:00,08:10:00,Q8,3\n"


@pytest.fixture
def archive(tmp_path):
    chemin = tmp_path / "gtfs.zip"
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("stops.txt", STOPS)
        z.writestr("calendar.txt", CALENDAR)
        z.writestr("trips.txt", TRIPS)
        z.writestr("stop_times.txt", STOP_TIMES)
    return chemin


def construire(archive):
    suivi = Suivi("RUN")
    standard = gtfs.standardiser_stops(archive, source_id="S02", fichier_origine="f", sha256_origine="h",
                                       date_donnee="d", run_id="RUN")
    propre = gtfs.nettoyer_stops(standard, suivi, gtfs.quais_desservis(archive), EMPRISE)
    offre, correspondances = gtfs.dedupliquer_zones(propre, suivi, source_id="S02", seuil_rg06_m=None)
    return suivi, standard, propre, offre, correspondances


def test_conservation_et_rejets(archive):
    suivi, standard, propre, _, _ = construire(archive)
    rejets = suivi.table().query("niveau == 'rejet'")
    assert len(standard) == 12
    assert sorted(rejets["regle_id"]) == ["RC-03", "RC-03", "RG-01", "RG-03"]
    verifier_conservation(len(standard), len(propre), len(rejets), "cleaned")  # 12 = 8 + 4


def test_conservation_violee_detectee():
    with pytest.raises(RuntimeError, match="CS-01"):
        verifier_conservation(12, 8, 3, "cleaned")


def test_exclusions_et_alertes(archive):
    suivi, _, propre, _, _ = construire(archive)
    journal = suivi.table()
    exclus = set(journal.loc[journal["niveau"] == "exclusion", "id_origine"])
    assert {"E1", "Q2", "Q3"} <= exclus          # RC-06 entrée ; RC-04 quais sans course
    assert "Z2" in exclus                         # RC-05 zone sans quai desservi
    assert list(journal.loc[journal["regle_id"] == "RG-04", "id_origine"]) == ["Q8"]
    assert propre.crs.to_epsg() == 2154
    assert {"lat_wgs84", "lon_wgs84"} <= set(propre.columns)


def test_dedoublonnage(archive):
    _, _, propre, offre, correspondances = construire(archive)
    assert sorted(offre["offre_id"]) == ["bus_S02_Q4", "bus_S02_Z1"]
    z1 = offre.set_index("offre_id").loc["bus_S02_Z1"]
    assert (z1["n_quais"], z1["n_quais_desservis"]) == (3, 2)     # Q1, Q2, Q8 ; Q2 non desservi
    methodes = correspondances.set_index("id_origine")["methode"]
    assert methodes["Q4"] == "aucune" and methodes["Q1"] == "parent_station"
    gtfs.controler_correspondances(propre, correspondances)       # CS-07


def test_identifiants_restent_du_texte(tmp_path):
    chemin = tmp_path / "g.zip"
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("stops.txt", "stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n00042,A,46.1,-1.1,0,\n")
    assert gtfs.lire_table_gtfs(chemin, "stops.txt")["stop_id"].iloc[0] == "00042"


@pytest.mark.parametrize("brut, attendu", [
    ("Place de Verdun - Quai A", "place de verdun quai a"),
    ("Hôtel-de-Ville", "hotel de ville"),
    ("  Gare   SNCF ", "gare sncf"),
    (None, None),
])
def test_normaliser_nom(brut, attendu):
    assert normaliser_nom(brut) == attendu
