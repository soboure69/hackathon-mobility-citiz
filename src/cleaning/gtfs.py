"""Arrêts GTFS (S02) : standardisation, nettoyage, dédoublonnage par zone d'arrêt."""
from __future__ import annotations

import zipfile

import geopandas as gpd
import pandas as pd

from src.cleaning.audit import Suivi, ajouter_audit
from src.cleaning.coordonnees import controler_coordonnees, vers_lambert93
from src.cleaning.normalisation import normaliser_nom

JOURS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def lire_table_gtfs(chemin_zip, nom: str, colonnes: list[str] | None = None) -> pd.DataFrame | None:
    """Lit un fichier du zip GTFS, tout en texte (aucun identifiant converti en nombre).

    Renvoie None si le fichier n'existe pas dans l'archive (fichiers facultatifs de la norme).
    """
    with zipfile.ZipFile(chemin_zip) as archive:
        if nom not in archive.namelist():
            return None
        with archive.open(nom) as fichier:
            table = pd.read_csv(fichier, dtype="string", keep_default_na=False,
                                encoding="utf-8-sig", usecols=colonnes)
    return table.replace("", pd.NA)


def standardiser_stops(chemin_zip, *, source_id: str, fichier_origine: str, sha256_origine: str,
                       date_donnee: str, run_id: str) -> pd.DataFrame:
    """stops.txt tel quel, en texte, avec les colonnes d'audit. Aucune ligne retirée."""
    stops = lire_table_gtfs(chemin_zip, "stops.txt")
    stops["location_type"] = stops["location_type"].fillna("0")  # norme GTFS : vide = 0 (quai)
    return ajouter_audit(stops, source_id=source_id, id_origine=stops["stop_id"],
                         fichier_origine=fichier_origine, sha256_origine=sha256_origine,
                         date_donnee=date_donnee, run_id=run_id)


def services_actifs(chemin_zip) -> set[str]:
    """Services ayant au moins un jour de circulation (calendar) ou un ajout (calendar_dates)."""
    actifs: set[str] = set()
    calendrier = lire_table_gtfs(chemin_zip, "calendar.txt")
    if calendrier is not None:
        actifs |= set(calendrier.loc[(calendrier[JOURS] == "1").any(axis=1), "service_id"])
    exceptions = lire_table_gtfs(chemin_zip, "calendar_dates.txt")
    if exceptions is not None:
        actifs |= set(exceptions.loc[exceptions["exception_type"] == "1", "service_id"])
    return actifs


def quais_desservis(chemin_zip) -> set[str]:
    """Arrêts présents dans stop_times pour au moins une course d'un service actif."""
    actifs = services_actifs(chemin_zip)
    courses = lire_table_gtfs(chemin_zip, "trips.txt", ["trip_id", "service_id"])
    courses_actives = set(courses.loc[courses["service_id"].isin(actifs), "trip_id"])
    horaires = lire_table_gtfs(chemin_zip, "stop_times.txt", ["trip_id", "stop_id"])
    return set(horaires.loc[horaires["trip_id"].isin(courses_actives), "stop_id"])


def nettoyer_stops(stops: pd.DataFrame, suivi: Suivi, desservis: set[str], emprise: dict) -> gpd.GeoDataFrame:
    """RC-02, RC-03, RG-01 à RG-04, RC-06, RC-04. Sortie en EPSG:2154."""
    etape = "cleaned"
    df = suivi.rejeter(stops, stops["stop_id"].isna(), "RC-02", "identifiant manquant", etape)
    df = suivi.rejeter(df, df["stop_id"].duplicated(keep=False), "RC-03",
                       "identifiant en double dans la source", etape, "stop_id")
    df = controler_coordonnees(df, suivi, etape=etape, emprise=emprise, col_lat="stop_lat", col_lon="stop_lon")
    df = suivi.exclure(df, df["location_type"].isin(["2", "3", "4"]), "RC-06",
                       "entrée, nœud ou zone d'embarquement : pas une option", etape, "location_type")

    quai = df["location_type"] == "0"
    df["desservi"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[quai, "desservi"] = df.loc[quai, "stop_id"].isin(desservis)
    df = suivi.exclure(df, quai & ~df["desservi"].fillna(False), "RC-04",
                       "quai sans course active dans le GTFS", etape)

    df["nom_normalise"] = df["stop_name"].map(normaliser_nom).astype("string")
    df["statut_transformation"] = df["statut_transformation"].where(
        df["statut_transformation"] == "exclu", "standardise")
    return vers_lambert93(df)


def dedupliquer_zones(stops: gpd.GeoDataFrame, suivi: Suivi, *, source_id: str,
                      seuil_rg06_m: float | None) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """Une option = une zone d'arrêt (parent_station) avec au moins un quai desservi.

    Un quai sans zone valide devient sa propre option (méthode « aucune »).
    Renvoie (offre_arrets, dedup_correspondances). Aucun quai n'est perdu.
    """
    etape = "deduplicated"
    zones = stops[stops["location_type"] == "1"].set_index("stop_id")
    quais = stops[stops["location_type"] == "0"].copy()

    a_parent = quais["parent_station"].notna() & quais["parent_station"].isin(zones.index)
    quais["zone_id"] = quais["parent_station"].where(a_parent, quais["stop_id"])
    quais["methode"] = a_parent.map({True: "parent_station", False: "aucune"})
    geometrie_zone = gpd.GeoSeries(zones.geometry.reindex(quais["zone_id"]).values, index=quais.index, crs=stops.crs)
    quais["distance_m"] = quais.geometry.distance(geometrie_zone).where(a_parent)
    if seuil_rg06_m is not None:
        quais = suivi.signaler(quais, quais["distance_m"] > seuil_rg06_m, "RG-06",
                               f"quai à plus de {seuil_rg06_m} m de sa zone", etape, "distance_m")

    quais["offre_id"] = "bus_" + source_id + "_" + quais["zone_id"]
    correspondances = pd.DataFrame({
        "source_id": source_id, "id_origine": quais["stop_id"], "offre_id": quais["offre_id"],
        "zone_id": quais["zone_id"], "methode": quais["methode"],
        "distance_m": quais["distance_m"], "desservi": quais["desservi"],
    }).reset_index(drop=True)

    compte = correspondances.groupby("offre_id").agg(
        n_quais=("id_origine", "size"), n_quais_desservis=("desservi", "sum"))
    lignes_zone = pd.concat([
        zones.reset_index().assign(offre_id=lambda t: "bus_" + source_id + "_" + t["stop_id"]),
        quais[quais["methode"] == "aucune"].drop(columns=["zone_id", "methode", "distance_m"]),
    ], ignore_index=True)
    lignes_zone = lignes_zone[lignes_zone["offre_id"].isin(compte.index)].merge(
        compte, left_on="offre_id", right_index=True)
    lignes_zone = gpd.GeoDataFrame(lignes_zone, geometry="geometry", crs=stops.crs)

    lignes_zone = suivi.exclure(lignes_zone, lignes_zone["n_quais_desservis"] == 0, "RC-05",
                                "zone d'arrêt sans aucun quai desservi", etape)
    offre = lignes_zone[lignes_zone["statut_transformation"] != "exclu"].copy()
    offre["mode"] = "bus"
    offre["nom"] = offre["stop_name"]
    offre["statut_transformation"] = "fusionne"
    colonnes = ["offre_id", "mode", "source_id", "id_origine", "nom", "nom_normalise",
                "lat_wgs84", "lon_wgs84", "n_quais", "n_quais_desservis",
                "fichier_origine", "sha256_origine", "date_donnee", "run_id",
                "statut_transformation", "regles_appliquees", "qualite", "geometry"]
    return gpd.GeoDataFrame(offre[colonnes], geometry="geometry", crs=stops.crs), correspondances


def controler_correspondances(stops: gpd.GeoDataFrame, correspondances: pd.DataFrame) -> None:
    """CS-07 : chaque quai apparaît exactement une fois dans les correspondances."""
    quais = set(stops.loc[stops["location_type"] == "0", "stop_id"])
    if correspondances["id_origine"].duplicated().any():
        raise RuntimeError("CS-07 : un quai apparaît plusieurs fois dans les correspondances.")
    if set(correspondances["id_origine"]) != quais:
        raise RuntimeError("CS-07 : quais manquants ou en trop dans les correspondances.")
