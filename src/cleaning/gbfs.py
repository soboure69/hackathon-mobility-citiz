"""Stations GBFS (Citiz S01, Yélo vélo S08) : standardisation, nettoyage, table d'offre.

Une station GBFS est déjà une option : pas de fusion entre stations (RG-07 signale seulement
les coordonnées partagées). Les champs de disponibilité, instantanés, ne sont pas repris (RC-14).
"""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

from src.cleaning.audit import Suivi, ajouter_audit
from src.cleaning.coordonnees import controler_coordonnees, vers_lambert93
from src.cleaning.normalisation import normaliser_nom

# Champs de la source repris en Silver, et leur nom Silver.
CHAMPS_REPRIS = {
    "station_id": "station_id", "name": "nom", "lat": "lat", "lon": "lon", "capacity": "capacity",
    "address": "address", "parking_type": "parking_type", "is_virtual_station": "is_virtual_station",
    "station_opening_hours": "station_opening_hours",
}


def texte_localise(valeur: object, langue: str = "fr") -> object:
    """GBFS v3 : liste [{text, language}] ; v1/v2 : texte simple. Préfère `langue`, sinon le premier."""
    if isinstance(valeur, list):
        textes = [v for v in valeur if isinstance(v, dict) and "text" in v]
        choisis = [v for v in textes if v.get("language") == langue] or textes
        return choisis[0]["text"] if choisis else None
    return valeur


def standardiser_stations(stations: list[dict], *, source_id: str, fichier_origine: str,
                          sha256_origine: str, date_donnee: str, run_id: str) -> tuple[pd.DataFrame, list[str]]:
    """Une ligne par station, champs repris seulement. Renvoie aussi la liste des champs ignorés."""
    lignes = []
    for station in stations:
        ligne = {}
        for champ, colonne in CHAMPS_REPRIS.items():
            valeur = station.get(champ)
            if champ in ("name", "address"):
                valeur = texte_localise(valeur)
            if champ in ("lat", "lon") and valeur is not None:
                valeur = str(valeur)  # gardé en texte pour compter les décimales (RG-04)
            ligne[colonne] = valeur
        lignes.append(ligne)
    table = pd.DataFrame(lignes, columns=list(CHAMPS_REPRIS.values()))
    for colonne in ("station_id", "nom", "lat", "lon", "address", "parking_type", "station_opening_hours"):
        table[colonne] = table[colonne].astype("string")
    table["capacity"] = pd.to_numeric(table["capacity"], errors="coerce").astype("Int64")
    table["is_virtual_station"] = table["is_virtual_station"].astype("boolean")

    ignores = sorted({k for s in stations for k in s} - set(CHAMPS_REPRIS))
    table = ajouter_audit(table, source_id=source_id, id_origine=table["station_id"],
                          fichier_origine=fichier_origine, sha256_origine=sha256_origine,
                          date_donnee=date_donnee, run_id=run_id)
    return table, ignores


def nettoyer_stations(stations: pd.DataFrame, suivi: Suivi, emprise: dict) -> gpd.GeoDataFrame:
    """RC-02, RC-03, RG-01 à RG-04, RC-07. Sortie en EPSG:2154."""
    etape = "cleaned"
    df = suivi.rejeter(stations, stations["station_id"].isna(), "RC-02", "identifiant manquant", etape)
    df = suivi.rejeter(df, df["station_id"].duplicated(keep=False), "RC-03",
                       "identifiant en double dans la source", etape, "station_id")
    df = controler_coordonnees(df, suivi, etape=etape, emprise=emprise, col_lat="lat", col_lon="lon")
    df = suivi.signaler(df, df["capacity"].isna(), "RC-07", "capacité absente (valeur NULL gardée)", etape)
    df["nom_normalise"] = df["nom"].map(normaliser_nom).astype("string")
    return vers_lambert93(df)


def construire_offre(stations: gpd.GeoDataFrame, suivi: Suivi, *, mode: str, source_id: str) -> gpd.GeoDataFrame:
    """Une option par station. RG-07 : stations distinctes aux mêmes coordonnées, signalées et gardées."""
    etape = "deduplicated"
    partagees = stations.duplicated(subset=["lat_wgs84", "lon_wgs84"], keep=False)
    offre = suivi.signaler(stations, partagees, "RG-07", "coordonnées partagées avec une autre station", etape)
    offre["offre_id"] = mode + "_" + source_id + "_" + offre["station_id"]
    offre["mode"] = mode
    offre["capacite"] = offre["capacity"]
    colonnes = ["offre_id", "mode", "source_id", "id_origine", "nom", "nom_normalise",
                "lat_wgs84", "lon_wgs84", "capacite",
                "fichier_origine", "sha256_origine", "date_donnee", "run_id",
                "statut_transformation", "regles_appliquees", "qualite", "geometry"]
    return gpd.GeoDataFrame(offre[colonnes], geometry="geometry", crs=stations.crs)
