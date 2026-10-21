"""Fumée : chaque page de l'application s'exécute sans exception sur les exports réels (si présents)."""
from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")
RACINE = Path(__file__).resolve().parents[1]
EXPORTS = RACINE / "data" / "gold" / "exports" / "dim_scenario_larochelle.parquet"
PAGES = ["p1_synthese", "p2_couverture", "p3_candidats", "p4_budget", "p5_methode"]


@pytest.mark.skipif(not EXPORTS.exists(), reason="exports absents : lancer scripts/build_exports.py")
@pytest.mark.parametrize("page", PAGES)
def test_page_sans_erreur(page):
    at = st_testing.AppTest.from_file(str(RACINE / "app" / "vues" / f"{page}.py"), default_timeout=60)
    at.run()
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.skipif(not EXPORTS.exists(), reason="exports absents")
def test_page4_equite_hors_cout_central_affiche_un_message():
    at = st_testing.AppTest.from_file(str(RACINE / "app" / "vues" / "p4_budget.py"), default_timeout=60)
    at.session_state["cout_p4"] = "bas"
    at.session_state["variante_p4"] = "equite"
    at.run()
    assert not at.exception
    assert any("coût central" in w.value for w in at.warning)


@pytest.mark.skipif(not EXPORTS.exists(), reason="exports absents")
def test_application_complete():
    at = st_testing.AppTest.from_file(str(RACINE / "app" / "streamlit_app.py"), default_timeout=60)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
