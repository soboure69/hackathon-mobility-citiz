"""Application de restitution — Hackathon Epitech x Citiz, CA de La Rochelle.

Lancement, depuis la racine du dépôt :  streamlit run app/streamlit_app.py
Prérequis : python scripts/build_exports.py --territoire larochelle
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun  # noqa: E402

st.set_page_config(page_title="Mobilité La Rochelle", page_icon="🚗", layout="wide")

pages = [
    st.Page("vues/p1_synthese.py", url_path="synthese", title="1 · Synthèse", default=True),
    st.Page("vues/p2_couverture.py", url_path="couverture", title="2 · Couverture actuelle"),
    st.Page("vues/p3_candidats.py", url_path="candidats", title="3 · Candidats et score"),
    st.Page("vues/p4_budget.py", url_path="budget", title="4 · Optimisation budgétaire"),
    st.Page("vues/p5_methode.py", url_path="methode", title="5 · Méthode, qualité, limites"),
]
page = st.navigation(pages, position="top")

d = commun.donnees()
meta = d["meta_execution"]
with st.sidebar:
    st.markdown("**CA de La Rochelle** · 28 communes")
    derniere = pd.to_datetime(meta["date_execution_utc"], utc=True).max()
    if pd.notna(derniere):
        st.caption(f"Données Gold au {derniere:%d/%m/%Y %H:%M} UTC")
    st.toggle("Fond de carte (Internet)", value=True, key="fond_carte",
              help="Sans Internet, désactivez : la carte garde les carreaux, les communes et les stations.")
    st.caption("Score de potentiel ≠ prédiction de fréquentation. Coûts et budgets : hypothèses de simulation.")
page.run()
