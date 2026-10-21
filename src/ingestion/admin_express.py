"""Contrôles de lecture d'ADMIN EXPRESS : le GeoPackage est extrait dans un
dossier temporaire du système, lu, puis supprimé. Rien n'est écrit dans data/."""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

import geopandas as gpd
import py7zr
import pyogrio

MOTIF_SIREN = re.compile(r"\d{9}")


def _extraire_gpkg(chemin_7z: Path | str, dossier: Path | str) -> Path:
    """Extrait l'unique GeoPackage de l'archive dans `dossier` et renvoie son chemin."""
    with py7zr.SevenZipFile(chemin_7z, "r") as archive:
        gpkg = [n for n in archive.getnames() if n.lower().endswith(".gpkg")]
        if len(gpkg) != 1:
            raise ValueError(f"Un seul GeoPackage attendu dans l'archive, trouvé : {gpkg}")
        archive.extract(path=dossier, targets=gpkg)
    return Path(dossier) / gpkg[0]


def controler_admin_express(chemin_7z: Path | str, siren_epci: str, nb_communes_attendu: int) -> list[dict]:
    with tempfile.TemporaryDirectory() as temporaire:
        try:
            chemin = _extraire_gpkg(chemin_7z, temporaire)
        except ValueError as erreur:
            return [{"id": "gpkg_unique", "resultat": "echec", "valeur": str(erreur)}]

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


def lire_contour_epci(chemin_7z: Path | str, siren_epci: str) -> gpd.GeoDataFrame:
    """Contour de l'EPCI, lu dans la couche `epci` (colonne `code_siren` constatée à S04)."""
    if not MOTIF_SIREN.fullmatch(siren_epci):
        raise ValueError(f"SIREN invalide : {siren_epci!r}")
    with tempfile.TemporaryDirectory() as temporaire:
        chemin = _extraire_gpkg(chemin_7z, temporaire)
        contour = pyogrio.read_dataframe(chemin, layer="epci", where=f"code_siren = '{siren_epci}'")
    if len(contour) != 1:
        raise ValueError(f"EPCI {siren_epci} : {len(contour)} contour(s), 1 attendu.")
    if contour.crs is None or contour.crs.to_epsg() != 2154:
        raise ValueError(f"CRS inattendu pour le contour : {contour.crs}")
    return contour
