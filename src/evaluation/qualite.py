"""Indicateurs de qualité Q1 à Q8, calculés sur les tables Silver (une ligne par indicateur)."""
from __future__ import annotations

import pandas as pd


def ligne(source_id: str, q_id: str, libelle: str, valeur: object, unite: str, run_id: str) -> dict:
    return {"source_id": source_id, "q_id": q_id, "libelle": libelle,
            "valeur": None if valeur is None else str(valeur), "unite": unite, "run_id": run_id}


def indicateurs_gtfs(*, source_id: str, run_id: str, standard: pd.DataFrame, propre: pd.DataFrame,
                     offre: pd.DataFrame, correspondances: pd.DataFrame, n_rejets: int,
                     feed_info: pd.DataFrame | None) -> pd.DataFrame:
    n = len(standard)
    coords = (standard["stop_lat"].notna() & standard["stop_lon"].notna()).mean()
    quais = len(correspondances)
    distances = correspondances["distance_m"].dropna()
    lignes = [
        ligne(source_id, "Q1", "complétude des coordonnées (stops.txt)", round(float(coords), 4), "part", run_id),
        ligne(source_id, "Q2", "lignes valides après nettoyage", round(1 - n_rejets / n, 4) if n else None, "part", run_id),
        ligne(source_id, "Q3", "lignes stops.txt", n, "lignes", run_id),
        ligne(source_id, "Q3", "quais (location_type = 0)", quais, "lignes", run_id),
        ligne(source_id, "Q3", "options après dédoublonnage", len(offre), "options", run_id),
        ligne(source_id, "Q4", "quais rattachés par parent_station",
              round(float((correspondances["methode"] == "parent_station").mean()), 4) if quais else None, "part", run_id),
        ligne(source_id, "RG-06", "distance quai → zone, médiane",
              round(float(distances.median()), 1) if len(distances) else None, "m", run_id),
        ligne(source_id, "RG-06", "distance quai → zone, 95e centile",
              round(float(distances.quantile(0.95)), 1) if len(distances) else None, "m", run_id),
        ligne(source_id, "RG-06", "distance quai → zone, maximum",
              round(float(distances.max()), 1) if len(distances) else None, "m", run_id),
    ]
    if feed_info is not None and len(feed_info):
        lignes += [
            ligne(source_id, "Q5", "début de validité (feed_info)", feed_info["feed_start_date"].iloc[0], "AAAAMMJJ", run_id),
            ligne(source_id, "Q5", "fin de validité (feed_info)", feed_info["feed_end_date"].iloc[0], "AAAAMMJJ", run_id),
        ]
    return pd.DataFrame(lignes).astype("string")


def indicateurs_gbfs(*, source_id: str, run_id: str, standard: pd.DataFrame, offre: pd.DataFrame,
                     n_rejets: int, last_updated: object, champs_ignores: list[str], n_rg07: int) -> pd.DataFrame:
    n = len(standard)
    lignes = [
        ligne(source_id, "Q1", "complétude des coordonnées", round(float((standard["lat"].notna() & standard["lon"].notna()).mean()), 4) if n else None, "part", run_id),
        ligne(source_id, "Q1", "complétude de la capacité", round(float(standard["capacity"].notna().mean()), 4) if n else None, "part", run_id),
        ligne(source_id, "Q2", "lignes valides après nettoyage", round(1 - n_rejets / n, 4) if n else None, "part", run_id),
        ligne(source_id, "Q3", "stations dans la source", n, "lignes", run_id),
        ligne(source_id, "Q3", "options (stations)", len(offre), "options", run_id),
        ligne(source_id, "RG-07", "stations aux coordonnées partagées", n_rg07, "stations", run_id),
        ligne(source_id, "Q5", "last_updated du fichier lu", last_updated, "tel que publié", run_id),
        ligne(source_id, "RC-14", "champs de la source non repris", ", ".join(champs_ignores) or "aucun", "liste", run_id),
    ]
    return pd.DataFrame(lignes).astype("string")


def indicateurs_admin(*, source_id: str, run_id: str, constats: list[dict], n_rejets: int,
                      n_reparees: int, communes: pd.DataFrame) -> pd.DataFrame:
    lignes = [ligne(source_id, "Q2", "géométries rejetées (vides)", n_rejets, "lignes", run_id),
              ligne(source_id, "RC-11", "géométries réparées", n_reparees, "lignes", run_id)]
    for c in constats:
        t = c["territoire"]
        pop = communes.loc[communes["territoire"] == t, "population"].sum()
        lignes += [
            ligne(source_id, "CS-09", f"{t} : communes (couche commune)", c["communes"], "communes", run_id),
            ligne(source_id, "CS-09", f"{t} : communes déclarées (couche epci)", c["declares_epci"], "communes", run_id),
            ligne(source_id, "Q6", f"{t} : population des communes (Admin Express)", int(pop), "habitants", run_id),
        ]
    return pd.DataFrame(lignes).astype("string")


def indicateurs_filosofi(*, source_id: str, run_id: str, carreaux: pd.DataFrame, communes: pd.DataFrame,
                         n_rejets: int, n_rc09: int) -> pd.DataFrame:
    lignes = [
        ligne(source_id, "Q2", "carreaux rejetés", n_rejets, "carreaux", run_id),
        ligne(source_id, "RC-09", "carreaux d'aire hors tolérance", n_rc09, "carreaux", run_id),
        ligne(source_id, "RC-09", "aire minimale", round(float(carreaux["aire_m2"].min()), 1), "m²", run_id),
        ligne(source_id, "RC-09", "aire maximale", round(float(carreaux["aire_m2"].max()), 1), "m²", run_id),
    ]
    for t, groupe in carreaux.groupby("territoire"):
        pop = float(groupe["ind"].sum())
        pop_admin = communes.loc[communes["territoire"] == t, "population"].sum()
        imputes = groupe["est_impute"]
        codes_vus = set(groupe["commune_insee"])
        codes = set(communes.loc[communes["territoire"] == t, "code_insee"])
        lignes += [
            ligne(source_id, "Q3", f"{t} : carreaux", len(groupe), "carreaux", run_id),
            ligne(source_id, "Q6", f"{t} : communes sans carreau rattaché", len(codes - codes_vus), "communes", run_id),
            ligne(source_id, "Q6", f"{t} : population Filosofi 2021", round(pop), "habitants", run_id),
            ligne(source_id, "Q6", f"{t} : rapport à la population Admin Express",
                  round(pop / float(pop_admin), 3) if pop_admin else None, "rapport", run_id),
            ligne(source_id, "Q8", f"{t} : part des carreaux imputés", round(float(imputes.mean()), 3), "part", run_id),
            ligne(source_id, "Q8", f"{t} : part de la population imputée",
                  round(float(groupe.loc[imputes, "ind"].sum()) / pop, 3) if pop else None, "part", run_id),
            ligne(source_id, "RF-01", f"{t} : carreaux multi-communes", int(groupe["multi_commune"].sum()), "carreaux", run_id),
            ligne(source_id, "RF-01", f"{t} : carreaux partiellement hors EPCI", int(groupe["partiel_epci"].sum()), "carreaux", run_id),
        ]
    return pd.DataFrame(lignes).astype("string")
