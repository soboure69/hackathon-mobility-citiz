"""Normalisation des noms : sert uniquement à comparer, jamais à remplacer le nom d'origine."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd


def normaliser_nom(nom: object) -> str | None:
    """Minuscules, sans accents, ponctuation remplacée par des espaces, espaces réduits."""
    if nom is None or pd.isna(nom):
        return None
    texte = unicodedata.normalize("NFKD", str(nom))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^\w\s]", " ", texte.lower())
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte or None
