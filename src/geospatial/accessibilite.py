"""Relations carreau × option à moins de 5 min de marche (table de paires, Gold).

Méthode réseau : accès carreau (vol d'oiseau) + plus court chemin piéton + accès option ≤ budget.
Méthode vol d'oiseau (repli MVP, et variables H6) : distance centroïde → option ≤ budget.
Variante « sans_trunk » : réseau privé des arêtes signalées par RC-01 (sensibilité, option B).
Aucun KPI n'est calculé ici : la table décrit seulement qui atteint quoi, et à quelle distance.
"""
from __future__ import annotations

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely import STRtree

COLONNES = ["cell_id", "offre_id", "mode", "methode", "variante", "dist_acces_cellule_m",
            "dist_reseau_m", "dist_acces_option_m", "dist_totale_m"]


def graphe_routable(aretes: gpd.GeoDataFrame, sans_trunk: bool = False) -> nx.Graph:
    """Graphe non orienté pondéré par length_m, sans arêtes exclues (RC-15), sans RC-01 si demandé."""
    utilisables = aretes[aretes["statut_transformation"] != "exclu"]
    if sans_trunk:
        utilisables = utilisables[~utilisables["regles_appliquees"].fillna("").str.contains("RC-01")]
    graphe = nx.Graph()
    for u, v, longueur in zip(utilisables["u"], utilisables["v"], utilisables["length_m"]):
        if not graphe.has_edge(u, v) or longueur < graphe[u][v]["length"]:
            graphe.add_edge(u, v, length=float(longueur))
    return graphe


def paires_reseau(cellules: pd.DataFrame, offres: pd.DataFrame, graphe: nx.Graph,
                  budget: float, variante: str) -> pd.DataFrame:
    """Un plus court chemin borné par option : on part de l'option et on remonte vers les carreaux."""
    par_noeud: dict = {}
    for cell_id, noeud, acces in zip(cellules["cell_id"], cellules["node_id"], cellules["dist_snap_m"]):
        par_noeud.setdefault(noeud, []).append((cell_id, float(acces)))
    lignes = []
    for offre in offres.itertuples(index=False):
        reste = budget - float(offre.dist_snap_m)
        if reste < 0 or offre.node_id not in graphe:
            continue
        distances = nx.single_source_dijkstra_path_length(graphe, offre.node_id, cutoff=reste, weight="length")
        for noeud, reseau in distances.items():
            for cell_id, acces in par_noeud.get(noeud, ()):
                total = acces + reseau + float(offre.dist_snap_m)
                if total <= budget:
                    lignes.append((cell_id, offre.offre_id, offre.mode, "reseau", variante,
                                   acces, reseau, float(offre.dist_snap_m), total))
    paires = pd.DataFrame(lignes, columns=COLONNES)
    for colonne in COLONNES[5:]:
        paires[colonne] = paires[colonne].astype("Float64")
    return paires


def paires_vol_oiseau(cellules: pd.DataFrame, offres: gpd.GeoDataFrame, budget: float) -> pd.DataFrame:
    """Repli sans réseau : centroïde du carreau → point de l'option, à vol d'oiseau."""
    centroides = gpd.points_from_xy(cellules["x_centroide"], cellules["y_centroide"], crs=offres.crs)
    arbre = STRtree(offres.geometry.values)
    i_cellule, i_offre = arbre.query(centroides, predicate="dwithin", distance=budget)
    distances = gpd.GeoSeries(centroides[i_cellule], crs=offres.crs).distance(
        gpd.GeoSeries(offres.geometry.values[i_offre], crs=offres.crs))
    vide = pd.Series(pd.NA, index=range(len(i_cellule)), dtype="Float64")
    return pd.DataFrame({
        "cell_id": cellules["cell_id"].to_numpy()[i_cellule], "offre_id": offres["offre_id"].to_numpy()[i_offre],
        "mode": offres["mode"].to_numpy()[i_offre], "methode": "vol_oiseau", "variante": "reference",
        "dist_acces_cellule_m": vide, "dist_reseau_m": vide, "dist_acces_option_m": vide,
        "dist_totale_m": pd.Series(distances.to_numpy(), dtype="Float64"),
    })[COLONNES]
