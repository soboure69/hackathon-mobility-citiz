"""Tables d'export pour la restitution (application Streamlit, compatible Power BI).

Fonctions pures : elles reçoivent des tables Gold déjà lues et renvoient les tables d'export.
Aucun KPI n'est recalculé autrement qu'en Gold : on renomme, on dépivote, on fusionne.
Règles (AD1 à AD4) : coordonnées WGS84 en colonnes `lat` / `lon`, aucune géométrie binaire,
aucune table de paires. Les polygones partent dans deux GeoJSON à part (communes, carreaux).
"""
from __future__ import annotations

import re

import geopandas as gpd
import numpy as np
import pandas as pd

MODES = pd.DataFrame({
    "mode": ["tous", "bus", "citiz", "velo"],
    "libelle": ["Tous modes", "Bus", "Citiz", "Vélo"],
    "ordre": [1, 2, 3, 4],
    "couleur": ["#1A1A1A", "#6E6E6E", "#0072B2", "#CC79A7"],
})
CRITERES = pd.DataFrame({
    "critere": ["impact", "besoin", "complementarite_bus", "logement_collectif", "petits_menages"],
    "libelle_critere": ["Impact", "Besoin", "Complémentarité bus", "Logement collectif", "Petits ménages"],
    "ordre": [1, 2, 3, 4, 5],
})
LIBELLES_BUDGET = {"prudent": "Prudent", "central": "Central", "ambitieux": "Ambitieux"}
ORDRE_BUDGET = {"prudent": 1, "central": 2, "ambitieux": 3}
LIBELLES_VARIANTE = {"efficacite": "Efficacité", "equite": "Équité"}
CLASSES_SCORE = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"]


def _wgs84(gdf: gpd.GeoDataFrame) -> tuple[pd.Series, pd.Series]:
    """Centroïdes (calculés en 2154) en WGS84."""
    centres = gpd.GeoSeries(gdf.geometry.centroid, crs=gdf.crs).to_crs(4326)
    return centres.y.round(6), centres.x.round(6)


def dim_mode() -> pd.DataFrame:
    return MODES.copy()


def dim_commune(communes: gpd.GeoDataFrame, kpi: pd.DataFrame, acces: pd.DataFrame,
                epci: str, seuil: float) -> pd.DataFrame:
    c = communes.loc[communes["epci_siren"] == epci, ["code_insee", "nom_officiel"]]
    c = c.rename(columns={"code_insee": "commune_insee", "nom_officiel": "nom"})
    k = kpi[kpi["perimetre_type"] == "commune"].pivot(index="perimetre_id", columns="mode", values="taux_couverture")
    c = c.merge(k[["tous", "citiz"]].rename(columns={"tous": "taux_tous_modes", "citiz": "taux_citiz"}),
                left_on="commune_insee", right_index=True, how="left")
    pop = acces.groupby("commune_insee")["pop"].sum().rename("pop_filosofi")
    c = c.merge(pop, left_on="commune_insee", right_index=True, how="left")
    c["prioritaire"] = c["taux_tous_modes"].astype(float) < seuil
    c["statut_commune"] = np.where(c["prioritaire"], "Prioritaire", "Autre")
    return c.reset_index(drop=True)


def dim_cellule(acces: gpd.GeoDataFrame, prioritaires: set[str]) -> pd.DataFrame:
    d = pd.DataFrame({
        "cell_id": acces["cell_id"], "commune_insee": acces["commune_insee"], "pop": acces["pop"].astype(float),
        "classe_acces": acces["classe_acces"], "n_options_total": acces["n_options_total"],
        "desservi_tous": acces["desservi"].astype(bool), "desservi_citiz": acces["desservi_citiz"].astype(bool),
        "quintile_niveau_vie": acces["quintile_niveau_vie"], "niveau_vie_moyen": acces["niveau_vie_moyen"],
        "est_impute": acces["est_impute"].astype(bool),
    })
    d["lat"], d["lon"] = _wgs84(acces)
    d["prioritaire"] = d["commune_insee"].isin(prioritaires)
    return d


def fact_acces_mode(acces: gpd.GeoDataFrame) -> pd.DataFrame:
    """Carreau × mode. `tous` reprend n_options_total, dist_min_m et desservi."""
    lat, lon = _wgs84(acces)
    blocs = []
    for mode in ["bus", "citiz", "velo", "tous"]:
        suffixe = "" if mode == "tous" else f"_{mode}"
        blocs.append(pd.DataFrame({
            "cell_id": acces["cell_id"], "mode": mode, "pop": acces["pop"].astype(float),
            "n_options": acces["n_options_total" if mode == "tous" else f"n_options_{mode}"].astype(int),
            "dist_min_m": acces[f"dist_min{suffixe}_m"].astype(float),
            "desservi": acces[f"desservi{suffixe}"].astype(bool), "lat": lat, "lon": lon,
        }))
    return pd.concat(blocs, ignore_index=True)


def fact_kpi(kpi: pd.DataFrame, perimetre: str) -> pd.DataFrame:
    colonnes = ["mode", "pop_totale", "pop_desservie", "pop_non_desservie", "taux_couverture",
                "options_moyennes_par_habitant", "pop_au_moins_2_modes"]
    k = kpi[kpi["perimetre_type"] == perimetre]
    if perimetre == "commune":
        return k.rename(columns={"perimetre_id": "commune_insee"})[["commune_insee"] + colonnes].reset_index(drop=True)
    return k[colonnes].reset_index(drop=True)


def fact_distribution(distribution: pd.DataFrame) -> pd.DataFrame:
    d = distribution[["mode", "n_options", "pop", "n_carreaux"]].copy()
    d["classe"] = pd.cut(d["n_options"], [-1, 0, 2, 5, np.inf], labels=["0", "1-2", "3-5", "6+"]).astype(str)
    return d


def fact_equite_quintile(equite: pd.DataFrame) -> pd.DataFrame:
    e = equite.rename(columns={"quintile_niveau_vie": "quintile"})
    return e[["quintile", "mode", "pop", "pop_desservie", "taux_couverture"]].astype({"quintile": str}).reset_index(drop=True)


def dim_offre(offre: gpd.GeoDataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "offre_id": offre["offre_id"], "mode": offre["mode"], "nom": offre["nom"], "commune_insee": offre["commune_insee"],
        "lat": offre["lat_wgs84"].round(6), "lon": offre["lon_wgs84"].round(6), "capacite": offre["capacite"],
        "pop_5min": offre["pop_5min"].astype(float), "pop_exclusive": offre["pop_exclusive"].astype(float),
        "atteinte": offre["atteinte"].astype(bool),
    }).reset_index(drop=True)


def dim_candidat(candidats: pd.DataFrame, type_equipement: str) -> pd.DataFrame:
    """Candidats retenus du type (P-4 : Citiz seulement)."""
    c = candidats[(candidats["type_equipement"] == type_equipement) & candidats["retenu"].astype(bool)]
    d = pd.DataFrame({
        "candidat_id": c["candidat_id"], "commune_insee": c["commune_insee"], "score": c["score"].astype(float),
        "rang": c["rang"], "rang_commune": c["rang_commune"], "rang_equite": c["rang_equite"],
        "pop_rayon": c["pop_rayon"].astype(float), "pop_nouvelle_isolee": c["pop_nouvelle"].astype(float),
        "taux_redondance": c["taux_redondance"].astype(float), "frequence_top_n": c["frequence_top_n"].astype(float),
        "commune_prioritaire": c["commune_prioritaire"].astype(bool),
        "lat": c["lat_wgs84"].round(6), "lon": c["lon_wgs84"].round(6),
    }).reset_index(drop=True)
    d["classe_score"] = pd.qcut(d["score"], 5, labels=CLASSES_SCORE).astype(str)
    return d


def fact_contribution(candidats_dim: pd.DataFrame, candidats: pd.DataFrame, type_equipement: str) -> pd.DataFrame:
    """Candidat × critère. Un même nœud est candidat pour plusieurs types : on filtre le type."""
    c = candidats[(candidats["type_equipement"] == type_equipement) & candidats["candidat_id"].isin(candidats_dim["candidat_id"])]
    blocs = [pd.DataFrame({"candidat_id": c["candidat_id"], "critere": k,
                           "valeur_normalisee": c[f"n_{k}"].astype(float), "contribution": c[f"contribution_{k}"].astype(float)})
             for k in CRITERES["critere"]]
    return pd.concat(blocs, ignore_index=True).merge(CRITERES, on="critere")


def dim_scenario(scenarios: pd.DataFrame, kpi_scenario: pd.DataFrame, reference: str) -> pd.DataFrame:
    s = scenarios.merge(kpi_scenario.drop(columns=["cout_etiquette", "variante", "run_id"], errors="ignore"),
                        on="scenario_id", how="left")
    d = pd.DataFrame({
        "scenario_id": s["scenario_id"], "scenario": s["scenario"], "ordre_budget": s["scenario"].map(ORDRE_BUDGET),
        "hypothese_cout": s["hypothese_cout"], "variante": s["variante"], "budget": s["budget"].astype(float),
        "cout_station": s["cout_station"].astype(float), "cout_etiquette": s["cout_etiquette"],
        "n_stations": s["n_stations"].astype(int), "k6": s["k6_pop_nouvellement_couverte"].astype(float),
        "k7": s["k7_cout_total"].astype(float), "k8": s["k8_cout_par_habitant"].astype(float),
        "couverture_citiz_avant": s["couverture_citiz_avant"], "couverture_citiz_apres": s["couverture_citiz_apres"],
        "couverture_tous_avant": s["couverture_tous_modes_avant"], "couverture_tous_apres": s["couverture_tous_modes_apres"],
        "pop_sans_option_gagnee": s["pop_sans_option_gagnee"],
        "pop_gagnee_prioritaire": s["pop_gagnee_communes_prioritaires"],
        "k12_part_prioritaire": s["k12_part_gains_communes_prioritaires"],
        "scenario_reference": s["scenario_reference"], "prix_equite_habitants": s["prix_equite_habitants"],
        "prix_equite_part": s["prix_equite_part"], "statut_solution": s["statut_solution"],
        "ecart_relatif_garanti": s["ecart_relatif_garanti"], "k6_glouton": s["k6_glouton"],
    })
    d["libelle"] = (d["scenario"].map(LIBELLES_BUDGET) + " · " + d["budget"].map(lambda b: f"{b:,.0f} €".replace(",", " "))
                    + " · " + d["cout_station"].map(lambda c: f"{c:,.0f} €/station".replace(",", " "))
                    + " · " + d["variante"].map(LIBELLES_VARIANTE))
    d["est_reference"] = d["scenario_id"] == reference
    return d.reset_index(drop=True)


def fact_selection(selection: pd.DataFrame) -> pd.DataFrame:
    colonnes = ["scenario_id", "candidat_id", "ordre_ajout", "cout", "cout_cumule", "pop_nouvelle_marginale",
                "pop_nouvelle_cumulee", "commune_insee", "score"]
    d = pd.DataFrame(selection[colonnes])
    d["lat"], d["lon"] = selection["lat_wgs84"].round(6), selection["lon_wgs84"].round(6)
    return d.reset_index(drop=True)


def fact_carte_scenario(selection: pd.DataFrame, offre: pd.DataFrame, scenarios: list[str], type_equipement: str) -> pd.DataFrame:
    """Une table de points par scénario : stations existantes du type (répétées) + stations proposées."""
    existantes = offre[offre["mode"] == type_equipement]
    blocs = []
    for sid in scenarios:
        blocs.append(pd.DataFrame({"scenario_id": sid, "point_id": existantes["offre_id"], "type_point": "Citiz existante",
                                   "nom": existantes["nom"], "lat": existantes["lat"], "lon": existantes["lon"],
                                   "taille": existantes["pop_5min"], "ordre_ajout": pd.NA}))
    s = selection
    blocs.append(pd.DataFrame({"scenario_id": s["scenario_id"], "point_id": s["candidat_id"], "type_point": "Station proposée",
                               "nom": "Station proposée n° " + s["ordre_ajout"].astype(str), "lat": s["lat"], "lon": s["lon"],
                               "taille": s["pop_nouvelle_marginale"], "ordre_ajout": s["ordre_ajout"]}))
    d = pd.concat(blocs, ignore_index=True)
    d["ordre_ajout"] = d["ordre_ajout"].astype("Int64")
    return d


def fact_cellules_gagnees(cellules: pd.DataFrame) -> pd.DataFrame:
    return cellules[["scenario_id", "cell_id", "pop", "prioritaire", "gain_tous_modes"]].reset_index(drop=True)


def fact_courbe(courbe: pd.DataFrame) -> pd.DataFrame:
    return courbe[["n_stations", "budget", "k6", "gain_marginal", "k8_cout_par_habitant"]].rename(
        columns={"k8_cout_par_habitant": "k8"}).reset_index(drop=True)


def fact_sensibilite(sensibilite: pd.DataFrame, type_equipement: str) -> pd.DataFrame:
    s = sensibilite[sensibilite["type_equipement"] == type_equipement]
    return s[["variable", "facteur", "spearman", "recouvrement_top_n"]].reset_index(drop=True)


def fact_qualite(qualite: pd.DataFrame) -> pd.DataFrame:
    return qualite.drop(columns=["run_id"]).reset_index(drop=True)


def dim_source(registre: pd.DataFrame) -> pd.DataFrame:
    colonnes = {"source_id": "source_id", "nom": "nom", "producteur": "producteur", "licence": "licence",
                "millesime_ou_version": "millesime", "date_consultation": "date_consultation",
                "url_fiche": "url", "priorite": "priorite", "statut": "statut"}
    d = registre[list(colonnes)].rename(columns=colonnes)
    return d.astype({c: "string" for c in d.columns}).reset_index(drop=True)


def ref_hypotheses(hypotheses: list[dict]) -> pd.DataFrame:
    d = pd.DataFrame(hypotheses)
    attendu = {"hypothese_id", "theme", "texte", "valeur", "nature", "document"}
    if set(d.columns) != attendu:
        raise ValueError(f"config/app.yaml : colonnes d'hypothèse {sorted(d.columns)}, attendu {sorted(attendu)}")
    if not d["nature"].isin(["certain", "estimé", "hypothèse"]).all():
        raise ValueError("config/app.yaml : nature ∈ {certain, estimé, hypothèse}")
    return d.astype("string")


def ref_risques(texte_markdown: str) -> pd.DataFrame:
    """Lit le tableau de docs/suivi_risques.md (lignes « | Rnn | … | »)."""
    lignes = []
    for ligne in texte_markdown.splitlines():
        if re.match(r"^\| R\d+ \|", ligne):
            cases = [c.strip() for c in ligne.strip().strip("|").split("|")]
            if len(cases) >= 6:
                lignes.append(cases[:6])
    d = pd.DataFrame(lignes, columns=["risque_id", "libelle", "probabilite", "impact", "mitigation", "responsable"])
    d["ouvert"] = ~(d["probabilite"].str.lower().eq("écartée") | d["mitigation"].str.contains(r"\b[Cc]los", regex=True))
    return d.drop_duplicates("risque_id", keep="last").reset_index(drop=True)


def meta_execution(manifestes: dict[str, dict]) -> pd.DataFrame:
    """Une ligne par table Gold : run_id, date d'exécution et commit lus dans le run_id."""
    lignes = []
    for dossier, contenu in manifestes.items():
        for table, entree in contenu.get("tables", {}).items():
            run_id = str(entree.get("run_id", ""))
            m = re.match(r"^(\d{8}T\d{6}Z)_([0-9a-f]+)(-modifie)?$", run_id)
            lignes.append({"dossier": dossier, "table": table, "run_id": run_id,
                           "date_execution_utc": pd.to_datetime(m.group(1), format="%Y%m%dT%H%M%SZ", utc=True) if m else pd.NaT,
                           "commit": m.group(2) if m else None, "modifie": bool(m and m.group(3))})
    return pd.DataFrame(lignes)


def geojson_communes(communes: gpd.GeoDataFrame, dim: pd.DataFrame, tolerance_m: float = 20.0) -> gpd.GeoDataFrame:
    g = communes.rename(columns={"code_insee": "commune_insee"}).merge(
        dim[["commune_insee", "nom", "prioritaire", "taux_tous_modes"]], on="commune_insee", how="inner")
    g = g[["commune_insee", "nom", "prioritaire", "taux_tous_modes", "geometry"]].copy()
    g["geometry"] = g.geometry.simplify(tolerance_m, preserve_topology=True)
    return g.to_crs(4326)


def geojson_carreaux(acces: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return acces[["cell_id", "geometry"]].to_crs(4326)
