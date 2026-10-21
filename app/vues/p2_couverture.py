"""Page 2 — Couverture actuelle : où sont les habitants mal desservis, par quel mode, et qui sont-ils."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import altair as alt  # noqa: E402
import pydeck as pdk  # noqa: E402
import streamlit as st  # noqa: E402

from commun import (ESPACE_MILLIERS, C, COULEURS_MODE, MODES, carte, couche_communes, donnees, ent, filtre_communes, geojson,  # noqa: E402
                    legende, m, pct, rgb, titre)

d = donnees()
cellules, acces = d["dim_cellule"], d["fact_acces_mode"]
sans = m.pop_sans_option(cellules)
total = cellules["pop"].sum()
titre("Où sont les habitants mal desservis aujourd'hui ?",
      f"{pct(sans / total, 0)} des habitants n'ont aucune option de mobilité à 5 minutes à pied")

f1, f2 = st.columns([2, 3])
with f1:
    libelle = st.segmented_control("Mode", list(MODES), default="Tous modes", required=True, key="mode_p2")
with f2:
    communes = filtre_communes(d)
mode = MODES[libelle]
k = m.couverture(acces, cellules, mode, communes)

c = st.columns(4)
c[0].metric(f"Taux de couverture · {libelle}", pct(k["taux"]), border=True,
            help="Habitants à 5 min à pied d'au moins une option du mode, sur la population du périmètre.")
c[1].metric("Habitants desservis", ent(k["pop_desservie"]), border=True)
c[2].metric("Habitants non desservis", ent(k["pop_non_desservie"]), border=True)
c[3].metric("Options à 5 min par habitant", f"{k['options_par_habitant']:.2f}".replace(".", ","), border=True,
            help="Moyenne pondérée par la population. « Tous modes » compte chaque option une fois.")

gauche, droite = st.columns([3, 2])
with gauche:
    etat = acces[acces["mode"] == mode].set_index("cell_id")["desservi"]
    ids = set(cellules.loc[cellules["commune_insee"].isin(communes), "cell_id"]) if communes else None
    g = geojson("carreaux")
    pop = cellules.set_index("cell_id")["pop"]
    feats = []
    for f in g["features"]:
        cid = f["properties"]["cell_id"]
        if ids is not None and cid not in ids:
            continue
        ok = bool(etat.get(cid, False))
        feats.append({**f, "properties": {"cell_id": cid, "pop": f"· {pop.get(cid, 0):,.0f} habitants".replace(",", " "),
                                          "etat": "Carreau desservi" if ok else "Carreau non desservi",
                                          "couleur": rgb(C["couvert"] if ok else C["manque"], 170)}})
    carreaux = pdk.Layer("GeoJsonLayer", {"type": "FeatureCollection", "features": feats}, filled=True, stroked=False,
                         get_fill_color="properties.couleur", pickable=True)
    offre = d["dim_offre"] if mode == "tous" else d["dim_offre"][d["dim_offre"]["mode"] == mode]
    offre = offre.assign(couleur=offre["mode"].map(lambda x: rgb(COULEURS_MODE[x])),
                         habitants=offre["pop_5min"].map(lambda p: f"· {p:,.0f} habitants à 5 min".replace(",", " ")))
    stations = pdk.Layer("ScatterplotLayer", offre, get_position="[lon, lat]", get_fill_color="couleur", get_radius=35,
                         radius_min_pixels=2, pickable=True)
    carte([carreaux, couche_communes(), stations],
          {"html": "{properties.etat} {properties.pop}<br/>{nom} {mode} {habitants}"})
    legende([(C["couvert"], f"carreau de 200 m desservi ({libelle})"), (C["manque"], "carreau non desservi"),
             (C["prioritaire_trait"], "commune prioritaire"), (C["texte"], "point : station ou arrêt (survol = habitants à 5 min)")])
    st.markdown(f"**Habitants à 5 min de chaque station ou arrêt · {libelle}** (objectif 2 du sujet)")
    o = offre.assign(commune=offre["commune_insee"].map(dict(zip(d["dim_commune"]["commune_insee"], d["dim_commune"]["nom"]))))
    if communes:
        o = o[o["commune_insee"].isin(communes)]
    st.dataframe(o.sort_values("pop_5min", ascending=False)[["nom", "mode", "commune", "pop_5min", "pop_exclusive"]],
                 hide_index=True, height=210,
                 column_config={"nom": "Station ou arrêt", "mode": "Mode", "commune": "Commune",
                                "pop_5min": st.column_config.NumberColumn("Habitants à 5 min", format="%d",
                                                                          help="Ne s'additionne pas entre stations : les zones se chevauchent."),
                                "pop_exclusive": st.column_config.NumberColumn("Dont desservis par elle seule", format="%d")})

noms = d["dim_commune"][["commune_insee", "nom", "statut_commune", "prioritaire"]]
with droite:
    st.markdown(f"**Couverture par commune · {libelle}** (trait : seuil de priorité, tous modes 60 %)")
    kc = d["fact_kpi_commune"].query("mode == @mode").merge(noms, on="commune_insee")
    if communes:
        kc = kc[kc["commune_insee"].isin(communes)]
    barres = alt.Chart(kc).mark_bar().encode(
        x=alt.X("taux_couverture:Q", title="Taux de couverture", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("nom:N", sort="-x", title=None, axis=alt.Axis(labelOverlap=False, labelLimit=160)),
        color=alt.Color("statut_commune:N", title="Commune", scale=alt.Scale(domain=["Prioritaire", "Autre"],
                                                                             range=[C["equite"], C["couvert"]])),
        tooltip=[alt.Tooltip("nom:N", title="Commune"), alt.Tooltip("taux_couverture:Q", format=".1%", title="Couverture"),
                 alt.Tooltip("pop_non_desservie:Q", format=",.0f", title="Non desservis")])
    regle = alt.Chart().mark_rule(color=C["texte"], strokeDash=[4, 3]).encode(x=alt.datum(0.6))
    st.altair_chart(barres + regle, height=max(180, 19 * len(kc)))

b1, b2, b3 = st.columns([2, 2, 3])
with b1:
    st.markdown(f"**Habitants par nombre d'options · {libelle}**")
    dist = d["fact_distribution"].query("mode == @mode").groupby("classe", as_index=False)["pop"].sum()
    st.altair_chart(alt.Chart(dist).mark_bar(color=COULEURS_MODE[mode]).encode(
        x=alt.X("classe:N", sort=["0", "1-2", "3-5", "6+"], title="Options à 5 min"),
        y=alt.Y("pop:Q", title="Habitants", axis=alt.Axis(labelExpr=ESPACE_MILLIERS)), tooltip=[alt.Tooltip("pop:Q", format=",.0f", title="Habitants")]), height=240)
with b2:
    st.markdown(f"**Couverture par quintile de niveau de vie · {libelle}**")
    q = m.taux_quintiles(d["fact_equite_quintile"], mode)
    st.altair_chart(alt.Chart(q).mark_bar(color=COULEURS_MODE[mode]).encode(
        x=alt.X("quintile:N", title="Quintile (1 = plus modeste)"),
        y=alt.Y("taux:Q", title="Taux de couverture", axis=alt.Axis(format="%")),
        tooltip=[alt.Tooltip("taux:Q", format=".1%")]), height=240)
    st.caption(f"Écart quintile 1 − quintile 5 : {m.ecart_q1_q5(d['fact_equite_quintile'], mode):+.1f} pt".replace(".", ","))
with b3:
    st.markdown("**Communes prioritaires** (couverture tous modes < 60 %)")
    t = d["fact_kpi_commune"].query("mode == 'tous'").merge(noms, on="commune_insee").query("prioritaire")
    st.dataframe(t.sort_values("taux_couverture")[["nom", "pop_totale", "pop_non_desservie", "taux_couverture"]],
                 hide_index=True, height=240,
                 column_config={"nom": "Commune", "pop_totale": st.column_config.NumberColumn("Habitants", format="%d"),
                                "pop_non_desservie": st.column_config.NumberColumn("Sans option", format="%d"),
                                "taux_couverture": st.column_config.ProgressColumn("Couverture", format="percent",
                                                                                   min_value=0, max_value=1)})

prio = cellules[cellules["prioritaire"]]
part_sans_prio = prio.loc[~prio["desservi_tous"], "pop"].sum() / sans if sans else float("nan")
st.info(f"**À retenir.** {pct(sans / total, 0)} des habitants n'ont aucune option à 5 minutes. "
        f"Les {int(d['dim_commune']['prioritaire'].sum())} communes prioritaires regroupent {pct(prio['pop'].sum() / total, 0)} "
        f"des habitants mais {pct(part_sans_prio, 0)} des habitants sans option. "
        "Un habitant desservi par le bus et par le vélo ne compte qu'une fois en « tous modes ».")
