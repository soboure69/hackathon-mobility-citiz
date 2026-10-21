"""Écriture des tables Silver et de leur manifeste d'exécution.

Silver est reproductible : tables et manifestes sont RÉÉCRITS à chaque exécution.
L'historique des manifestes est conservé par Git.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.utils.manifest import NOM_MANIFESTE, calculer_sha256


def ecrire_table(table: pd.DataFrame, chemin: Path | str, cle: list[str]) -> dict[str, object]:
    """Écrit en Parquet (GeoParquet si géométrie), trié par la clé pour un fichier reproductible.

    Vérifie l'unicité de la clé (CS-03) et, pour une table géométrique, le CRS 2154 (CS-04).
    """
    chemin = Path(chemin)
    if table.duplicated(subset=cle).any():
        raise RuntimeError(f"CS-03 {chemin.name} : clé {cle} non unique.")
    geometrique = isinstance(table, gpd.GeoDataFrame)
    if geometrique and (table.crs is None or table.crs.to_epsg() != 2154):
        raise RuntimeError(f"CS-04 {chemin.name} : CRS {table.crs}, EPSG:2154 attendu.")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    table = table.sort_values(cle).reset_index(drop=True)
    table.to_parquet(chemin, index=False)
    return {"nom": chemin.name, "lignes": len(table), "cle": cle,
            "colonnes": [str(c) for c in table.columns],
            "crs": "EPSG:2154" if geometrique else None, "sha256": calculer_sha256(chemin)}


def mettre_a_jour_manifeste(dossier: Path | str, table: str, entree: dict[str, object],
                            couche: str = "silver") -> None:
    """Met à jour l'entrée `table` du _manifest.json du dossier (les autres tables sont gardées)."""
    chemin = Path(dossier) / NOM_MANIFESTE
    contenu = (json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists()
               else {"couche": couche, "tables": {}})
    contenu["tables"][table] = entree
    with chemin.open("w", encoding="utf-8", newline="\n") as fichier:
        fichier.write(json.dumps(contenu, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
