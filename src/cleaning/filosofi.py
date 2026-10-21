"""Filosofi 2021 carroyé 200 m (S03) : restriction aux EPCI d'étude (RF-01), contrôles RC-09, RC-10.

La clé est idcar_200m (cell_id). idcar_nat est le carreau naturel (diffusion des valeurs
imputées) : gardé comme attribut, jamais comme clé.
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

from src.cleaning.admin import reparer_geometries
from src.cleaning.audit import Suivi, ajouter_audit


def lire_carreaux(chemin_zip: Path | str, couche: str, codes_communes: set[str]) -> gpd.GeoDataFrame:
    """Lecture dans le zip, sans extraction. Pré-filtre large par département ; RF-01 fait le tri exact."""
    departements = sorted({code[:2] for code in codes_communes})
    filtre = " OR ".join(f"lcog_geo LIKE '%{d}%'" for d in departements)
    vsi = f"/vsizip/{Path(chemin_zip).as_posix()}/{couche}.gpkg"
    return pyogrio.read_dataframe(vsi, layer=couche, where=filtre)


def standardiser_carreaux(carreaux: gpd.GeoDataFrame, communes: pd.DataFrame, separateur: str,
                          **audit) -> gpd.GeoDataFrame:
    """RF-01 : carreau gardé si au moins un code de lcog_geo est une commune d'un EPCI d'étude.

    commune_insee = premier code membre (les codes sont triés par surface d'intersection décroissante).
    """
    membre = dict(zip(communes["code_insee"], communes["territoire"]))
    epci_de = dict(zip(communes["code_insee"], communes["epci_siren"]))
    listes = carreaux["lcog_geo"].fillna("").str.split(separateur)
    garde = listes.map(lambda l: any(c in membre for c in l))
    carreaux, listes = carreaux[garde].copy(), listes[garde]

    carreaux["cell_id"] = carreaux["idcar_200m"].astype("string")
    carreaux["commune_insee"] = listes.map(lambda l: next(c for c in l if c in membre)).astype("string")
    carreaux["commune_principale"] = listes.map(lambda l: l[0]).astype("string")
    carreaux["territoire"] = carreaux["commune_insee"].map(membre).astype("string")
    carreaux["epci_siren"] = carreaux["commune_insee"].map(epci_de).astype("string")
    carreaux["multi_commune"] = listes.map(len) > 1
    carreaux["partiel_epci"] = [any(membre.get(c) != t for c in l)
                                for l, t in zip(listes, carreaux["territoire"])]
    carreaux["est_impute"] = carreaux["i_est_200"] == 1
    carreaux = ajouter_audit(carreaux, id_origine=carreaux["idcar_200m"], **audit)
    return gpd.GeoDataFrame(carreaux, geometry="geometry", crs=carreaux.crs)


def nettoyer_carreaux(carreaux: gpd.GeoDataFrame, suivi: Suivi, tolerance_aire: float) -> gpd.GeoDataFrame:
    """RC-10 (doublon de clé → rejet des deux), RC-11 (géométrie), RC-09 (aire hors tolérance → alerte)."""
    etape = "cleaned"
    df = suivi.rejeter(carreaux, carreaux["idcar_200m"].duplicated(keep=False), "RC-10",
                       "idcar_200m en double", etape, "idcar_200m")
    df = reparer_geometries(df, suivi, etape)
    df["aire_m2"] = df.geometry.area
    ecart = (df["aire_m2"] - 40_000).abs() / 40_000
    df = suivi.signaler(df, ecart > tolerance_aire, "RC-09", f"aire à plus de {tolerance_aire:.0%} de 40 000 m²",
                        etape, "aire_m2")
    return df
