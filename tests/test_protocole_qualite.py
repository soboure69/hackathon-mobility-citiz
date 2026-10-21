"""Tests du protocole qualité : statuts, dates, couverture de mobilité sans double compte."""
from datetime import date

import pandas as pd
import pytest

from src.evaluation import protocole_qualite as pq


@pytest.mark.parametrize("valeur, regle, attendu", [
    (0.96, {"sens": ">=", "seuil": 0.95}, "ok"),
    (0.90, {"sens": ">=", "seuil": 0.95}, "alerte"),
    (126, {"sens": "<=", "seuil": 30}, "alerte"),
    (0.954, {"sens": "intervalle", "seuil": [0.85, 1.05]}, "ok"),
    (3, {"sens": "info"}, "info"),
    (None, {"sens": ">=", "seuil": 1}, "info"),
])
def test_statut(valeur, regle, attendu):
    assert pq.statut(valeur, regle) == attendu


@pytest.mark.parametrize("valeur, jour", [
    ("20270103", date(2027, 1, 3)),                                  # GTFS
    ("2026-10-21T04:04:01.2783437+02:00", date(2026, 10, 21)),       # GBFS v3, 7 décimales
    ("2026-06-17T11:12:55+02:00", date(2026, 6, 17)),
    (1781000000, date(2026, 6, 9)),                                  # GBFS v2, POSIX
])
def test_lire_jour(valeur, jour):
    assert pq.lire_jour(valeur) == jour


def test_jours_depuis_signe():
    assert pq.jours_depuis("2026-06-17", date(2026, 10, 21)) == 126
    assert -pq.jours_depuis("20270103", date(2026, 10, 21)) == 74     # validité restante


def test_couverture_mobilite_compte_chaque_carreau_une_fois():
    cellules = pd.DataFrame({"cell_id": ["a", "b", "c"], "pop": [100.0, 50.0, 25.0]})
    paires = pd.DataFrame({
        "cell_id": ["a", "a", "a", "b", "c"],
        "offre_id": ["o1", "o2", "o3", "o1", "o9"],
        "mode": ["bus", "bus", "velo", "bus", "bus"],
        "methode": ["reseau"] * 4 + ["vol_oiseau"],
        "variante": ["reference"] * 5,
    })
    desservie, totale, taux = pq.couverture_mobilite(cellules, paires)
    assert (desservie, totale) == (150.0, 175.0)          # « a » a 3 options mais compte une fois ; « c » vol d'oiseau exclu
    assert taux == pytest.approx(150 / 175)
    assert pq.couverture_mobilite(cellules, paires, "velo")[0] == 100.0


def test_releve_calcule_le_statut_avec_le_seuil():
    releve = pq.Releve({"X": {"sens": ">=", "seuil": 0.5}}, date(2026, 10, 21), "R")
    releve.ajouter("X:S01", "complétude", "qualite", "S01", "t", "l", "f", 0.4, "part")
    table = releve.table()
    assert table.loc[0, "statut"] == "alerte" and table.loc[0, "seuil"] == "0.5"
