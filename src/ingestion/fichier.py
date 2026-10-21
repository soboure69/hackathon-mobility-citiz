"""Ingestion Bronze d'une ressource unique : téléchargement et contrôle d'archive."""
from __future__ import annotations

import zipfile
from pathlib import Path

import py7zr

from src.ingestion.http_download import telecharger_avec_essais


def controler_archive(chemin: Path | str) -> list[dict[str, object]]:
    """Archive lisible et intègre (sommes de contrôle internes), et liste de son contenu."""
    chemin = Path(chemin)
    suffixe = chemin.suffix.lower()
    if suffixe == ".zip":
        with zipfile.ZipFile(chemin) as archive:
            noms, corrompu = archive.namelist(), archive.testzip()
    elif suffixe == ".7z":
        with py7zr.SevenZipFile(chemin, "r") as archive:
            noms = archive.getnames()
        with py7zr.SevenZipFile(chemin, "r") as archive:
            corrompu = archive.testzip()
    else:
        return [{"id": "archive", "resultat": "ok", "valeur": "pas une archive"}]
    return [
        {"id": "archive_integre", "resultat": "ok" if corrompu is None else "echec",
         "valeur": corrompu or f"{len(noms)} entrées"},
        {"id": "contenu_archive", "resultat": "ok", "valeur": noms},
    ]


def ingerer_fichier(url: str, dossier: Path | str, *, taille_annoncee: int | None = None,
                    **options) -> tuple[list, dict, list]:
    """Télécharge une ressource unique. Renvoie (fichiers, version_producteur, contrôles)."""
    description = telecharger_avec_essais(url, dossier, **options)
    controles: list[dict] = []
    if taille_annoncee is not None:
        controles.append({
            "id": "taille_annoncee",
            "resultat": "ok" if description["taille_octets"] == taille_annoncee else "alerte",
            "valeur": f"{description['taille_octets']} reçus / {taille_annoncee} annoncés",
        })
    controles.extend(controler_archive(Path(dossier) / description["nom"]))
    version = {"last_modified": description.get("last_modified"), "etag": description.get("etag")}
    return [description], version, controles
