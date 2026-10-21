"""Étape silver/spatial : rattachement des carreaux et des options au réseau piéton.

- Réseau routable : arêtes non exclues (RC-15), graphe non orienté, plus grande composante.
- Rattachement : nœud routable le plus proche, distance à vol d'oiseau en Lambert-93.
  Cette distance d'accès fera partie du budget de marche (elle n'est pas un seuil arbitraire).
- RG-05 : `dans_emprise` (contour de l'EPCI élargi du tampon S05) ; marqueur, aucune ligne retirée.
- RG-08 : rattachement plus long que le budget de marche → alerte.
"""
from __future__ import annotations

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely import STRtree

from src.cleaning.audit import Suivi

COLONNES_OFFRE = ["offre_id", "mode", "source_id", "id_origine", "nom", "nom_normalise",
                  "lat_wgs84", "lon_wgs84", "capacite", "n_quais", "n_quais_desservis",
                  "fichier_origine", "sha256_origine", "date_donnee", "run_id",
                  "statut_transformation", "regles_appliquees", "qualite", "geometry"]


def noeuds_routables(noeuds: gpd.GeoDataFrame, aretes: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Nœuds de la plus grande composante du réseau sans les arêtes exclues."""
    utilisables = aretes[aretes["statut_transformation"] != "exclu"]
    graphe = nx.Graph()
    graphe.add_edges_from(zip(utilisables["u"], utilisables["v"]))
    principale = max(nx.connected_components(graphe), key=len)
    return noeuds[noeuds["node_id"].isin(principale)].sort_values("node_id").reset_index(drop=True)


def rattacher(points: gpd.GeoSeries, noeuds: gpd.GeoDataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Nœud le plus proche (un seul, déterministe) et distance en mètres."""
    if points.crs is None or points.crs.to_epsg() != 2154 or noeuds.crs.to_epsg() != 2154:
        raise RuntimeError("Rattachement : EPSG:2154 attendu pour les points et les nœuds.")
    arbre = STRtree(noeuds.geometry.values)
    (_, indices), distances = arbre.query_nearest(points.values, return_distance=True, all_matches=False)
    return noeuds["node_id"].to_numpy()[indices], distances


def construire_cellules(carreaux: gpd.GeoDataFrame, territoire: str, noeuds: gpd.GeoDataFrame,
                        suivi: Suivi, distance_max: float, run_id: str) -> gpd.GeoDataFrame:
    cellules = carreaux[carreaux["territoire"] == territoire].copy()
    centroides = cellules.geometry.centroid
    cellules["x_centroide"], cellules["y_centroide"] = centroides.x, centroides.y
    cellules["node_id"], cellules["dist_snap_m"] = rattacher(centroides, noeuds)
    cellules["pop"] = cellules["ind"]
    cellules["run_id"] = run_id
    return suivi.signaler(cellules, cellules["dist_snap_m"] > distance_max, "RG-08",
                          f"centroïde à plus de {distance_max:.0f} m du réseau", "spatial", "dist_snap_m")


def construire_offre_points(offres: list[gpd.GeoDataFrame], noeuds: gpd.GeoDataFrame, emprise,
                            suivi: Suivi, distance_max: float, run_id: str) -> gpd.GeoDataFrame:
    # Union des colonnes ; une colonne propre à un mode reste vide pour les autres.
    morceaux = [o[[c for c in COLONNES_OFFRE if c in o.columns]] for o in offres]
    points = pd.concat(morceaux, ignore_index=True).reindex(columns=COLONNES_OFFRE)
    points = gpd.GeoDataFrame(points, geometry="geometry", crs=offres[0].crs)
    if points["offre_id"].duplicated().any():
        raise RuntimeError("offre_id en double entre modes.")
    points["capacite"] = points["capacite"].astype("Int64")
    points["n_quais"] = points["n_quais"].astype("Int64")
    points["n_quais_desservis"] = points["n_quais_desservis"].astype("Int64")
    points["node_id"], points["dist_snap_m"] = rattacher(points.geometry, noeuds)
    points["dans_emprise"] = points.geometry.within(emprise)
    points["run_id"] = run_id
    return suivi.signaler(points, points["dist_snap_m"] > distance_max, "RG-08",
                          f"option à plus de {distance_max:.0f} m du réseau", "spatial", "dist_snap_m")
