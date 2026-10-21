"""Ingestion Bronze du réseau piéton OpenStreetMap, via OSMnx (API Overpass)."""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import networkx as nx
import osmnx as ox

PARAMETRES_GRAPHE = {"network_type": "walk", "simplify": True, "retain_all": True}


def construire_emprise(contour_2154: gpd.GeoDataFrame, tampon_m: float) -> gpd.GeoDataFrame:
    """Contour élargi de `tampon_m` mètres (calcul en Lambert-93), rendu en EPSG:4326 pour Overpass."""
    if tampon_m < 0:
        raise ValueError("Le tampon doit être positif ou nul.")
    geometrie = contour_2154.geometry.union_all().buffer(tampon_m)
    emprise = gpd.GeoDataFrame({"tampon_m": [tampon_m]}, geometry=[geometrie], crs=contour_2154.crs)
    return emprise.to_crs(4326)


def ecrire_emprise(emprise_4326: gpd.GeoDataFrame, chemin: Path | str) -> None:
    """Écrit l'emprise de la requête en GeoJSON. Refuse d'écraser (Bronze immuable)."""
    with Path(chemin).open("x", encoding="utf-8", newline="\n") as fichier:
        fichier.write(emprise_4326.to_json())


def telecharger_graphe_pieton(emprise_4326: gpd.GeoDataFrame, chemin_graphml: Path | str) -> dict[str, int]:
    """Interroge Overpass sur l'emprise et sauvegarde le graphe tel que reçu, sans le corriger."""
    chemin = Path(chemin_graphml)
    if chemin.exists():
        raise FileExistsError(f"Déjà présent : {chemin}")
    ox.settings.use_cache = False  # réponse fraîche, et non un cache local d'une date inconnue
    graphe = ox.graph_from_polygon(emprise_4326.geometry.iloc[0], **PARAMETRES_GRAPHE)
    ox.save_graphml(graphe, chemin)
    return {
        "nb_noeuds": graphe.number_of_nodes(),
        "nb_aretes": graphe.number_of_edges(),
        "nb_composantes": nx.number_weakly_connected_components(graphe),
    }
