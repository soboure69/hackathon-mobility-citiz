"""Éléments partagés de l'application : chargement des exports, couleurs, formats, cartes.

L'application lit SEULEMENT data/gold/exports/ (AD3). Elle ne recalcule aucun KPI :
les mesures sont dans src/export/mesures.py, testées par pytest.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from src.export import mesures as m  # noqa: E402,F401  (réexporté pour les pages)

EXPORTS = RACINE / "data" / "gold" / "exports"
TERRITOIRE = "larochelle"

# Convention de couleurs (powerbi/conception_rapport.md § 6) : Okabe-Ito, jamais la couleur seule.
C = {
    "couvert": "#0072B2", "manque": "#D55E00", "propose": "#009E73", "equite": "#CC79A7",
    "neutre": "#6E6E6E", "texte": "#1A1A1A", "prioritaire_trait": "#6A3D9A",
    "texte_manque": "#A6411A", "texte_propose": "#007A5A", "texte_equite": "#B2186F",
}
MODES = {"Tous modes": "tous", "Bus": "bus", "Citiz": "citiz", "Vélo": "velo"}
COULEURS_MODE = {"tous": "#1A1A1A", "bus": "#6E6E6E", "citiz": "#0072B2", "velo": "#CC79A7"}
SEQUENTIEL = ["#EFF3FF", "#BDD7E7", "#6BAED6", "#3182BD", "#08519C"]
CLASSES_SCORE = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"]
VUE = pdk.ViewState(latitude=46.13, longitude=-1.07, zoom=9.6, pitch=0)            # agglomération entière
VUE_VILLE = pdk.ViewState(latitude=46.158, longitude=-1.15, zoom=11.6, pitch=0)    # stations Citiz (La Rochelle)


def rgb(hex_: str, alpha: int = 255) -> list[int]:
    h = hex_.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [alpha]


# ---------- Formats français ----------
def ent(x: float) -> str:
    return "—" if pd.isna(x) else f"{x:,.0f}".replace(",", " ")


def pct(x: float, d: int = 1) -> str:
    return "—" if pd.isna(x) else f"{100 * x:.{d}f}".replace(".", ",") + " %"


def eur(x: float, d: int = 0) -> str:
    return "—" if pd.isna(x) else f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " €"


def pts(x: float) -> str:
    return "—" if pd.isna(x) else f"{x:+.1f}".replace(".", ",") + " pt"


# ---------- Données ----------
@st.cache_data(show_spinner="Lecture des exports…")
def charger() -> dict[str, pd.DataFrame]:
    tables = {}
    for f in sorted(EXPORTS.glob(f"*_{TERRITOIRE}.parquet")):
        tables[f.name.removesuffix(f"_{TERRITOIRE}.parquet")] = pd.read_parquet(f)
    if not tables:
        st.error("Aucun export trouvé. Lancez d'abord : python scripts/build_exports.py --territoire larochelle")
        st.stop()
    return tables


@st.cache_data
def geojson(nom: str) -> dict:
    return json.loads((EXPORTS / f"{nom}_{TERRITOIRE}.geojson").read_text(encoding="utf-8"))


def donnees() -> dict[str, pd.DataFrame]:
    return charger()


# ---------- Mise en page ----------
def titre(question: str, reponse: str) -> None:
    """Une page = une question ; le titre est la réponse (principe 1)."""
    st.caption(question)
    st.subheader(reponse)


def etiquette(texte: str) -> str:
    return f":orange-background[{texte}]"


def fond_de_carte() -> bool:
    return st.session_state.get("fond_carte", True)


def carte(couches: list[pdk.Layer], infobulle: dict | None = None, hauteur: int = 460, vue: pdk.ViewState = VUE) -> None:
    fond = fond_de_carte()
    deck = pdk.Deck(layers=couches, initial_view_state=vue, tooltip=infobulle,
                    map_provider="carto" if fond else None,
                    map_style=pdk.map_styles.CARTO_LIGHT if fond else None)
    st.pydeck_chart(deck, height=hauteur)


def couche_communes(prioritaires_seulement: bool = False) -> pdk.Layer:
    g = geojson("communes")
    if prioritaires_seulement:
        g = {**g, "features": [f for f in g["features"] if f["properties"]["prioritaire"]]}
    for f in g["features"]:
        p = f["properties"]
        p["trait"] = rgb(C["prioritaire_trait"]) if p["prioritaire"] else rgb(C["neutre"], 160)
        p["epaisseur"] = 90 if p["prioritaire"] else 15   # mètres ; pydeck lit une chaîne comme une expression, d'où pas de *_units
        p["statut"] = "commune prioritaire" if p["prioritaire"] else "commune"
    return pdk.Layer("GeoJsonLayer", g, stroked=True, filled=False, get_line_color="properties.trait",
                     get_line_width="properties.epaisseur", line_width_min_pixels=1, pickable=False)


def legende(elements: list[tuple[str, str]]) -> None:
    """Légende texte : la couleur est toujours doublée d'un libellé."""
    st.markdown(" &nbsp; ".join(f"<span style='color:{c};font-size:1.2em'>●</span> {t}" for c, t in elements),
                unsafe_allow_html=True)


def filtre_communes(d: dict[str, pd.DataFrame], cle: str = "communes") -> list[str]:
    """Segment commune partagé entre les pages (même clé de session)."""
    communes = d["dim_commune"].sort_values("nom")
    noms = st.multiselect("Communes", communes["nom"].tolist(), key=cle, placeholder="Toutes les communes")
    return communes.loc[communes["nom"].isin(noms), "commune_insee"].tolist()


def nom_commune(d: dict[str, pd.DataFrame]) -> dict[str, str]:
    return dict(zip(d["dim_commune"]["commune_insee"], d["dim_commune"]["nom"]))
