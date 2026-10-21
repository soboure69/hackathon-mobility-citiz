"""Page 5 — Méthode, qualité, limites et risques : peut-on faire confiance aux chiffres, et dans quelles limites."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from commun import donnees, m, pct, titre  # noqa: E402

d = donnees()
q = d["fact_qualite"]
ctrl = m.controles(d["fact_acces_mode"], d["dim_cellule"], d["fact_kpi_territoire"], d["dim_scenario"],
                   d["fact_cellules_gagnees"], d["fact_selection"])
n_ok, n_alerte, n_info = (int((q["statut"] == s).sum()) for s in ("ok", "alerte", "info"))
titre("Peut-on faire confiance à ces chiffres ?",
      f"Des chiffres traçables : {n_ok} contrôles de qualité conformes, {n_alerte} alertes connues")

meta = d["meta_execution"]
k = st.columns(4)
k[0].metric("Indicateurs conformes", pct(m.part_conformes(q), 0), border=True,
            help=f"{n_ok} conformes sur {n_ok + n_alerte} indicateurs à seuil ; {n_info} indicateurs informatifs sans seuil.")
k[1].metric("Indicateurs en alerte", n_alerte, border=True)
k[2].metric("Dernière exécution Gold", f"{pd.to_datetime(meta['date_execution_utc'], utc=True).max():%d/%m/%Y}", border=True,
            help="Lue dans les manifestes : chaque table porte son run_id (date UTC + commit Git).")
k[3].metric("Recoupements application / Python", f"{int(ctrl['ok'].sum())} / {len(ctrl)} à zéro", border=True,
            help="L'application ne recalcule pas les KPI : ces écarts prouvent qu'elle affiche les mêmes valeurs que le pipeline.")
if meta["modifie"].any():
    st.error("Au moins une table Gold vient de code non commité (run_id « -modifie »).")

st.markdown("**Chaîne de traitement**")
st.graphviz_chart("""
digraph { rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#EFF3FF", color="#0072B2", fontname="Helvetica"];
  S [label="Sources ouvertes\\nGTFS, GBFS, Filosofi,\\nAdmin Express, OSM"]; B [label="Bronze\\nbrut, empreintes SHA-256"];
  Si [label="Silver\\nnettoyé, dédoublonné,\\njointures, qualité"]; G [label="Gold\\naccessibilité, KPI, score,\\noptimisation"];
  E [label="Exports\\ncontrôles X-01 à X-07"]; A [label="Application"];
  S -> B -> Si -> G -> E -> A; }""", width="stretch")

g, dr = st.columns(2)
with g:
    st.markdown("**Qualité par dimension**")
    famille = st.segmented_control("Famille", sorted(q["famille"].unique()), selection_mode="multi",
                                   default=sorted(q["famille"].unique()), key="famille_p5",
                                   format_func=lambda f: f.replace("_", " "))
    qf = q[q["famille"].isin(famille or [])]
    st.dataframe(pd.crosstab(qf["dimension"], qf["statut"]).rename(columns={"ok": "✓ ok", "alerte": "⚠ alerte", "info": "ⓘ info"}))
with dr:
    st.markdown("**Alertes**")
    st.dataframe(qf[qf["statut"] == "alerte"][["indicateur_id", "libelle", "valeur", "seuil", "source_id"]], hide_index=True,
                 column_config={"indicateur_id": "Indicateur", "libelle": "Libellé", "valeur": "Valeur", "seuil": "Seuil",
                                "source_id": "Source"})
    st.markdown("**Recoupements** (écart attendu : 0)")
    st.dataframe(ctrl.assign(statut=ctrl["ok"].map({True: "✓", False: "✕"}))[["statut", "controle", "ecart"]], hide_index=True,
                 column_config={"statut": st.column_config.TextColumn("", width="small"), "controle": "Contrôle",
                                "ecart": st.column_config.NumberColumn("Écart", format="%.2e")})

st.markdown("**Hypothèses** · ● certain · ◐ estimé · ○ hypothèse")
h = d["ref_hypotheses"]
icone = {"certain": "●", "estimé": "◐", "hypothèse": "○"}
st.dataframe(h.assign(nature=h["nature"].map(lambda n: f"{icone[n]} {n}"))[["hypothese_id", "theme", "texte", "valeur", "nature", "document"]],
             hide_index=True, column_config={"hypothese_id": "Id", "theme": "Thème", "texte": st.column_config.TextColumn("Hypothèse", width="large"),
                                             "valeur": "Valeur", "nature": "Nature", "document": "Document"})

s1, s2 = st.columns(2)
with s1:
    st.markdown("**Sources**")
    src = d["dim_source"]
    st.dataframe(src[src["statut"].fillna("").str.len() > 0][["source_id", "nom", "producteur", "licence", "millesime", "statut"]],
                 hide_index=True, height=300, column_config={"source_id": "Id", "nom": "Source", "producteur": "Producteur",
                                                             "licence": "Licence", "millesime": "Millésime", "statut": "Statut"})
with s2:
    st.markdown("**Risques ouverts**")
    r = d["ref_risques"]
    st.dataframe(r[r["ouvert"]][["risque_id", "libelle", "probabilite", "impact", "mitigation"]], hide_index=True, height=300,
                 column_config={"risque_id": "Id", "libelle": st.column_config.TextColumn("Risque", width="large"),
                                "probabilite": "Probabilité", "impact": "Impact", "mitigation": "Mitigation"})

st.markdown("**Limites et enjeux**")
st.markdown(
    "- **Score, pas prédiction** : aucun historique d'usage Citiz n'est disponible ; le score classe des sites, il ne prévoit pas de locations.\n"
    "- **Coûts et budgets** : hypothèses de simulation ou estimations publiques, jamais des montants votés.\n"
    "- **Couverture des données ≠ couverture de mobilité** : la première mesure ce que les sources couvrent, la seconde qui a une option à 5 min.\n"
    "- **Marche à 5 minutes** sur le réseau piéton OpenStreetMap (400 m) : pentes, traversées et obstacles ne sont pas modélisés.\n"
    "- **Vie privée** : aucune donnée personnelle ; population agrégée en carreaux de 200 m, carreaux de moins de 11 ménages imputés par l'INSEE.\n"
    "- **Accessibilité** des stations aux personnes à mobilité réduite : non mesurée.\n"
    "- **Fraîcheur** : voir l'alerte sur l'âge du flux GBFS ; l'offre a pu changer depuis le téléchargement.")
