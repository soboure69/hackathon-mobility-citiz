"""Ingestion Bronze d'un flux GBFS : l'index gbfs.json, puis les flux retenus."""
from __future__ import annotations

import json
from pathlib import Path

from src.ingestion.http_download import telecharger_avec_essais

FLUX_RETENUS = ("system_information", "station_information")


def lire_json(chemin: Path | str) -> dict:
    with Path(chemin).open(encoding="utf-8") as fichier:
        contenu = json.load(fichier)
    if not isinstance(contenu, dict):
        raise ValueError(f"JSON inattendu (pas un objet) : {chemin}")
    return contenu


def lister_flux(index: dict) -> dict[str, str]:
    """Nom → URL des flux annoncés. v3 : data.feeds ; v1 et v2 : data.<langue>.feeds."""
    data = index.get("data")
    if not isinstance(data, dict):
        raise ValueError("gbfs.json sans bloc `data`.")
    if "feeds" in data:
        flux = data["feeds"]
    else:
        if not data:
            raise ValueError("gbfs.json : aucune langue dans `data`.")
        langue = "fr" if "fr" in data else sorted(data)[0]
        flux = data[langue].get("feeds", [])
    return {f["name"]: f["url"] for f in flux if isinstance(f, dict) and "name" in f and "url" in f}


def controler_stations(station_information: dict) -> list[dict[str, object]]:
    """Contrôles minimums sur station_information (sans rien modifier)."""
    stations = station_information.get("data", {}).get("stations", [])
    n = len(stations)
    coord = sum(1 for s in stations
                if isinstance(s.get("lat"), (int, float)) and isinstance(s.get("lon"), (int, float)))
    capacite = sum(1 for s in stations if s.get("capacity") is not None)
    return [
        {"id": "nb_stations", "resultat": "ok" if n > 0 else "echec", "valeur": n},
        {"id": "stations_coordonnees", "resultat": "ok" if n and coord == n else "alerte", "valeur": f"{coord}/{n}"},
        {"id": "stations_capacite", "resultat": "ok" if n and capacite == n else "alerte", "valeur": f"{capacite}/{n}"},
    ]


def ingerer_gbfs(url_index: str, dossier: Path | str, **options) -> tuple[list, dict, list]:
    """Télécharge gbfs.json puis les FLUX_RETENUS. Renvoie (fichiers, version_producteur, contrôles).

    `options` est transmis à telecharger_avec_essais (session, essais, delai…).
    """
    dossier = Path(dossier)
    fichiers: list[dict] = []
    controles: list[dict] = []

    description_index = telecharger_avec_essais(url_index, dossier, **options)
    fichiers.append(description_index)
    index = lire_json(dossier / description_index["nom"])
    flux = lister_flux(index)

    version = {
        "version": index.get("version"),
        "ttl": index.get("ttl"),
        "flux_annonces": sorted(flux),
        "last_updated": {description_index["nom"]: index.get("last_updated")},
    }
    controles.append({"id": "version_gbfs", "resultat": "ok" if index.get("version") else "alerte",
                      "valeur": index.get("version")})

    for nom_flux in FLUX_RETENUS:
        if nom_flux not in flux:
            controles.append({"id": f"flux_{nom_flux}", "resultat": "echec", "valeur": "absent de gbfs.json"})
            continue
        description = telecharger_avec_essais(flux[nom_flux], dossier, **options)
        fichiers.append(description)
        contenu = lire_json(dossier / description["nom"])
        version["last_updated"][description["nom"]] = contenu.get("last_updated")
        controles.append({"id": f"flux_{nom_flux}", "resultat": "ok", "valeur": description["nom"]})
        if nom_flux == "station_information":
            controles.extend(controler_stations(contenu))

    return fichiers, version, controles
