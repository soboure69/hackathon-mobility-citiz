"""Tests des KPI d'accessibilité : comptage des modes, exclusivité, agrégations, K6."""
import pandas as pd
import pytest

from src.features import kpi_acces as k


def jeu():
    cellules = pd.DataFrame({
        "cell_id": ["a", "b", "c", "d"], "pop": [100.0, 50.0, 30.0, 20.0],
        "commune_insee": ["17001", "17001", "17002", "17002"], "epci_siren": ["111111111"] * 4,
        "ind": [100.0, 50.0, 30.0, 20.0], "ind_snv": [1_000_000.0, 1_500_000.0, 900_000.0, 800_000.0],
    })
    paires = pd.DataFrame({
        "cell_id":  ["a",   "a",   "a",     "b",   "c",    "d"],
        "offre_id": ["b1",  "b2",  "c1",    "b1",  "v1",   "b1"],
        "mode":     ["bus", "bus", "citiz", "bus", "velo", "bus"],
        "methode":  ["reseau"] * 5 + ["vol_oiseau"],
        "variante": ["reference"] * 6,
        "dist_totale_m": [100.0, 50.0, 300.0, 200.0, 350.0, 390.0],
    })
    offres = pd.DataFrame({"offre_id": ["b1", "b2", "c1", "v1", "v9"], "mode": ["bus", "bus", "citiz", "velo", "velo"]})
    return cellules, paires, offres


def test_modes_comptes_une_fois():
    cellules, paires, _ = jeu()
    acces = k.acces_cellule(cellules, paires).set_index("cell_id")
    assert acces.loc["a", "n_options_bus"] == 2 and acces.loc["a", "n_modes"] == 2   # 2 bus = 1 mode
    assert acces.loc["a", "n_options_total"] == 3
    assert float(acces.loc["a", "dist_min_bus_m"]) == 50.0
    assert not acces.loc["d", "desservi"]                    # sa seule paire est à vol d'oiseau


def test_exclusif_somme_egale_couverture():
    cellules, paires, offres = jeu()
    desserte = k.desserte_offre(offres, cellules, paires).set_index("offre_id")
    assert float(desserte.loc["b1", "pop_5min"]) == 150.0      # a et b : non exclusif
    assert float(desserte.loc["b2", "pop_exclusive"]) == 100.0  # a va à b2 (50 m < 100 m)
    assert float(desserte.loc["b1", "pop_exclusive"]) == 50.0
    assert float(desserte.loc[desserte["mode"] == "bus", "pop_exclusive"].sum()) == 150.0
    assert not desserte.loc["v9", "atteinte"]


def test_communes_redonnent_l_epci():
    cellules, paires, _ = jeu()
    couverture = k.couverture(k.acces_cellule(cellules, paires), {"epci": "epci_siren", "commune": "commune_insee"})
    tous = couverture[couverture["mode"] == "tous"]
    epci = tous[tous["perimetre_type"] == "epci"].iloc[0]
    communes = tous[tous["perimetre_type"] == "commune"]
    assert float(communes["pop_desservie"].sum()) == float(epci["pop_desservie"]) == 180.0
    assert float(epci["pop_non_desservie"]) == 20.0
    assert float(epci["pop_au_moins_2_modes"]) == 100.0


def test_population_nouvellement_couverte():
    cellules, paires, _ = jeu()
    acces = k.acces_cellule(cellules, paires)
    assert k.population_nouvellement_couverte(acces, {"a", "d"}) == 20.0          # a déjà desservi
    assert k.population_nouvellement_couverte(acces, {"a", "b"}, mode="citiz") == 50.0


def test_quintile_pondere_par_la_population():
    valeur = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    poids = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0])
    assert list(k.quintile_pondere(valeur, poids)) == [1, 2, 3, 4, 5]


def test_paires_en_double_refusees():
    cellules, paires, _ = jeu()
    with pytest.raises(RuntimeError, match="double"):
        k.acces_cellule(cellules, pd.concat([paires, paires.iloc[[0]]]))
