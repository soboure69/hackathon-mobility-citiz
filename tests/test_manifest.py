"""Tests de src/utils/manifest.py.

Chaque test crée ses propres fichiers dans un dossier temporaire :
aucune donnée réelle n'est lue ni modifiée.
"""
from datetime import datetime, timedelta, timezone

import pytest

from src.utils.manifest import (
    CHAMPS_OBLIGATOIRES,
    calculer_sha256,
    construire_run_id,
    decrire_fichier,
    ecrire_manifeste,
    lire_manifeste,
    verifier_manifeste,
)

# Vecteur de référence publié pour SHA-256 : empreinte du texte « abc ».
SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def contenu_minimal(**valeurs):
    """Un contenu de manifeste avec les 15 champs, à None par défaut."""
    contenu = {champ: None for champ in CHAMPS_OBLIGATOIRES}
    contenu.update(valeurs)
    return contenu


@pytest.fixture
def dossier_bronze(tmp_path):
    """Un dossier daté factice : un fichier « abc » et son manifeste valide."""
    dossier = tmp_path / "S99_2026-10-21"
    dossier.mkdir()
    (dossier / "donnees.txt").write_bytes(b"abc")
    ecrire_manifeste(dossier, contenu_minimal(
        source_id="S99",
        statut_ingestion="reussie",
        fichiers=[decrire_fichier(dossier / "donnees.txt")],
    ))
    return dossier


def problemes(dossier):
    return [anomalie["probleme"] for anomalie in verifier_manifeste(dossier)]


# --- Étapes 1 et 2 : empreinte et description ---

def test_sha256_vecteur_de_reference(tmp_path):
    fichier = tmp_path / "abc.txt"
    fichier.write_bytes(b"abc")
    assert calculer_sha256(fichier) == SHA256_ABC


def test_sha256_fichier_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        calculer_sha256(tmp_path / "absent.bin")


def test_decrire_fichier(tmp_path):
    fichier = tmp_path / "abc.txt"
    fichier.write_bytes(b"abc")
    assert decrire_fichier(fichier) == {
        "nom": "abc.txt", "taille_octets": 3, "sha256": SHA256_ABC,
    }


def test_decrire_refuse_un_dossier(tmp_path):
    with pytest.raises(FileNotFoundError):
        decrire_fichier(tmp_path)


# --- Étape 3 : run_id ---

def test_run_id_deterministe():
    moment = datetime(2026, 10, 25, 0, 30, tzinfo=timezone.utc)
    assert construire_run_id(moment, "abc1234") == "20261025T003000Z_abc1234"


def test_run_id_convertit_en_utc():
    heure_ete_paris = timezone(timedelta(hours=2))
    moment = datetime(2026, 10, 21, 3, 0, tzinfo=heure_ete_paris)
    assert construire_run_id(moment, "abc1234") == "20261021T010000Z_abc1234"


def test_run_id_refuse_une_date_sans_fuseau():
    with pytest.raises(ValueError, match="fuseau"):
        construire_run_id(datetime(2026, 10, 21, 3, 0), "abc1234")


# --- Étapes 4 et 5 : écrire, lire, valider ---

def test_aller_retour(dossier_bronze):
    manifeste = lire_manifeste(dossier_bronze)
    assert manifeste["source_id"] == "S99"
    assert manifeste["fichiers"][0]["sha256"] == SHA256_ABC


def test_refus_ecrasement(dossier_bronze):
    with pytest.raises(FileExistsError):
        ecrire_manifeste(dossier_bronze, lire_manifeste(dossier_bronze))


def test_champ_manquant(tmp_path):
    with pytest.raises(ValueError, match="Champs manquants"):
        ecrire_manifeste(tmp_path, {"source_id": "S99", "statut_ingestion": "reussie"})


def test_statut_invalide(tmp_path):
    with pytest.raises(ValueError, match="statut_ingestion invalide"):
        ecrire_manifeste(tmp_path, contenu_minimal(statut_ingestion="reussi", fichiers=[]))


def test_fichiers_vide_accepte_si_echec(tmp_path):
    ecrire_manifeste(tmp_path, contenu_minimal(statut_ingestion="echouee", fichiers=[]))
    assert lire_manifeste(tmp_path)["statut_ingestion"] == "echouee"


def test_fichiers_vide_refuse_si_reussie(tmp_path):
    with pytest.raises(ValueError, match="vide"):
        ecrire_manifeste(tmp_path, contenu_minimal(statut_ingestion="reussie", fichiers=[]))


def test_lecture_json_casse(tmp_path):
    (tmp_path / "_manifest.json").write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ValueError):  # JSONDecodeError est une sous-classe de ValueError
        lire_manifeste(tmp_path)


# --- Étape 6 : vérifier ---

def test_verifier_conforme(dossier_bronze):
    assert verifier_manifeste(dossier_bronze) == []


def test_verifier_taille(dossier_bronze):
    (dossier_bronze / "donnees.txt").write_bytes(b"abcd")
    assert problemes(dossier_bronze) == ["taille"]


def test_verifier_meme_taille_contenu_different(dossier_bronze):
    (dossier_bronze / "donnees.txt").write_bytes(b"abd")
    assert problemes(dossier_bronze) == ["sha256"]


def test_verifier_fichier_non_liste(dossier_bronze):
    (dossier_bronze / "intrus.txt").write_text("x", encoding="utf-8")
    assert problemes(dossier_bronze) == ["non_liste"]


def test_verifier_fichier_absent(dossier_bronze):
    (dossier_bronze / "donnees.txt").unlink()
    assert problemes(dossier_bronze) == ["absent"]


def test_verifier_accepte_une_empreinte_en_majuscules(tmp_path):
    """Cas d'un manifeste écrit à la main à partir de Get-FileHash."""
    (tmp_path / "donnees.txt").write_bytes(b"abc")
    description = decrire_fichier(tmp_path / "donnees.txt")
    description["sha256"] = description["sha256"].upper()
    ecrire_manifeste(tmp_path, contenu_minimal(statut_ingestion="reussie", fichiers=[description]))
    assert verifier_manifeste(tmp_path) == []
