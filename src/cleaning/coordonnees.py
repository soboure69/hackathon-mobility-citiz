"""Contrôle des coordonnées (RG-01 à RG-04) et passage en Lambert-93."""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

from src.cleaning.audit import Suivi


def _decimales(colonne: pd.Series) -> pd.Series:
    return colonne.astype("string").str.extract(r"\.(\d*)$")[0].str.len().fillna(0).astype(int)


def controler_coordonnees(df: pd.DataFrame, suivi: Suivi, *, etape: str, emprise: dict,
                          col_lat: str, col_lon: str) -> pd.DataFrame:
    """Coordonnées lues en texte. Ajoute lat_wgs84 et lon_wgs84 (nombres). Aucune correction."""
    df = df.copy()
    df["lat_wgs84"] = pd.to_numeric(df[col_lat], errors="coerce")
    df["lon_wgs84"] = pd.to_numeric(df[col_lon], errors="coerce")
    df["_brut"] = df[col_lat].astype("string").fillna("∅") + " , " + df[col_lon].astype("string").fillna("∅")

    df = suivi.rejeter(df, df["lat_wgs84"].isna() | df["lon_wgs84"].isna(),
                       "RG-01", "coordonnée absente ou non numérique", etape, "_brut")

    lat, lon = df["lat_wgs84"], df["lon_wgs84"]
    dans_lat = lat.between(emprise["lat_min"], emprise["lat_max"])
    dans_lon = lon.between(emprise["lon_min"], emprise["lon_max"])
    inversees = ~(dans_lat & dans_lon) & lon.between(emprise["lat_min"], emprise["lat_max"]) \
        & lat.between(emprise["lon_min"], emprise["lon_max"])
    df = suivi.rejeter(df, inversees, "RG-03", "latitude et longitude probablement inversées", etape, "_brut")

    lat, lon = df["lat_wgs84"], df["lon_wgs84"]
    hors = ~(lat.between(emprise["lat_min"], emprise["lat_max"]) & lon.between(emprise["lon_min"], emprise["lon_max"]))
    df = suivi.rejeter(df, hors | ((lat == 0) & (lon == 0)), "RG-02", "hors France métropolitaine ou (0, 0)", etape, "_brut")

    precision = emprise["precision_min_decimales"]
    imprecis = (_decimales(df[col_lat]) < precision) | (_decimales(df[col_lon]) < precision)
    df = suivi.signaler(df, imprecis, "RG-04", f"moins de {precision} décimales", etape, "_brut")
    return df.drop(columns="_brut")


def vers_lambert93(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Géométrie en EPSG:2154 ; les coordonnées d'origine restent dans lat_wgs84 et lon_wgs84."""
    points = gpd.points_from_xy(df["lon_wgs84"], df["lat_wgs84"])
    return gpd.GeoDataFrame(df, geometry=points, crs=4326).to_crs(2154)
