"""Tests du bloc Silver S-3 (Admin Express, Filosofi), sur des tables construites par le test."""
import geopandas as gpd
import pytest
from shapely.geometry import box

from src.cleaning import admin, filosofi
from src.cleaning.audit import Suivi

TERRITOIRES = {"ville": {"siren": "111111111", "nb_communes": 2, "role": "decision"}}
AUDIT = {"source_id": "S99", "fichier_origine": "f", "sha256_origine": "h", "date_donnee": "d", "run_id": "RUN"}


def communes_brutes():
    return gpd.GeoDataFrame({
        "code_insee": ["17001", "17002", "17003"],
        "nom_officiel": ["A", "B", "Hors EPCI"],
        "codes_siren_des_epci": ["111111111", "200000000/111111111", "NR"],
        "population": [100, 200, 50],
        "code_insee_du_departement": ["17", "17", "17"],
        "code_insee_de_la_region": ["75", "75", "75"],
    }, geometry=[box(0, 0, 1000, 1000), box(1000, 0, 2000, 1000), box(2000, 0, 3000, 1000)], crs=2154)


def epci_brut(liste="17001, 17002"):
    return gpd.GeoDataFrame({"code_siren": ["111111111"], "nom_officiel": ["CA Ville"], "nature": ["CA"],
                             "codes_insee_des_communes_membres": [liste]},
                            geometry=[box(0, 0, 2000, 1000)], crs=2154)


def test_membres_par_siren_quel_que_soit_le_separateur():
    communes, epci = admin.standardiser_admin(communes_brutes(), epci_brut(), TERRITOIRES, **AUDIT)
    assert sorted(communes["code_insee"]) == ["17001", "17002"]      # « 200000000/111111111 » reconnu, « NR » écarté
    assert set(communes["territoire"]) == {"ville"}
    assert admin.controler_composition(communes, epci, TERRITOIRES)[0]["communes"] == 2


def test_composition_contraire_a_g2_bloque():
    communes, epci = admin.standardiser_admin(communes_brutes(), epci_brut("17001"), TERRITOIRES, **AUDIT)
    with pytest.raises(RuntimeError, match="RC-12"):
        admin.controler_composition(communes, epci, TERRITOIRES)


def carreaux_bruts():
    carre = [box(0, 0, 200, 200), box(200, 0, 400, 200), box(400, 0, 600, 200), box(600, 0, 800, 200),
             box(0, 200, 100, 300), box(800, 0, 1000, 200)]
    return gpd.GeoDataFrame({
        "idcar_200m": ["C1", "C2", "C3", "C3", "C5", "C6"],
        "idcar_nat": ["N1", "N1", "N2", "N2", "N3", "N4"],
        "lcog_geo": ["17001", "17003,17002", "17002", "17001", "17002", "17009"],
        "ind": [10.0, 5.5, 3.0, 2.0, 1.0, 4.0],
        "i_est_200": [0, 1, 0, 0, 1, 0],
    }, geometry=carre, crs=2154)


def test_rf01_et_attributs():
    communes, _ = admin.standardiser_admin(communes_brutes(), epci_brut(), TERRITOIRES, **AUDIT)
    std = filosofi.standardiser_carreaux(carreaux_bruts(), communes, ",", **AUDIT).set_index("idcar_200m")
    assert "C6" not in std.index                                          # carreau hors EPCI (17009) écarté par RF-01
    c2 = std.loc["C2"]
    assert (c2["commune_insee"], c2["commune_principale"]) == ("17002", "17003")  # premier code MEMBRE
    assert bool(c2["multi_commune"]) and bool(c2["partiel_epci"]) and bool(c2["est_impute"])
    assert std.loc["C1", "cell_id"] == "C1"                              # clé = idcar_200m, pas idcar_nat


def test_doublon_rejete_et_aire_signalee():
    communes, _ = admin.standardiser_admin(communes_brutes(), epci_brut(), TERRITOIRES, **AUDIT)
    std = filosofi.standardiser_carreaux(carreaux_bruts(), communes, ",", **AUDIT)
    suivi = Suivi("RUN")
    propre = filosofi.nettoyer_carreaux(std, suivi, 0.01)
    journal = suivi.table()
    assert sorted(journal.loc[journal["regle_id"] == "RC-10", "id_origine"]) == ["C3", "C3"]  # les deux lignes rejetées
    assert list(journal.loc[journal["regle_id"] == "RC-09", "id_origine"]) == ["C5"]     # 100 m × 100 m
    assert "C3" not in set(propre["cell_id"])
