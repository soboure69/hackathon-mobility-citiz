"""Protocole de mesure : qualité des données, couverture des données, couverture de mobilité.

Trois familles, jamais mélangées :
- qualité (QC-*) : la donnée est-elle juste, complète, unique, cohérente, fraîche, traçable ?
- couverture des données (CD-*) : le territoire est-il entièrement décrit par nos sources ?
- couverture de mobilité (CM-*) : quelle part de la population a une option à ≤ 5 min ?
"""
from __future__ import annotations

import re
from datetime import date, datetime, timezone

import pandas as pd

COLONNES = ["indicateur_id", "dimension", "famille", "source_id", "perimetre", "libelle", "formule",
            "valeur", "valeur_texte", "unite", "sens", "seuil", "statut", "date_reference", "run_id"]


def statut(valeur: float | None, regle: dict) -> str:
    sens, seuil = regle["sens"], regle.get("seuil")
    if sens == "info" or valeur is None or pd.isna(valeur):
        return "info"
    if sens == ">=":
        return "ok" if valeur >= seuil else "alerte"
    if sens == "<=":
        return "ok" if valeur <= seuil else "alerte"
    if sens == "intervalle":
        return "ok" if seuil[0] <= valeur <= seuil[1] else "alerte"
    raise ValueError(f"Sens inconnu : {sens}")


class Releve:
    """Accumule les indicateurs, avec leur seuil et leur statut calculés au même endroit."""

    def __init__(self, seuils: dict, date_reference: date, run_id: str) -> None:
        self.seuils, self.date_reference, self.run_id = seuils, date_reference, run_id
        self.lignes: list[dict] = []

    def ajouter(self, indicateur_id: str, dimension: str, famille: str, source_id: str, perimetre: str,
                libelle: str, formule: str, valeur: float | None, unite: str, valeur_texte: str | None = None):
        regle = self.seuils[indicateur_id.split(":")[0]]
        self.lignes.append({
            "indicateur_id": indicateur_id, "dimension": dimension, "famille": famille,
            "source_id": source_id, "perimetre": perimetre, "libelle": libelle, "formule": formule,
            "valeur": None if valeur is None else round(float(valeur), 6), "valeur_texte": valeur_texte,
            "unite": unite, "sens": regle["sens"],
            "seuil": None if regle.get("seuil") is None else str(regle["seuil"]),
            "statut": statut(valeur, regle), "date_reference": self.date_reference.isoformat(),
            "run_id": self.run_id,
        })

    def table(self) -> pd.DataFrame:
        table = pd.DataFrame(self.lignes, columns=COLONNES)
        table["valeur"] = table["valeur"].astype("Float64")
        texte = [c for c in COLONNES if c != "valeur"]
        table[texte] = table[texte].astype("string")
        return table


def part(numerateur: float, denominateur: float) -> float | None:
    return None if not denominateur else numerateur / denominateur


def completude(table: pd.DataFrame, colonnes: list[str]) -> float | None:
    """Part des lignes dont toutes les colonnes listées sont renseignées."""
    return part(int(table[colonnes].notna().all(axis=1).sum()), len(table))


def lire_jour(valeur: object) -> date:
    """Date d'une valeur publiée : AAAAMMJJ (GTFS), ISO avec heure quelconque (GBFS v3), ou
    horodatage POSIX en secondes (GBFS v1/v2). Seul le jour est retenu."""
    texte = str(valeur).strip()
    if texte.isdigit() and len(texte) == 8:
        return datetime.strptime(texte, "%Y%m%d").date()
    if texte.isdigit():
        return datetime.fromtimestamp(int(texte), tz=timezone.utc).date()
    correspondance = re.match(r"(\d{4}-\d{2}-\d{2})", texte)
    if not correspondance:
        raise ValueError(f"Date illisible : {valeur!r}")
    return date.fromisoformat(correspondance.group(1))


def jours_depuis(valeur: object, reference: date) -> int:
    """Nombre de jours entre une date publiée et la date de référence."""
    return (reference - lire_jour(valeur)).days


def couverture_mobilite(cellules: pd.DataFrame, paires: pd.DataFrame, mode: str | None = None) -> tuple[float, float, float]:
    """(population desservie, population totale, part). Chaque carreau compte une fois.

    Desservi = au moins une paire réseau/référence (accès + réseau + accès ≤ 400 m), pour le mode
    demandé ou pour tous les modes. On travaille sur l'ENSEMBLE des carreaux atteints : jamais une
    somme de populations par option (non exclusive).
    """
    reference = paires[(paires["methode"] == "reseau") & (paires["variante"] == "reference")]
    if mode is not None:
        reference = reference[reference["mode"] == mode]
    desservis = set(reference["cell_id"])
    totale = float(cellules["pop"].sum())
    desservie = float(cellules.loc[cellules["cell_id"].isin(desservis), "pop"].sum())
    return desservie, totale, part(desservie, totale)
