"""Réseau piéton OSM (S05) : nœuds et arêtes en Lambert-93.

RC-13 : arête de longueur nulle ou absente, extrémité inconnue, nœud sans coordonnées → rejet.
RC-01 : `motorroad=yes` sans `foot` explicite → rejet, SI ces tags sont dans le graphe.
        Sinon : constat « non applicable » et arêtes trunk / trunk_link signalées.
RC-15 : `highway=busway` (voie réservée aux bus) → exclue du réseau piéton.
RC-16 : `access=no` (hors busway) → alerte, arête gardée (le tag `foot` n'est pas connu).
Q7    : composante principale marquée ; aucune arête ni aucun nœud n'est supprimé pour ce motif.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd

from src.cleaning.audit import Suivi, ajouter_audit

FOOT_AUTORISE = {"yes", "designated", "permissive"}


def _texte(valeur: object) -> str | None:
    """Les attributs OSMnx peuvent être des listes (arêtes fusionnées) : on les écrit « a;b »."""
    if isinstance(valeur, (list, tuple, set)):
        return ";".join(str(v) for v in valeur)
    if valeur is None or (isinstance(valeur, float) and pd.isna(valeur)):
        return None
    return str(valeur)


def charger_graphe(chemin: Path | str) -> nx.MultiDiGraph:
    return ox.load_graphml(chemin)


def standardiser_reseau(graphe: nx.MultiDiGraph, **audit) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    composantes = sorted(nx.weakly_connected_components(graphe), key=len, reverse=True)
    numero = {noeud: i for i, composante in enumerate(composantes) for noeud in composante}
    noeuds, aretes = ox.graph_to_gdfs(graphe)

    noeuds = noeuds.reset_index().rename(columns={"osmid": "node_id"})
    noeuds["lon_wgs84"], noeuds["lat_wgs84"] = noeuds["x"], noeuds["y"]
    noeuds["composante"] = noeuds["node_id"].map(numero).astype("Int64")
    noeuds["composante_principale"] = noeuds["composante"] == 0
    noeuds["highway"] = noeuds["highway"].map(_texte).astype("string") if "highway" in noeuds else pd.NA
    noeuds = noeuds[["node_id", "lon_wgs84", "lat_wgs84", "street_count", "highway",
                     "composante", "composante_principale", "geometry"]]
    noeuds = ajouter_audit(noeuds, id_origine=noeuds["node_id"].astype("string"), **audit)

    aretes = aretes.reset_index()
    texte = [c for c in ("osmid", "highway", "name", "access", "service", "reversed",
                         "motorroad", "foot", "sidewalk") if c in aretes.columns]
    for colonne in texte:
        aretes[colonne] = aretes[colonne].map(_texte).astype("string")
    aretes["length_m"] = pd.to_numeric(aretes["length"], errors="coerce")
    aretes["composante"] = aretes["u"].map(numero).astype("Int64")
    aretes = aretes[["u", "v", "key", *texte, "oneway", "length_m", "composante", "geometry"]]
    id_arete = aretes["u"].astype(str) + "-" + aretes["v"].astype(str) + "-" + aretes["key"].astype(str)
    aretes = ajouter_audit(aretes, id_origine=id_arete.astype("string"), **audit)
    return (gpd.GeoDataFrame(noeuds, geometry="geometry", crs=graphe.graph["crs"]).to_crs(2154),
            gpd.GeoDataFrame(aretes, geometry="geometry", crs=graphe.graph["crs"]).to_crs(2154))


def _contient(colonne: pd.Series, valeur: str) -> pd.Series:
    return colonne.fillna("").str.split(";").map(lambda l: valeur in l)


def nettoyer_reseau(noeuds: gpd.GeoDataFrame, aretes: gpd.GeoDataFrame, suivi: Suivi) -> tuple:
    """Renvoie (nœuds, arêtes, statut_rc01)."""
    etape = "cleaned"
    noeuds = suivi.rejeter(noeuds, noeuds["lon_wgs84"].isna() | noeuds["lat_wgs84"].isna(),
                           "RC-13", "nœud sans coordonnées", etape)
    connus = set(noeuds["node_id"])
    aretes = suivi.rejeter(aretes, ~(aretes["length_m"] > 0), "RC-13", "longueur nulle ou absente", etape, "length_m")
    aretes = suivi.rejeter(aretes, ~aretes["u"].isin(connus) | ~aretes["v"].isin(connus),
                           "RC-13", "extrémité inconnue", etape)

    if "motorroad" in aretes.columns:
        foot = aretes["foot"] if "foot" in aretes.columns else pd.Series(pd.NA, index=aretes.index, dtype="string")
        interdite = _contient(aretes["motorroad"], "yes") & ~foot.fillna("").isin(FOOT_AUTORISE)
        aretes = suivi.rejeter(aretes, interdite, "RC-01", "motorroad=yes sans foot explicite", etape, "highway")
        statut_rc01 = "appliquée"
    else:
        voie_rapide = _contient(aretes["highway"], "trunk") | _contient(aretes["highway"], "trunk_link")
        aretes = suivi.signaler(aretes, voie_rapide, "RC-01",
                                "tag motorroad absent du graphe : voie rapide (trunk) signalée", etape, "highway")
        statut_rc01 = "non applicable : tags motorroad et foot absents du graphe"

    bus = _contient(aretes["highway"], "busway")
    aretes = suivi.exclure(aretes, bus, "RC-15", "voie réservée aux bus (highway=busway)", etape, "highway")
    aretes = suivi.signaler(aretes, _contient(aretes["access"], "no") & ~bus,
                            "RC-16", "access=no (tag foot inconnu)", etape, "highway")
    return noeuds, aretes, statut_rc01
