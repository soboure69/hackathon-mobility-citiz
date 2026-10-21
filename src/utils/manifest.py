"""Traçabilité de la couche Bronze : empreintes et manifestes."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

TAILLE_BLOC = 1024 * 1024  # 1 Mo lu à la fois

NOM_MANIFESTE = "_manifest.json"

CHAMPS_OBLIGATOIRES = (
    "source_id", "nom", "run_id", "date_heure",
    "url_demandee", "url_effective", "http_status",
    "fichiers", "version_producteur",
    "licence_registre", "licence_constatee",
    "outil", "parametres", "controles", "statut_ingestion",
)

STATUTS_INGESTION = ("reussie", "reussie_avec_alertes", "echouee")


def calculer_sha256(chemin: Path | str) -> str:
    """Renvoie l'empreinte SHA-256 d'un fichier, en hexadécimal.

    Le fichier est lu par blocs : la mémoire utilisée reste faible,
    même pour un fichier de plusieurs centaines de Mo.
    """
    chemin = Path(chemin)
    empreinte = hashlib.sha256()
    with chemin.open("rb") as fichier:
        for bloc in iter(lambda: fichier.read(TAILLE_BLOC), b""):
            empreinte.update(bloc)
    return empreinte.hexdigest()


def decrire_fichier(chemin: Path | str) -> dict[str, object]:
    """Décrit un fichier pour le manifeste : nom, taille en octets, empreinte.

    Le nom est celui du fichier seul : le manifeste est rangé dans le même
    dossier, donc le chemin complet est inutile et dépendrait de la machine.
    """
    chemin = Path(chemin)
    if not chemin.is_file():
        raise FileNotFoundError(f"Introuvable, ou n'est pas un fichier : {chemin}")
    return {
        "nom": chemin.name,
        "taille_octets": chemin.stat().st_size,
        "sha256": calculer_sha256(chemin),
    }


def lire_commit_git(dossier: Path | str = ".") -> str:
    """Hash court du commit courant.

    Suffixe « -modifie » si des fichiers suivis par Git ont des modifications
    non commitées : le code exécuté n'est alors pas exactement ce commit.
    """
    def git(*arguments: str) -> str:
        resultat = subprocess.run(
            ["git", *arguments],
            cwd=dossier,
            capture_output=True,
            text=True,
            check=True,
        )
        return resultat.stdout.strip()

    commit = git("rev-parse", "--short", "HEAD")
    if git("status", "--porcelain", "--untracked-files=no"):
        commit += "-modifie"
    return commit


def construire_run_id(maintenant: datetime | None = None, commit: str | None = None) -> str:
    """Identifiant d'exécution : AAAAMMJJTHHMMSSZ_<commit>, horodaté en UTC.

    `maintenant` et `commit` peuvent être fournis pour obtenir un résultat
    déterministe (tests). Sinon, on prend l'heure courante et le commit Git.
    """
    if maintenant is None:
        maintenant = datetime.now(timezone.utc)
    if maintenant.tzinfo is None:
        raise ValueError("La date doit porter un fuseau horaire.")
    horodatage = maintenant.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if commit is None:
        commit = lire_commit_git()
    return f"{horodatage}_{commit}"


def valider_contenu(contenu: dict[str, object]) -> None:
    """Vérifie qu'un contenu de manifeste respecte le format. Lève ValueError sinon."""
    manquants = [champ for champ in CHAMPS_OBLIGATOIRES if champ not in contenu]
    if manquants:
        raise ValueError(f"Champs manquants dans le manifeste : {manquants}")

    statut = contenu["statut_ingestion"]
    if statut not in STATUTS_INGESTION:
        raise ValueError(f"statut_ingestion invalide : {statut!r}")

    fichiers = contenu["fichiers"]
    if not isinstance(fichiers, list):
        raise ValueError("`fichiers` doit être une liste.")
    if not fichiers and statut != "echouee":
        raise ValueError("`fichiers` est vide alors que l'ingestion n'a pas échoué.")
    for entree in fichiers:
        if not isinstance(entree, dict) or not {"nom", "taille_octets", "sha256"} <= entree.keys():
            raise ValueError(f"Entrée de `fichiers` incomplète : {entree!r}")


def ecrire_manifeste(dossier: Path | str, contenu: dict[str, object]) -> Path:
    """Écrit _manifest.json dans `dossier`. Refuse d'écraser un manifeste existant.

    Un champ peut valoir None (par exemple `parametres` hors OSM),
    mais il doit être présent.
    """
    dossier = Path(dossier)
    if not dossier.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {dossier}")

    valider_contenu(contenu)

    texte = json.dumps(contenu, ensure_ascii=False, indent=2) + "\n"
    chemin = dossier / NOM_MANIFESTE
    with chemin.open("x", encoding="utf-8", newline="\n") as fichier:
        fichier.write(texte)
    return chemin


def lire_manifeste(dossier: Path | str) -> dict[str, object]:
    """Lit et valide le _manifest.json d'un dossier Bronze."""
    chemin = Path(dossier) / NOM_MANIFESTE
    with chemin.open(encoding="utf-8") as fichier:
        contenu = json.load(fichier)
    if not isinstance(contenu, dict):
        raise ValueError(f"Le manifeste n'est pas un objet JSON : {chemin}")
    valider_contenu(contenu)
    return contenu


def verifier_manifeste(dossier: Path | str) -> list[dict[str, object]]:
    """Compare les fichiers d'un dossier Bronze à son manifeste.

    Renvoie la liste des anomalies : une liste vide signifie « conforme ».
    """
    dossier = Path(dossier)
    contenu = lire_manifeste(dossier)
    anomalies: list[dict[str, object]] = []
    noms_listes: set[str] = set()

    for entree in contenu["fichiers"]:
        nom = entree["nom"]
        noms_listes.add(nom)
        chemin = dossier / nom

        if not chemin.is_file():
            anomalies.append({"fichier": nom, "probleme": "absent",
                              "attendu": "présent", "constate": "absent"})
            continue

        taille = chemin.stat().st_size
        if taille != entree["taille_octets"]:
            anomalies.append({"fichier": nom, "probleme": "taille",
                              "attendu": entree["taille_octets"], "constate": taille})
            continue

        empreinte = calculer_sha256(chemin)
        if empreinte != str(entree["sha256"]).lower():
            anomalies.append({"fichier": nom, "probleme": "sha256",
                              "attendu": entree["sha256"], "constate": empreinte})

    for chemin in sorted(dossier.iterdir()):
        if chemin.name != NOM_MANIFESTE and chemin.name not in noms_listes:
            anomalies.append({"fichier": chemin.name, "probleme": "non_liste",
                              "attendu": "absent", "constate": "présent"})

    return anomalies
