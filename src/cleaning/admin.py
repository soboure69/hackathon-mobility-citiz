"""Admin Express (S04) : communes et EPCI d'étude, en Lambert-93.

RC-11 : géométrie invalide réparée et signalée ; vide rejetée.
RC-12 : nombre de communes par EPCI différent de la grille G2 → arrêt (contradiction avec G2).
"""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

from src.cleaning.audit import Suivi, ajouter_audit
from src.ingestion.admin_express import _extraire_gpkg

MOTIF_SIREN = re.compile(r"\d{9}")
MOTIF_CODE_INSEE = re.compile(r"\b(?:\d{5}|2[AB]\d{3})\b")


def lire_admin(chemin_7z: Path | str, sirens: list[str]) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Couches commune (toutes) et epci (EPCI d'étude), lues hors du dépôt puis libérées."""
    for siren in sirens:
        if not MOTIF_SIREN.fullmatch(siren):
            raise ValueError(f"SIREN invalide : {siren!r}")
    liste = ", ".join(f"'{s}'" for s in sirens)
    with tempfile.TemporaryDirectory() as temporaire:
        gpkg = _extraire_gpkg(chemin_7z, temporaire)
        communes = pyogrio.read_dataframe(gpkg, layer="commune",
                                          columns=["code_insee", "nom_officiel", "codes_siren_des_epci", "population",
                                                   "code_insee_du_departement", "code_insee_de_la_region"])
        epci = pyogrio.read_dataframe(gpkg, layer="epci", where=f"code_siren IN ({liste})",
                                      columns=["code_siren", "nom_officiel", "nature", "codes_insee_des_communes_membres"])
    return communes, epci


def standardiser_admin(communes: gpd.GeoDataFrame, epci: gpd.GeoDataFrame, territoires: dict, **audit):
    """Garde les communes membres d'un EPCI d'étude. Ajoute epci_siren et territoire."""
    par_siren = {r["siren"]: nom for nom, r in territoires.items()}
    sirens = communes["codes_siren_des_epci"].fillna("").map(MOTIF_SIREN.findall)
    etude = sirens.map(lambda l: [s for s in l if s in par_siren])
    if (etude.map(len) > 1).any():
        raise RuntimeError("Une commune appartient à deux EPCI d'étude : cas non prévu.")
    communes = communes[etude.map(len) == 1].copy()
    communes["epci_siren"] = etude[communes.index].map(lambda l: l[0]).astype("string")
    communes["territoire"] = communes["epci_siren"].map(par_siren).astype("string")
    communes["code_insee"] = communes["code_insee"].astype("string")
    communes["code_departement"] = communes.pop("code_insee_du_departement").astype("string")
    communes["code_region"] = communes.pop("code_insee_de_la_region").astype("string")
    communes["population"] = pd.to_numeric(communes["population"], errors="coerce").astype("Int64")
    communes = ajouter_audit(communes, id_origine=communes["code_insee"], **audit)

    epci = epci.copy()
    epci["code_siren"] = epci["code_siren"].astype("string")
    epci["territoire"] = epci["code_siren"].map(par_siren).astype("string")
    epci["n_membres_declares"] = epci["codes_insee_des_communes_membres"].fillna("").map(
        lambda v: len(MOTIF_CODE_INSEE.findall(v))).astype("Int64")
    epci = ajouter_audit(epci, id_origine=epci["code_siren"], **audit)
    return gpd.GeoDataFrame(communes, geometry="geometry", crs=communes.crs), \
        gpd.GeoDataFrame(epci, geometry="geometry", crs=epci.crs)


def reparer_geometries(table: gpd.GeoDataFrame, suivi: Suivi, etape: str) -> gpd.GeoDataFrame:
    """RC-11 : vide → rejet ; invalide → make_valid + alerte (l'information n'est pas changée)."""
    table = suivi.rejeter(table, table.geometry.is_empty | table.geometry.isna(), "RC-11", "géométrie vide", etape)
    invalide = ~table.geometry.is_valid
    table = suivi.signaler(table, invalide, "RC-11", "géométrie invalide, réparée", etape)
    table.loc[invalide, "geometry"] = table.loc[invalide, "geometry"].make_valid()
    table.loc[invalide, "statut_transformation"] = "repare"
    return table


def controler_composition(communes: gpd.GeoDataFrame, epci: gpd.GeoDataFrame, territoires: dict) -> list[dict]:
    """RC-12 / CS-09 : nombre de communes par EPCI = grille G2, et = liste déclarée par la couche epci."""
    constats = []
    for nom, reglage in territoires.items():
        n = int((communes["territoire"] == nom).sum())
        declares = epci.loc[epci["territoire"] == nom, "n_membres_declares"]
        n_declares = int(declares.iloc[0]) if len(declares) else None
        if n != reglage["nb_communes"] or n_declares != reglage["nb_communes"]:
            raise RuntimeError(f"RC-12 {nom} : {n} communes (couche commune), {n_declares} (couche epci), "
                               f"{reglage['nb_communes']} attendues (G2).")
        constats.append({"territoire": nom, "communes": n, "declares_epci": n_declares})
    if len(epci) != len(territoires):
        raise RuntimeError(f"RC-12 : {len(epci)} contours EPCI pour {len(territoires)} territoires.")
    return constats
