"""Téléchargement vers la couche Bronze : dossiers datés et fichiers."""
from __future__ import annotations

import re
import time
from collections.abc import Mapping
from datetime import date, datetime
from email.message import Message
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import requests

from src.utils.manifest import decrire_fichier

FAMILLES = (
    "gtfs", "gbfs", "insee_filosofi", "insee_omphale",
    "admin_express", "osm", "external",
)
TERRITOIRES = ("larochelle", "angers", "poitiers", "nantes", "rennes", "national")
MOTIF_SOURCE_ID = re.compile(r"S\d{2}[a-z]?")
EXTENSIONS_PAR_TYPE = {
    "application/json": ".json",
    "text/html": ".html",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
    "text/csv": ".csv",
}
CARACTERES_INTERDITS = set('<>:"/\\|?*')
TAILLE_BLOC = 1024 * 1024  # 1 Mo
DELAI_PAR_DEFAUT = (10, 60)  # secondes : (connexion, lecture)
EN_TETES_PAR_DEFAUT = {
    "User-Agent": "hackathon-mobility-citiz/0.1 (projet etudiant Epitech x Citiz)",
}
ERREURS_PASSAGERES = (
    requests.ConnectionError,
    requests.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


def creer_dossier_date(
    racine_bronze: Path | str,
    famille: str,
    territoire: str,
    source_id: str,
    jour: date,
    suffixe: int | None = None,
) -> Path:
    """Crée le dossier daté d'une source dans Bronze et renvoie son chemin.

    Refuse si le dossier existe déjà : Bronze est immuable. Pour un second
    téléchargement le même jour, passer suffixe=2 (puis 3…).
    """
    if famille not in FAMILLES:
        raise ValueError(f"Famille inconnue : {famille!r}")
    if territoire not in TERRITOIRES:
        raise ValueError(f"Territoire inconnu : {territoire!r}")
    if not MOTIF_SOURCE_ID.fullmatch(source_id):
        raise ValueError(f"source_id invalide : {source_id!r}")
    if isinstance(jour, datetime) or not isinstance(jour, date):
        raise TypeError("`jour` doit être une date (sans heure).")
    if suffixe is not None and suffixe < 2:
        raise ValueError("Le suffixe commence à 2 : le premier dossier n'en a pas.")

    nom = f"{source_id}_{jour.isoformat()}"
    if suffixe is not None:
        nom += f"_{suffixe}"

    dossier = Path(racine_bronze) / famille / territoire / nom
    dossier.mkdir(parents=True, exist_ok=False)
    return dossier


def _en_tete(en_tetes: Mapping[str, str], nom: str) -> str | None:
    """Lit un en-tête HTTP sans tenir compte des majuscules."""
    for cle, valeur in en_tetes.items():
        if cle.lower() == nom.lower():
            return valeur
    return None


def nom_fichier_depuis_reponse(url_effective: str, en_tetes: Mapping[str, str]) -> str:
    """Nom d'origine d'un fichier téléchargé, sans jamais l'inventer.

    1. Content-Disposition ; 2. dernier segment de l'URL finale ;
    3. si aucune extension : extension tirée du Content-Type, pour les seuls
       types de EXTENSIONS_PAR_TYPE.
    """
    nom = None
    disposition = _en_tete(en_tetes, "Content-Disposition")
    if disposition:
        message = Message()
        message["Content-Disposition"] = disposition
        nom = message.get_filename()
    if not nom:
        nom = unquote(PurePosixPath(urlsplit(url_effective).path).name)

    # Ne garder que le nom : un serveur ne doit jamais choisir le dossier.
    nom = PurePosixPath(nom.replace("\\", "/")).name
    if not nom or nom in {".", ".."} or any(c in CARACTERES_INTERDITS for c in nom):
        raise ValueError(f"Nom de fichier inutilisable : {nom!r} (URL : {url_effective})")

    if not PurePosixPath(nom).suffix:
        type_contenu = (_en_tete(en_tetes, "Content-Type") or "").split(";")[0].strip().lower()
        nom += EXTENSIONS_PAR_TYPE.get(type_contenu, "")
    return nom


def telecharger_fichier(
    url: str,
    dossier: Path | str,
    *,
    session: requests.Session | None = None,
    delai: tuple[float, float] = DELAI_PAR_DEFAUT,
) -> dict[str, object]:
    """Télécharge `url` dans `dossier`, sous son nom d'origine.

    Écrit d'abord dans <nom>.part, puis renomme : un fichier interrompu
    ne prend jamais son nom définitif. Renvoie la description du fichier
    (nom, taille, sha256) complétée des informations HTTP.
    """
    dossier = Path(dossier)
    if not dossier.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {dossier}")

    client = session if session is not None else requests
    with client.get(url, stream=True, timeout=delai, headers=EN_TETES_PAR_DEFAUT) as reponse:
        reponse.raise_for_status()
        nom = nom_fichier_depuis_reponse(reponse.url, reponse.headers)

        destination = dossier / nom
        if destination.exists():
            raise FileExistsError(f"Déjà présent dans le dossier : {destination}")

        partiel = dossier / f"{nom}.part"
        fichier = partiel.open("xb")
        try:
            with fichier:
                for bloc in reponse.iter_content(chunk_size=TAILLE_BLOC):
                    fichier.write(bloc)
            partiel.rename(destination)
        except BaseException:
            partiel.unlink(missing_ok=True)
            raise

        description = decrire_fichier(destination)
        description.update(
            content_type=reponse.headers.get("Content-Type"),
            http_status=reponse.status_code,
            url_demandee=url,
            url_effective=reponse.url,
        )
    return description


def _est_passagere(erreur: Exception) -> bool:
    """Vrai si l'erreur peut disparaître en réessayant plus tard."""
    if isinstance(erreur, ERREURS_PASSAGERES):
        return True
    if isinstance(erreur, requests.HTTPError) and erreur.response is not None:
        code = erreur.response.status_code
        return code == 429 or code >= 500
    return False


def telecharger_avec_essais(
    url: str,
    dossier: Path | str,
    *,
    essais: int = 3,
    attente_initiale: float = 2.0,
    session: requests.Session | None = None,
    delai: tuple[float, float] = DELAI_PAR_DEFAUT,
    attendre=time.sleep,
) -> dict[str, object]:
    """Appelle telecharger_fichier, en réessayant les seules erreurs passagères.

    Pause entre deux essais : attente_initiale, puis le double, etc.
    `attendre` est remplaçable pour tester sans attendre réellement.
    """
    if essais < 1:
        raise ValueError("Il faut au moins un essai.")

    for numero in range(1, essais + 1):
        try:
            description = telecharger_fichier(url, dossier, session=session, delai=delai)
        except Exception as erreur:
            if numero == essais or not _est_passagere(erreur):
                raise
            attendre(attente_initiale * 2 ** (numero - 1))
        else:
            description["tentatives"] = numero
            return description

    raise AssertionError("Point jamais atteint")  # chaque tour renvoie ou lève
