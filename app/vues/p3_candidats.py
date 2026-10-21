"""Page 3 — Zones candidates : quels sites ont du potentiel, pourquoi, et le classement est-il robuste."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import altair as alt  # noqa: E402
import pydeck as pdk  # noqa: E402
import streamlit as st  # noqa: E402

from commun import (C, CLASSES_SCORE, SEQUENTIEL, carte, couche_communes, donnees, ent, eur, filtre_communes,  # noqa: E402
                    legende, nom_commune, pct, rgb, titre)

d = donnees()
cand = d["dim_candidat"].copy()
noms = nom_commune(d)
cand["commune"] = cand["commune_insee"].map(noms)
titre("Quels sites ont le plus de potentiel, et pourquoi ?",
      f"{ent(len(cand))} sites Citiz possibles, classés par un score de potentiel — pas une prédiction")
st.warning("Le score (sur 100) **classe** des sites selon cinq critères. Il ne prédit pas une fréquentation : "
           "aucun historique d'usage n'est disponible. La sélection finale se fait en page 4.", icon="ℹ️")

f1, f2, f3 = st.columns([3, 1, 2])
with f1:
    communes = filtre_communes(d, cle="communes")
with f2:
    seul_prio = st.toggle("Communes prioritaires seulement", key="prio_p3")
with f3:
    bornes = st.slider("Score", 0, 100, (0, 100), key="score_p3")
vue = cand[cand["score"].between(*bornes)]
if communes:
    vue = vue[vue["commune_insee"].isin(communes)]
if seul_prio:
    vue = vue[vue["commune_prioritaire"]]
vue = vue.sort_values("rang")

st.markdown("**Sites** — cliquez sur une ligne pour voir la décomposition de son score")
choix = st.dataframe(
    vue[["rang", "commune", "score", "pop_nouvelle_isolee", "taux_redondance", "frequence_top_n", "candidat_id"]],
    hide_index=True, height=220, on_select="rerun", selection_mode="single-row", key="table_p3",
    column_config={"rang": st.column_config.NumberColumn("Rang", width="small"), "commune": "Commune",
                   "score": st.column_config.ProgressColumn("Score", format="%.0f", min_value=0, max_value=100),
                   "pop_nouvelle_isolee": st.column_config.NumberColumn("Habitants gagnés (site seul)", format="%d"),
                   "taux_redondance": st.column_config.NumberColumn("Redondance", format="percent"),
                   "frequence_top_n": st.column_config.NumberColumn("Stabilité top 20", format="percent",
                                                                    help="Part des 500 tirages de pondérations où le site reste dans le top 20."),
                   "candidat_id": None})
lignes = choix.selection.rows if choix and choix.selection else []
site = vue.iloc[lignes[0]] if lignes else vue.iloc[0] if len(vue) else None

cout_central = float(d["dim_scenario"].query("hypothese_cout == 'central'")["cout_station"].iloc[0])
k = st.columns(4)
k[0].metric("Sites affichés", ent(len(vue)), border=True)
k[1].metric("Score du site", "—" if site is None else f"{site['score']:.0f} / 100", border=True,
            help="Site sélectionné dans le tableau (par défaut : le mieux classé).")
k[2].metric("Habitants gagnés (site seul)", "—" if site is None else ent(site["pop_nouvelle_isolee"]), border=True,
            help="Si ce site était le seul ajouté. Ne s'additionne pas entre sites : leurs zones se chevauchent.")
k[3].metric("Coût par habitant (site seul)", "—" if site is None or not site["pop_nouvelle_isolee"]
            else eur(cout_central / site["pop_nouvelle_isolee"], 2), border=True,
            help=f"Au coût central de {eur(cout_central)} par station (hypothèse de simulation).")

gauche, droite = st.columns([3, 2])
with gauche:
    palette = dict(zip(CLASSES_SCORE, SEQUENTIEL))
    pts = vue.assign(couleur=vue["classe_score"].map(lambda c: rgb(palette.get(c, C["neutre"]), 220)))
    couches = [couche_communes(), pdk.Layer("ScatterplotLayer", pts, get_position="[lon, lat]", get_fill_color="couleur",
                                            get_radius=45, radius_min_pixels=2, pickable=True)]
    if site is not None:
        couches.append(pdk.Layer("ScatterplotLayer", site.to_frame().T[["lon", "lat"]].astype(float),
                                 get_position="[lon, lat]", get_fill_color=rgb(C["propose"]), get_radius=160,
                                 stroked=True, get_line_color=[255, 255, 255], line_width_min_pixels=2))
    carte(couches, {"text": "Rang {rang} · score {score}\n{commune}"})
    legende([(SEQUENTIEL[0], "score très faible"), (SEQUENTIEL[2], "moyen"), (SEQUENTIEL[4], "très fort"),
             (C["propose"], "site sélectionné")])
with droite:
    if site is not None:
        st.markdown(f"**Pourquoi ce score ?** Rang {site['rang']} · {site['commune']}")
        contrib = d["fact_contribution"].query("candidat_id == @site.candidat_id")
        st.altair_chart(alt.Chart(contrib).mark_bar(color=C["couvert"]).encode(
            x=alt.X("contribution:Q", title="Points de score"), y=alt.Y("libelle_critere:N", sort=None, title=None),
            tooltip=[alt.Tooltip("valeur_normalisee:Q", format=".2f", title="Valeur normalisée (0-1)"),
                     alt.Tooltip("contribution:Q", format=".1f", title="Contribution")]), height=200)
    st.markdown("**Impact et redondance**: en haut à gauche, les meilleurs sites")
    st.altair_chart(alt.Chart(vue).mark_circle(opacity=0.5).encode(
        x=alt.X("taux_redondance:Q", title="Redondance avec l'offre Citiz existante", axis=alt.Axis(format="%")),
        y=alt.Y("pop_nouvelle_isolee:Q", title="Habitants gagnés (site seul)"),
        color=alt.Color("commune_prioritaire:N", title="Commune prioritaire",
                        scale=alt.Scale(domain=[True, False], range=[C["equite"], C["couvert"]])),
        tooltip=["rang:Q", "commune:N", alt.Tooltip("score:Q", format=".0f")]), height=230)

b1, b2 = st.columns([3, 2])
with b1:
    st.markdown("**Top 20 : composition du score**")
    top = vue.nsmallest(20, "rang")[["candidat_id", "rang", "commune"]]
    t = d["fact_contribution"].merge(top, on="candidat_id")
    t["site"] = t["rang"].astype(str) + " · " + t["commune"].fillna("")
    st.altair_chart(alt.Chart(t).mark_bar().encode(
        y=alt.Y("site:N", sort=alt.EncodingSortField("rang", order="ascending"), title=None),
        x=alt.X("contribution:Q", title="Score (somme des contributions)"),
        color=alt.Color("libelle_critere:N", title="Critère",
                        scale=alt.Scale(range=[C["couvert"], C["manque"], C["neutre"], C["equite"], C["propose"]])),
        order="ordre:Q"), height=380)
with b2:
    st.markdown("**Sensibilité aux pondérations** (une pondération ×0,5 ou ×1,5)")
    s = d["fact_sensibilite"]
    st.dataframe(s, hide_index=True, column_config={
        "variable": "Critère", "facteur": st.column_config.NumberColumn("Facteur", format="×%.1f"),
        "spearman": st.column_config.NumberColumn("Spearman (ordre global)", format="%.3f"),
        "recouvrement_top_n": st.column_config.NumberColumn("Top 20 commun", format="percent"),
        "run_id": None})
    st.caption(f"L'ordre d'ensemble est stable (Spearman ≥ {s['spearman'].min():.3f}). Le top 20 l'est moins "
               f"({pct(s['recouvrement_top_n'].min(), 0)} à {pct(s['recouvrement_top_n'].max(), 0)} de sites communs) : "
               "les meilleurs scores sont très proches. Le score départage ; c'est l'optimisation qui choisit.")
