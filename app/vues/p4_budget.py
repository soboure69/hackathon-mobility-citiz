"""Page 4 — Optimisation budgétaire : quel portefeuille financer, avec quel impact, et que coûte l'équité."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import altair as alt  # noqa: E402
import pydeck as pdk  # noqa: E402
import streamlit as st  # noqa: E402

from commun import ESPACE_MILLIERS, VUE_VILLE, C, carte, couche_communes, donnees, ent, etiquette, eur, legende, m, nom_commune, pct, pts, rgb, titre  # noqa: E402

d = donnees()
sc = d["dim_scenario"]
noms = nom_commune(d)
budgets = sc.sort_values("ordre_budget").drop_duplicates("scenario")
couts = sc.sort_values("cout_station").drop_duplicates("hypothese_cout")

f = st.columns(3)
budget = f[0].segmented_control("Budget sur 3 ans", budgets["scenario"].tolist(), default="central", required=True,
                                format_func=lambda s: eur(budgets.set_index("scenario").loc[s, "budget"]), key="budget_p4")
cout = f[1].segmented_control("Coût par station", couts["hypothese_cout"].tolist(), default="central", required=True,
                              format_func=lambda h: eur(couts.set_index("hypothese_cout").loc[h, "cout_station"]), key="cout_p4")
variante = f[2].segmented_control("Variante", ["efficacite", "equite"], default="efficacite", required=True,
                                  format_func={"efficacite": "Efficacité", "equite": "Équité (≥ 30 % prioritaires)"}.get,
                                  key="variante_p4")
s = m.scenario(sc, budget, cout, variante)
if s is None:
    central = eur(couts.set_index("hypothese_cout").loc["central", "cout_station"])
    st.warning(f"La variante équité n'est calculée qu'au coût central ({central} par station). Choisissez ce coût.")
    st.stop()

titre("Pour ce budget, quelles stations financer ?",
      f"{s['n_stations']} stations, {ent(s['k6'])} habitants nouvellement couverts, {eur(s['k8'], 2)} par habitant")
st.markdown(f"{s['libelle']} · coût {etiquette(s['cout_etiquette'])} · budget {etiquette('hypothèse de simulation')} · "
            f"optimum prouvé à {pct(s['ecart_relatif_garanti'])} près")

k = st.columns(5)
k[0].metric("Stations financées", s["n_stations"], border=True,
            help=f"Budget non utilisé : {eur(s['budget'] - s['k7'])}")
k[1].metric("Habitants nouvellement couverts", ent(s["k6"]), border=True, help="Chaque habitant compté une seule fois.")
k[2].metric("Coût par habitant gagné", eur(s["k8"], 2), border=True)
k[3].metric("Couverture Citiz", pct(s["couverture_citiz_apres"]),
            delta=pts(m.gain_points(s["couverture_citiz_avant"], s["couverture_citiz_apres"])), border=True)
k[4].metric("Gains en communes prioritaires", pct(s["k12_part_prioritaire"]), border=True,
            help=f"{ent(s['pop_gagnee_prioritaire'])} habitants nouvellement couverts dans les communes prioritaires.")

gauche, droite = st.columns([3, 2])
sel = d["fact_selection"].query("scenario_id == @s.scenario_id").sort_values("ordre_ajout")
sel = sel.assign(commune=sel["commune_insee"].map(noms))
with droite:
    st.markdown("**Portefeuille, par ordre d'apport** — cliquez sur une station pour la repérer")
    choix = st.dataframe(sel[["ordre_ajout", "commune", "score", "pop_nouvelle_marginale", "pop_nouvelle_cumulee", "cout_cumule"]],
                         hide_index=True, height=230, on_select="rerun", selection_mode="single-row", key="table_p4",
                         column_config={"ordre_ajout": st.column_config.NumberColumn("#", width="small"), "commune": "Commune",
                                        "score": st.column_config.NumberColumn("Score", format="%.0f"),
                                        "pop_nouvelle_marginale": st.column_config.NumberColumn("+ habitants", format="%d"),
                                        "pop_nouvelle_cumulee": st.column_config.NumberColumn("Cumul", format="%d"),
                                        "cout_cumule": st.column_config.NumberColumn("Coût cumulé (€)", format="%d")})
    lignes = choix.selection.rows if choix and choix.selection else []
    st.markdown("**Rendements décroissants du portefeuille**")
    st.altair_chart(alt.Chart(sel).mark_line(interpolate="step-after", color=C["propose"], point=True).encode(
        x=alt.X("ordre_ajout:Q", title="Stations ajoutées", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("pop_nouvelle_cumulee:Q", title="Habitants (cumul)", axis=alt.Axis(labelExpr=ESPACE_MILLIERS)),
        tooltip=["commune:N", alt.Tooltip("pop_nouvelle_marginale:Q", format=",.0f", title="+ habitants")]), height=200)
with gauche:
    points = d["fact_carte_scenario"].query("scenario_id == @s.scenario_id").copy()
    vert = C["equite"] if variante == "equite" else C["propose"]
    points["couleur"] = [rgb(vert) if t == "Station proposée" else rgb(C["couvert"]) for t in points["type_point"]]
    points["rayon"] = 60 + points["taille"].fillna(0).clip(lower=0) ** 0.5 * 4
    couches = [couche_communes(), pdk.Layer("ScatterplotLayer", points, get_position="[lon, lat]", get_fill_color="couleur",
                                            get_radius="rayon", stroked=True,
                                            get_line_color=[255, 255, 255], line_width_min_pixels=1, pickable=True)]
    if lignes:
        ici = sel.iloc[[lignes[0]]][["lon", "lat"]]
        couches.append(pdk.Layer("ScatterplotLayer", ici, get_position="[lon, lat]", get_fill_color=[0, 0, 0, 0],
                                 get_radius=320, stroked=True, get_line_color=rgb(C["texte"]),
                                 line_width_min_pixels=3))
    carte(couches, {"text": "{type_point}\n{nom}"}, hauteur=470, vue=VUE_VILLE)
    legende([(C["couvert"], "station Citiz existante"), (vert, "station proposée (taille = habitants gagnés)"),
             (C["prioritaire_trait"], "commune prioritaire")])

b = st.columns(3)
with b[0]:
    st.markdown("**Budget → impact** (coût central, 1 à 30 stations)")
    courbe = d["fact_courbe"]
    st.altair_chart(alt.Chart(courbe).mark_line(color=C["couvert"], point=True).encode(
        x=alt.X("n_stations:Q", title=f"Stations (× {eur(courbe['budget'].iloc[0])})"), y=alt.Y("k6:Q", title="Habitants nouvellement couverts", axis=alt.Axis(labelExpr=ESPACE_MILLIERS)),
        tooltip=[alt.Tooltip("budget:Q", format=",.0f", title="Budget (€)"), alt.Tooltip("k6:Q", format=",.0f"),
                 alt.Tooltip("gain_marginal:Q", format=",.0f", title="Apport de la dernière station")]), height=240)
    st.caption(f"La 1re station couvre {ent(courbe['gain_marginal'].iloc[0])} habitants, "
               f"la {int(courbe['n_stations'].max())}e {ent(courbe['gain_marginal'].iloc[-1])}.")
with b[1]:
    st.markdown("**Les 12 scénarios** (le scénario choisi est cerclé)")
    vue = sc.assign(choisi=sc["scenario_id"] == s["scenario_id"],
                    Variante=sc["variante"].map({"efficacite": "Efficacité", "equite": "Équité"}))
    base = alt.Chart(vue).encode(x=alt.X("k7:Q", title="Coût total (€)", axis=alt.Axis(labelExpr=ESPACE_MILLIERS)),
                                 y=alt.Y("k6:Q", title="Habitants nouvellement couverts", axis=alt.Axis(labelExpr=ESPACE_MILLIERS)))
    st.altair_chart(base.mark_point(filled=True, size=90).encode(
        color=alt.Color("Variante:N", scale=alt.Scale(domain=["Efficacité", "Équité"], range=[C["couvert"], C["equite"]])),
        shape=alt.Shape("Variante:N"), tooltip=["libelle:N", alt.Tooltip("k6:Q", format=",.0f"), alt.Tooltip("k8:Q", format=".2f")])
        + base.transform_filter("datum.choisi").mark_point(size=400, color=C["texte"], strokeWidth=2), height=240)
with b[2]:
    st.markdown("**Prix de l'équité** (coût central, même budget)")
    eq = sc.query("hypothese_cout == 'central'").assign(
        Variante=lambda x: x["variante"].map({"efficacite": "Efficacité", "equite": "Équité"}),
        Budget=lambda x: x["budget"].map(eur))
    st.altair_chart(alt.Chart(eq).mark_bar().encode(
        x=alt.X("Budget:N", sort=alt.EncodingSortField("budget"), title=None), xOffset="Variante:N",
        y=alt.Y("k6:Q", title="Habitants nouvellement couverts", axis=alt.Axis(labelExpr=ESPACE_MILLIERS)),
        color=alt.Color("Variante:N", scale=alt.Scale(domain=["Efficacité", "Équité"], range=[C["couvert"], C["equite"]])),
        tooltip=["libelle:N", alt.Tooltip("k6:Q", format=",.0f"), alt.Tooltip("prix_equite_part:Q", format=".1%", title="Prix")]),
        height=240)
    e = sc.query("variante == 'equite'").sort_values("budget")
    st.caption("Prix : " + " · ".join(f"{eur(r.budget)} → −{ent(r.prix_equite_habitants)} hab. ({pct(r.prix_equite_part)})"
                                      for r in e.itertuples()))

if variante == "equite":
    st.info(f"**À retenir.** Imposer 30 % des gains aux communes prioritaires coûte {ent(s['prix_equite_habitants'])} habitants "
            f"({pct(s['prix_equite_part'])}) à ce budget, mais apporte {ent(s['pop_gagnee_prioritaire'])} habitants gagnés dans ces "
            f"communes, et {ent(s['pop_sans_option_gagnee'])} habitants qui n'avaient aucune option.")
else:
    st.info(f"**À retenir.** Ce portefeuille maximise les habitants nouvellement couverts ; il apporte "
            f"{pct(s['k12_part_prioritaire'])} de ses gains aux communes prioritaires et "
            f"{ent(s['pop_sans_option_gagnee'])} habitants qui n'avaient aucune option. Un optimum, pas une liste triée : "
            f"une règle simple (le meilleur site par euro, un par un) fait {ent(s['k6_glouton'])}.")
