"""Colonnes d'audit, journal des rejets et des alertes, contrôle de conservation (CS-01)."""
from __future__ import annotations

import pandas as pd

COLONNES_AUDIT = (
    "source_id", "id_origine", "fichier_origine", "sha256_origine", "date_donnee",
    "run_id", "statut_transformation", "regles_appliquees", "qualite",
)
COLONNES_SUIVI = ["source_id", "id_origine", "regle_id", "niveau", "motif", "valeur_constatee", "etape", "run_id"]


def ajouter_audit(df: pd.DataFrame, *, source_id: str, id_origine: pd.Series, fichier_origine: str,
                  sha256_origine: str, date_donnee: str, run_id: str) -> pd.DataFrame:
    """Ajoute les colonnes d'audit à chaque ligne, sans toucher aux colonnes de la source."""
    df = df.copy()
    df["source_id"] = source_id
    df["id_origine"] = id_origine.astype("string")
    df["fichier_origine"] = fichier_origine
    df["sha256_origine"] = sha256_origine
    df["date_donnee"] = date_donnee
    df["run_id"] = run_id
    df["statut_transformation"] = "standardise"
    df["regles_appliquees"] = ""
    df["qualite"] = "ok"
    return df


def _ajouter_regle(colonne: pd.Series, regle_id: str) -> pd.Series:
    return colonne.map(lambda v: regle_id if not v else f"{v};{regle_id}")


class Suivi:
    """Collecte, ligne par ligne, ce que chaque règle a rejeté, signalé ou exclu."""

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self._morceaux: list[pd.DataFrame] = []

    def _noter(self, df, masque, regle_id, niveau, motif, etape, colonne_valeur):
        selection = df[masque]
        if selection.empty:
            return
        valeurs = (selection[colonne_valeur].astype("string") if colonne_valeur
                   else pd.Series(pd.NA, index=selection.index, dtype="string"))
        self._morceaux.append(pd.DataFrame({
            "source_id": selection["source_id"], "id_origine": selection["id_origine"],
            "regle_id": regle_id, "niveau": niveau, "motif": motif,
            "valeur_constatee": valeurs, "etape": etape, "run_id": self.run_id,
        }))

    def rejeter(self, df, masque, regle_id, motif, etape, colonne_valeur=None) -> pd.DataFrame:
        """Retire les lignes du masque et les note comme rejets."""
        masque = masque.fillna(False).astype(bool)
        self._noter(df, masque, regle_id, "rejet", motif, etape, colonne_valeur)
        return df[~masque].copy()

    def signaler(self, df, masque, regle_id, motif, etape, colonne_valeur=None) -> pd.DataFrame:
        """Garde les lignes, marque qualite = alerte."""
        masque = masque.fillna(False).astype(bool)
        self._noter(df, masque, regle_id, "alerte", motif, etape, colonne_valeur)
        df = df.copy()
        df.loc[masque, "regles_appliquees"] = _ajouter_regle(df.loc[masque, "regles_appliquees"], regle_id)
        df.loc[masque, "qualite"] = "alerte"
        return df

    def exclure(self, df, masque, regle_id, motif, etape, colonne_valeur=None) -> pd.DataFrame:
        """Garde les lignes en Silver, mais elles ne comptent pas comme options (statut = exclu)."""
        masque = masque.fillna(False).astype(bool)
        self._noter(df, masque, regle_id, "exclusion", motif, etape, colonne_valeur)
        df = df.copy()
        df.loc[masque, "regles_appliquees"] = _ajouter_regle(df.loc[masque, "regles_appliquees"], regle_id)
        df.loc[masque, "statut_transformation"] = "exclu"
        return df

    def table(self) -> pd.DataFrame:
        if not self._morceaux:
            return pd.DataFrame({c: pd.Series(dtype="string") for c in COLONNES_SUIVI})
        return pd.concat(self._morceaux, ignore_index=True)

    def compter(self, niveau: str, etape: str | None = None) -> int:
        table = self.table()
        masque = table["niveau"] == niveau
        if etape is not None:
            masque &= table["etape"] == etape
        return int(masque.sum())


def verifier_conservation(n_entree: int, n_sortie: int, n_rejets: int, etape: str) -> None:
    """CS-01 : chaque ligne d'entrée est soit en sortie, soit dans les rejets."""
    if n_entree != n_sortie + n_rejets:
        raise RuntimeError(f"CS-01 {etape} : {n_entree} en entrée ≠ {n_sortie} en sortie + {n_rejets} rejets")
