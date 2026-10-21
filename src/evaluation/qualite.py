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
