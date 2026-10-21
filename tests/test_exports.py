"""Exports de restitution et mesures de l'application, sur petits cas fabriqués."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from src.export import exports as ex
from src.export import mesures as m


def acces_fabrique():
    geoms = [box(380000, 6570000, 380200, 6570200), box(380200, 6570000, 380400, 6570200)]
    return gpd.GeoDataFrame({
        "cell_id": ["a", "b"], "commune_insee": ["17300", "17001"], "pop": [100.0, 50.0], "classe_acces": ["3-5", "0"],
        "n_options_total": [3, 0], "desservi": [True, False], "dist_min_m": [120.0, float("nan")],
        "n_options_bus": [2, 0], "dist_min_bus_m": [150.0, float("nan")], "desservi_bus": [True, False],
        "n_options_citiz": [1, 0], "dist_min_citiz_m": [120.0, float("nan")], "desservi_citiz": [True, False],
        "n_options_velo": [0, 0], "dist_min_velo_m": [float("nan")] * 2, "desservi_velo": [False, False],
        "quintile_niveau_vie": [1, 5], "niveau_vie_moyen": [15000.0, 30000.0], "est_impute": [False, True],
    }, geometry=geoms, crs=2154)


def test_depivot_acces_un_carreau_par_mode_et_wgs84():
    f = ex.fact_acces_mode(acces_fabrique())
    assert len(f) == 8 and set(f["mode"]) == {"tous", "bus", "citiz", "velo"}
    tous = f[f["mode"] == "tous"].set_index("cell_id")
    assert tous.loc["a", "n_options"] == 3 and not tous.loc["b", "desservi"]
    assert f["lat"].between(45, 47).all() and f["lon"].between(-2, 0).all()      # La Rochelle, pas des mètres


def test_couverture_un_mode_et_population_sans_option():
    a = acces_fabrique()
    f, c = ex.fact_acces_mode(a), ex.dim_cellule(a, {"17001"})
    k = m.couverture(f, c, "citiz")
    assert k["pop_desservie"] == 100 and k["taux"] == pytest.approx(100 / 150)
    assert k["options_par_habitant"] == pytest.approx(100 / 150)
    assert m.couverture(f, c, "tous", communes=["17001"])["taux"] == 0
    assert m.pop_sans_option(c) == 50
    with pytest.raises(ValueError):
        m.couverture(f, c, "train")


def test_scenario_absent_renvoie_none_et_variante_equite():
    sc = pd.DataFrame({"scenario_id": ["A", "A_eq", "B"], "scenario": ["central"] * 3, "hypothese_cout": ["central", "central", "bas"],
                       "variante": ["efficacite", "equite", "efficacite"], "scenario_reference": [None, "A", None],
                       "est_reference": [True, False, False]})
    assert m.scenario(sc, "central", "bas", "equite") is None
    assert m.scenario(sc, "central", "central", "equite")["scenario_id"] == "A_eq"
    assert m.variante_equite(sc, m.reference(sc))["scenario_id"] == "A_eq"


def test_part_conformes_exclut_les_indicateurs_info():
    q = pd.DataFrame({"statut": ["ok", "ok", "ok", "alerte", "info", "info"]})
    assert m.part_conformes(q) == 0.75


def test_risques_lus_dans_le_markdown_et_risques_clos():
    md = ("| ID | Risque | P | I | M | R |\n|---|---|---|---|---|---|\n"
          "| R1 | Périmètre trop large | Élevée | Critique | Porte G2 | Porteur |\n"
          "| R25 | run_id sans -modifie | Écartée | Moyen | Clos le 21/10 | Porteur |\n"
          "| R26 | Tags absents | Certaine | Faible | Option B, risque clos sans réingestion | Porteur |\n")
    r = ex.ref_risques(md).set_index("risque_id")
    assert list(r.index) == ["R1", "R25", "R26"] and r.loc["R1", "ouvert"] and not r.loc["R25", "ouvert"] and not r.loc["R26", "ouvert"]


def test_meta_execution_lit_date_commit_et_modifie():
    meta = ex.meta_execution({"optimization": {"tables": {"t.parquet": {"run_id": "20261021T084710Z_5c8ceff"},
                                                          "u.parquet": {"run_id": "20261021T084710Z_5c8ceff-modifie"}}}})
    assert list(meta["commit"]) == ["5c8ceff", "5c8ceff"] and list(meta["modifie"]) == [False, True]
    assert meta["date_execution_utc"].iloc[0] == pd.Timestamp("2026-10-21 08:47:10", tz="UTC")


def test_hypotheses_refusent_une_nature_inconnue():
    h = {"hypothese_id": "H-1", "theme": "t", "texte": "x", "valeur": "1", "document": "d"}
    assert len(ex.ref_hypotheses([{**h, "nature": "estimé"}])) == 1
    with pytest.raises(ValueError):
        ex.ref_hypotheses([{**h, "nature": "probable"}])


def test_carte_repete_l_existant_dans_chaque_scenario():
    offre = pd.DataFrame({"offre_id": ["o1"], "mode": ["citiz"], "nom": ["Gare"], "lat": [46.15], "lon": [-1.14], "pop_5min": [900.0]})
    sel = pd.DataFrame({"scenario_id": ["S1"], "candidat_id": ["c1"], "ordre_ajout": [1], "pop_nouvelle_marginale": [400.0],
                        "lat": [46.16], "lon": [-1.15]})
    carte = ex.fact_carte_scenario(sel, offre, ["S1", "S2"], "citiz")
    assert len(carte) == 3 and (carte["type_point"] == "Citiz existante").sum() == 2
    assert not carte.duplicated(["scenario_id", "point_id"]).any()
