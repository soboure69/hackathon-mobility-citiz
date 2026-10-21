"""Page 1 — Synthèse : situation, recommandation, coût, compromis équité (en 30 secondes)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pydeck as pdk  # noqa: E402
import streamlit as st  # noqa: E402

from commun import VUE_VILLE, C, carte, couche_communes, donnees, ent, etiquette, eur, legende, m, nom_commune, pct, rgb, titre  # noqa: E402

d = donnees()
sc = d["dim_scenario"]
ref = m.reference(sc)
eq = m.variante_equite(sc, ref)
cellules = d["dim_cellule"]
citiz = m.couverture(d["fact_acces_mode"], cellules, "citiz")
sans = m.pop_sans_option(cellules)

titre("Où financer de nouvelles stations Citiz, et avec quel effet ?",
      f"{ref['n_stations']} stations Citiz font passer la couverture de {pct(ref['couverture_citiz_avant'])} "
      f"à {pct(ref['couverture_citiz_apres'])} pour {eur(ref['budget'])}")

k = st.columns(4)
k[0].metric("Couverture Citiz aujourd'hui", pct(citiz["taux"]), border=True,
            help="Part des habitants à 5 min à pied (400 m sur le réseau piéton) d'une station Citiz.")
k[1].metric("Habitants sans aucune option à 5 min", ent(sans), border=True,
            help="Ni bus, ni Citiz, ni vélo en libre-service à 5 min à pied.")
k[2].metric("Habitants nouvellement couverts", "+" + ent(ref["k6"]), border=True,
            help="Chaque habitant compté une seule fois, même s'il est proche de plusieurs nouvelles stations.")
k[3].metric("Coût par habitant gagné", eur(ref["k8"], 2), border=True,
            help=f"Coût sur 3 ans : {eur(ref['cout_station'])} par station ({ref['cout_etiquette']}).")
st.markdown(f"Scénario de référence : **{ref['libelle']}** · coûts {etiquette(ref['cout_etiquette'])} · budget {etiquette('hypothèse de simulation')}")

gauche, droite = st.columns([3, 2])
with gauche:
    points = d["fact_carte_scenario"].query("scenario_id == @ref.scenario_id").copy()
    points["couleur"] = [rgb(C["propose"]) if t == "Station proposée" else rgb(C["couvert"]) for t in points["type_point"]]
    points["rayon"] = 60 + points["taille"].fillna(0).clip(lower=0) ** 0.5 * 4
    couche = pdk.Layer("ScatterplotLayer", points, get_position="[lon, lat]", get_fill_color="couleur",
                       get_radius="rayon", stroked=True, get_line_color=[255, 255, 255],
                       line_width_min_pixels=1, pickable=True)
    carte([couche_communes(), couche], {"text": "{type_point}\n{nom}"}, vue=VUE_VILLE)
    legende([(C["couvert"], "station Citiz existante"), (C["propose"], "station proposée (taille = habitants gagnés)"),
             (C["prioritaire_trait"], "contour épais : commune prioritaire (couverture tous modes < 60 %)")])

with droite:
    st.markdown("**Stations proposées, par ordre d'apport**")
    sel = d["fact_selection"].query("scenario_id == @ref.scenario_id").sort_values("ordre_ajout")
    noms = nom_commune(d)
    st.dataframe(sel.assign(commune=sel["commune_insee"].map(noms))[
        ["ordre_ajout", "commune", "pop_nouvelle_marginale", "pop_nouvelle_cumulee", "cout_cumule"]],
        hide_index=True, height=260,
        column_config={"ordre_ajout": st.column_config.NumberColumn("#", width="small"),
                       "commune": "Commune",
                       "pop_nouvelle_marginale": st.column_config.NumberColumn("+ habitants", format="%d"),
                       "pop_nouvelle_cumulee": st.column_config.NumberColumn("Cumul", format="%d"),
                       "cout_cumule": st.column_config.NumberColumn("Coût cumulé (€)", format="%d")})
    if eq is not None:
        st.markdown("**Même budget : efficacité ou équité ?**")
        a, b = st.columns(2)
        a.metric("Efficacité · habitants", ent(ref["k6"]), border=True)
        b.metric("Équité · habitants", ent(eq["k6"]),
                 delta=f"-{ent(eq['prix_equite_habitants'])} hab. ({pct(eq['prix_equite_part'])})", delta_color="off",
                 border=True, help="Au moins 30 % des habitants nouvellement couverts vivent dans une commune prioritaire.")
        st.caption(f"Habitants gagnés en communes prioritaires : {ent(ref['pop_gagnee_prioritaire'])} → "
                   f"{ent(eq['pop_gagnee_prioritaire'])}. L'outil montre l'arbitrage ; il ne le tranche pas.")

st.info(
    f"**À retenir.** Aujourd'hui, {pct(citiz['taux'])} des habitants ont une station Citiz à 5 minutes à pied. "
    f"Avec {eur(ref['budget'])} sur 3 ans, {ref['n_stations']} stations bien placées couvrent "
    f"{ent(ref['k6'])} habitants de plus, pour {eur(ref['k8'], 2)} par habitant gagné. "
    + (f"Ce choix n'apporte que {pct(ref['k12_part_prioritaire'])} de ses gains aux communes peu desservies ; "
       f"en y imposer 30 % coûte {pct(eq['prix_equite_part'], 0)} de l'impact." if eq is not None else ""))
