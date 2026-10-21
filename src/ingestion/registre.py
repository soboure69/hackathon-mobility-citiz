"""Lecture du registre des sources, en lecture seule."""
from __future__ import annotations

from pathlib import Path

import openpyxl

COLONNES_UTILES = ("source_id", "nom", "famille", "territoire", "url_ressource", "statut_url", "licence")


def lire_source(chemin_registre: Path | str, source_id: str) -> dict[str, object]:
    """Renvoie la ligne `source_id` de l'onglet `sources`.

    Refuse une source sans URL vérifiée en https : rien ne se télécharge « à peu près ».
    """
    classeur = openpyxl.load_workbook(chemin_registre, read_only=True, data_only=True)
    try:
        lignes = classeur["sources"].iter_rows(values_only=True)
        entetes = list(next(lignes))
        manquantes = [c for c in COLONNES_UTILES if c not in entetes]
        if manquantes:
            raise ValueError(f"Colonnes absentes du registre : {manquantes}")
        position = entetes.index("source_id")
        trouvees = [dict(zip(entetes, ligne)) for ligne in lignes if ligne and ligne[position] == source_id]
    finally:
        classeur.close()

    if len(trouvees) != 1:
        raise ValueError(f"{source_id} : {len(trouvees)} ligne(s) dans le registre, 1 attendue.")
    source = {c: trouvees[0][c] for c in COLONNES_UTILES}

    url = str(source["url_ressource"] or "")
    if source["statut_url"] != "verifiee" or not url.startswith("https://"):
        raise ValueError(f"{source_id} : URL non vérifiée ou absente ({url!r}). Rien n'est téléchargé.")
    return source
