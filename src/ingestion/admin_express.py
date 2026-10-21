"""Contrôles de lecture d'ADMIN EXPRESS : le GeoPackage est extrait dans un
dossier temporaire du système, lu, puis supprimé. Rien n'est écrit dans data/."""
from __future__ import annotations

import tempfile
from pathlib import Path

import py7zr
import pyogrio


def controler_admin_express(chemin_7z: Path | str, siren_epci: str, nb_communes_attendu: int) -> list[dict]:
    with tempfile.TemporaryDirectory() as temporaire:
        with py7zr.SevenZipFile(chemin_7z, "r") as archive:
            gpkg = [n for n in archive.getnames() if n.lower().endswith(".gpkg")]
            if len(gpkg) != 1:
                return [{"id": "gpkg_unique", "resultat": "echec", "valeur": gpkg}]
            archive.extract(path=temporaire, targets=gpkg)
        chemin = Path(temporaire) / gpkg[0]

        couches = [str(nom) for nom, _ in pyogrio.list_layers(chemin)]
        controles = [{"id": "couches", "resultat": "ok", "valeur": couches}]
        for couche in couches:
            if couche.lower() not in ("epci", "commune"):
                continue
            info = pyogrio.read_info(chemin, layer=couche)
            table = pyogrio.read_dataframe(chemin, layer=couche, read_geometry=False)
            # On ne suppose pas le nom de la colonne SIREN : on cherche où apparaît la valeur.
            colonnes = [c for c in table.columns if (table[c].astype(str) == siren_epci).any()]
            n = int((table[colonnes[0]].astype(str) == siren_epci).sum()) if colonnes else 0
            attendu = 1 if couche.lower() == "epci" else nb_communes_attendu
            controles.append({
                "id": f"couche_{couche.lower()}",
                "resultat": "ok" if n == attendu else "echec",
                "valeur": {"entites": int(info["features"]), "crs": str(info["crs"]),
                           "colonnes": [str(c) for c in table.columns],
                           "colonnes_contenant_siren": colonnes,
                           "lignes_siren": n, "attendu": attendu},
            })
    return controles
