"""Tests sans réseau : stations embarquées et contrôle d'archives."""
import zipfile

import py7zr

from src.ingestion.fichier import controler_archive
from src.ingestion.gbfs import trouver_stations


def test_trouver_stations_profondes():
    export = {"data": {"fr": {"stations": [{"lat": 46.1, "lon": -1.1}, {"lat": 46.2, "lon": -1.2}]}}}
    assert len(trouver_stations(export)) == 2


def test_trouver_stations_absentes():
    assert trouver_stations({"data": {"feeds": []}}) is None


def test_archive_zip_integre(tmp_path):
    chemin = tmp_path / "a.zip"
    with zipfile.ZipFile(chemin, "w") as archive:
        archive.writestr("stops.txt", "stop_id\n1\n")
    resultats = {c["id"]: c for c in controler_archive(chemin)}
    assert resultats["archive_integre"]["resultat"] == "ok"
    assert resultats["contenu_archive"]["valeur"] == ["stops.txt"]


def test_archive_7z_integre(tmp_path):
    (tmp_path / "donnees.txt").write_bytes(b"abc")
    chemin = tmp_path / "a.7z"
    with py7zr.SevenZipFile(chemin, "w") as archive:
        archive.write(tmp_path / "donnees.txt", "donnees.txt")
    resultats = {c["id"]: c for c in controler_archive(chemin)}
    assert resultats["archive_integre"]["resultat"] == "ok"
    assert resultats["contenu_archive"]["valeur"] == ["donnees.txt"]
