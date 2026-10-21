"""Tests de src/ingestion/http_download.py, sans réseau (fausse session)."""
from datetime import date, datetime

import pytest
import requests

from src.ingestion.http_download import (
    creer_dossier_date,
    nom_fichier_depuis_reponse,
    telecharger_avec_essais,
    telecharger_fichier,
)

SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
JOUR = date(2026, 10, 21)


class FausseReponse:
    """Imite une réponse requests en streaming."""

    def __init__(self, url, statut=200, contenu=b"abc", en_tetes=None, coupure=False):
        self.url = url
        self.status_code = statut
        self.headers = en_tetes or {}
        self._contenu = contenu
        self._coupure = coupure

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code), response=self)

    def iter_content(self, chunk_size):
        yield self._contenu[:1]
        if self._coupure:
            raise requests.exceptions.ChunkedEncodingError("coupure simulée")
        yield self._contenu[1:]


class FausseSession:
    """Renvoie, dans l'ordre, les réponses ou les erreurs préparées."""

    def __init__(self, *elements):
        self._elements = list(elements)
        self.appels = []

    def get(self, url, **kwargs):
        self.appels.append(url)
        element = self._elements.pop(0)
        if isinstance(element, BaseException):
            raise element
        return element


URL = "https://exemple.fr/abc.txt"


def ok():
    return FausseReponse(URL, en_tetes={"Content-Type": "text/plain"})


# --- creer_dossier_date ---

def test_dossier_cree(tmp_path):
    dossier = creer_dossier_date(tmp_path, "gbfs", "larochelle", "S01", JOUR)
    assert dossier == tmp_path / "gbfs" / "larochelle" / "S01_2026-10-21"
    assert dossier.is_dir()


def test_dossier_existant_refuse(tmp_path):
    creer_dossier_date(tmp_path, "gbfs", "larochelle", "S01", JOUR)
    with pytest.raises(FileExistsError):
        creer_dossier_date(tmp_path, "gbfs", "larochelle", "S01", JOUR)


def test_dossier_suffixe(tmp_path):
    creer_dossier_date(tmp_path, "gbfs", "larochelle", "S01", JOUR)
    dossier = creer_dossier_date(tmp_path, "gbfs", "larochelle", "S01", JOUR, suffixe=2)
    assert dossier.name == "S01_2026-10-21_2"


@pytest.mark.parametrize("famille, territoire, source_id, jour, suffixe, erreur", [
    ("gbfs", "larochele", "S01", JOUR, None, ValueError),
    ("gbfs", "larochelle", "S1", JOUR, None, ValueError),
    ("gbfs", "larochelle", "S01", JOUR, 1, ValueError),
    ("gbfs", "larochelle", "S01", datetime(2026, 10, 21, 3, 0), None, TypeError),
])
def test_dossier_parametres_refuses(tmp_path, famille, territoire, source_id, jour, suffixe, erreur):
    with pytest.raises(erreur):
        creer_dossier_date(tmp_path, famille, territoire, source_id, jour, suffixe)


# --- nom_fichier_depuis_reponse ---

@pytest.mark.parametrize("url, en_tetes, attendu", [
    ("https://a.fr/gbfs/v3.0/gbfs.json", {}, "gbfs.json"),
    ("https://a.fr/statistiques/8735162?x=1", {"Content-Type": "text/html; charset=utf-8"}, "8735162.html"),
    ("https://a.fr/t?id=42", {"content-disposition": 'attachment; filename="gtfs.zip"'}, "gtfs.zip"),
    ("https://a.fr/x", {"Content-Disposition": "attachment; filename*=UTF-8''donn%C3%A9es.csv"}, "données.csv"),
    ("https://a.fr/x", {"Content-Disposition": 'attachment; filename="../../evil.zip"'}, "evil.zip"),
    ("https://a.fr/f/station_information", {"Content-Type": "application/json"}, "station_information.json"),
    ("https://a.fr/f/station_information", {"Content-Type": "application/octet-stream"}, "station_information"),
])
def test_nom_fichier(url, en_tetes, attendu):
    assert nom_fichier_depuis_reponse(url, en_tetes) == attendu


def test_nom_fichier_inutilisable():
    with pytest.raises(ValueError, match="inutilisable"):
        nom_fichier_depuis_reponse("https://a.fr/", {})


# --- telecharger_fichier ---

def test_telechargement_reussi(tmp_path):
    description = telecharger_fichier(URL, tmp_path, session=FausseSession(ok()))
    assert description["nom"] == "abc.txt"
    assert description["sha256"] == SHA256_ABC
    assert description["http_status"] == 200
    assert sorted(p.name for p in tmp_path.iterdir()) == ["abc.txt"]


def test_erreur_404_rien_ecrit(tmp_path):
    with pytest.raises(requests.HTTPError):
        telecharger_fichier(URL, tmp_path, session=FausseSession(FausseReponse(URL, statut=404)))
    assert list(tmp_path.iterdir()) == []


def test_coupure_ne_laisse_ni_part_ni_fichier(tmp_path):
    coupee = FausseReponse(URL, coupure=True)
    with pytest.raises(requests.exceptions.ChunkedEncodingError):
        telecharger_fichier(URL, tmp_path, session=FausseSession(coupee))
    assert list(tmp_path.iterdir()) == []


def test_collision_de_nom(tmp_path):
    session = FausseSession(ok(), ok())
    telecharger_fichier(URL, tmp_path, session=session)
    with pytest.raises(FileExistsError):
        telecharger_fichier(URL, tmp_path, session=session)


# --- telecharger_avec_essais ---

def test_erreur_500_puis_succes(tmp_path):
    session = FausseSession(FausseReponse(URL, statut=500), ok())
    pauses = []
    description = telecharger_avec_essais(URL, tmp_path, session=session, attendre=pauses.append)
    assert description["tentatives"] == 2
    assert pauses == [2.0]


def test_404_jamais_reessaye(tmp_path):
    session = FausseSession(FausseReponse(URL, statut=404))
    pauses = []
    with pytest.raises(requests.HTTPError):
        telecharger_avec_essais(URL, tmp_path, session=session, attendre=pauses.append)
    assert len(session.appels) == 1
    assert pauses == []


def test_connexion_impossible_trois_essais(tmp_path):
    session = FausseSession(*(requests.ConnectionError() for _ in range(3)))
    pauses = []
    with pytest.raises(requests.ConnectionError):
        telecharger_avec_essais(URL, tmp_path, session=session, attendre=pauses.append)
    assert len(session.appels) == 3
    assert pauses == [2.0, 4.0]


def test_ctrl_c_jamais_reessaye(tmp_path):
    session = FausseSession(KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        telecharger_avec_essais(URL, tmp_path, session=session, attendre=lambda s: None)
    assert len(session.appels) == 1


def test_zero_essai_refuse(tmp_path):
    with pytest.raises(ValueError):
        telecharger_avec_essais(URL, tmp_path, essais=0)
