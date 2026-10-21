"""Sites candidats et score multicritère de potentiel territorial (K10).

Un site candidat = un nœud routable du réseau piéton auquel au moins un carreau peuplé est
rattaché. Une station se pose sur le réseau, pas au milieu d'un carreau.
Le score combine des variables observées (Filosofi, offre, réseau). Il n'est appris sur aucune
cible : c'est une note de priorité, pas une prédiction de fréquentation.
"""
from __future__ import annotations

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd

VARIABLES = ("impact", "besoin", "complementarite_bus", "logement_collectif", "petits_menages")


def generer_sites(cellules: gpd.GeoDataFrame, noeuds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Un site par nœud distinct ; carreau d'origine = le plus peuplé rattaché à ce nœud."""
    origine = (cellules.sort_values(["node_id", "pop", "cell_id"], ascending=[True, False, True])
               .drop_duplicates("node_id")[["node_id", "cell_id", "commune_insee"]]
               .rename(columns={"cell_id": "cell_id_origine"}))
    sites = noeuds[["node_id", "geometry"]].merge(origine, on="node_id")
    sites["candidat_id"] = "C_" + sites["cell_id_origine"].astype(str)
    return gpd.GeoDataFrame(sites, geometry="geometry", crs=noeuds.crs)


def paires_sites(sites: pd.DataFrame, cellules: pd.DataFrame, graphe: nx.Graph, budget: float) -> pd.DataFrame:
    """Carreaux à ≤ budget de chaque site : accès du carreau + réseau (le site est sur un nœud)."""
    par_noeud: dict = {}
    for cell_id, noeud, acces in zip(cellules["cell_id"], cellules["node_id"], cellules["dist_snap_m"]):
        par_noeud.setdefault(noeud, []).append((cell_id, float(acces)))
    lignes = []
    for candidat_id, noeud in zip(sites["candidat_id"], sites["node_id"]):
        if noeud not in graphe:
            continue
        for atteint, reseau in nx.single_source_dijkstra_path_length(graphe, noeud, cutoff=budget, weight="length").items():
            for cell_id, acces in par_noeud.get(atteint, ()):
                if acces + reseau <= budget:
                    lignes.append((candidat_id, cell_id, acces, reseau, acces + reseau))
    paires = pd.DataFrame(lignes, columns=["candidat_id", "cell_id", "dist_acces_cellule_m", "dist_reseau_m", "dist_totale_m"])
    for colonne in ("dist_acces_cellule_m", "dist_reseau_m", "dist_totale_m"):
        paires[colonne] = paires[colonne].astype("Float64")
    return paires


def acces_voiture(sites: pd.DataFrame, aretes: pd.DataFrame, voies: list[str]) -> pd.Series:
    """Vrai si le nœud touche au moins une voie carrossable (hors trunk et hors arêtes exclues)."""
    utilisables = aretes[aretes["statut_transformation"] != "exclu"]
    carrossable = utilisables["highway"].fillna("").str.split(";").map(lambda l: any(v in voies for v in l))
    noeuds = set(utilisables.loc[carrossable, "u"]) | set(utilisables.loc[carrossable, "v"])
    return sites["node_id"].isin(noeuds)


def variables(sites: pd.DataFrame, paires: pd.DataFrame, acces: pd.DataFrame, mode: str) -> pd.DataFrame:
    """Variables brutes d'un type d'équipement, calculées sur la zone atteinte à 5 min du site."""
    colonnes = list(dict.fromkeys(["cell_id", "pop", "men", "men_coll", "men_1ind", "ind", "ind_snv",
                                   "desservi", "desservi_bus", f"desservi_{mode}"]))  # sans doublon si mode = bus
    zone = paires.merge(acces[colonnes], on="cell_id")
    zone["pop_nouvelle"] = zone["pop"].where(~zone[f"desservi_{mode}"].astype(bool), 0.0)
    zone["pop_sans_option"] = zone["pop"].where(~zone["desservi"].astype(bool), 0.0)
    zone["pop_bus"] = zone["pop"].where(zone["desservi_bus"].astype(bool), 0.0)
    somme = zone.groupby("candidat_id")[["pop", "pop_nouvelle", "pop_sans_option", "pop_bus",
                                         "men", "men_coll", "men_1ind", "ind", "ind_snv"]].sum()
    somme["n_carreaux"] = zone.groupby("candidat_id")["cell_id"].nunique()
    v = pd.DataFrame(index=somme.index)
    v["pop_rayon"] = somme["pop"]
    v["pop_nouvelle"] = somme["pop_nouvelle"]                                     # K6 du site seul
    v["taux_redondance"] = 1 - somme["pop_nouvelle"] / somme["pop"]               # K9
    v["impact"] = somme["pop_nouvelle"]
    v["besoin"] = somme["pop_sans_option"] / somme["pop"]
    v["complementarite_bus"] = somme["pop_bus"] / somme["pop"]
    v["logement_collectif"] = somme["men_coll"] / somme["men"].where(somme["men"] > 0)
    v["petits_menages"] = somme["men_1ind"] / somme["men"].where(somme["men"] > 0)
    v["niveau_vie_moyen_zone"] = somme["ind_snv"] / somme["ind"].where(somme["ind"] > 0)
    v["n_carreaux_zone"] = somme["n_carreaux"]
    return sites.merge(v, left_on="candidat_id", right_index=True, how="left")


def normaliser(colonne: pd.Series) -> pd.Series:
    """Rang centile dans [0, 1] : « meilleur que x % des candidats ». Robuste aux valeurs extrêmes."""
    return colonne.rank(pct=True, method="average").fillna(0.0)


def noter(candidats: pd.DataFrame, poids: dict[str, float]) -> pd.DataFrame:
    """Score sur 100 = Σ poids × variable normalisée ; contributions gardées pour l'explication."""
    if abs(sum(poids.values()) - 1) > 1e-9:
        raise ValueError("Les pondérations doivent sommer à 1.")
    candidats = candidats.copy()
    candidats["score"] = 0.0
    for nom in VARIABLES:
        candidats[f"n_{nom}"] = normaliser(candidats[nom])
        candidats[f"contribution_{nom}"] = 100 * poids[nom] * candidats[f"n_{nom}"]
        candidats["score"] += candidats[f"contribution_{nom}"]
    return candidats


def classer(candidats: pd.DataFrame) -> pd.Series:
    """Rang 1 = meilleur score ; égalités départagées par l'impact puis l'identifiant."""
    ordre = candidats.sort_values(["score", "impact", "candidat_id"], ascending=[False, False, True]).index
    return pd.Series(np.arange(1, len(ordre) + 1), index=ordre).reindex(candidats.index)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Corrélation de rang : corrélation linéaire des rangs (égalités au rang moyen)."""
    rang_a = pd.Series(a).rank(method="average").to_numpy()
    rang_b = pd.Series(b).rank(method="average").to_numpy()
    return float(np.corrcoef(rang_a, rang_b)[0, 1])


def sensibilite(candidats: pd.DataFrame, poids: dict, tirages: int, concentration: float,
                graine: int, top_n: int) -> tuple[pd.Series, pd.DataFrame]:
    """(fréquence dans le top N sous pondérations tirées, tableau un-facteur-à-la-fois)."""
    normales = pd.DataFrame({nom: normaliser(candidats[nom]) for nom in VARIABLES})
    initial = np.array([poids[n] for n in VARIABLES])
    reference = normales.to_numpy() @ initial
    top_reference = set(np.argsort(-reference, kind="stable")[:top_n])
    rng = np.random.default_rng(graine)
    compte = np.zeros(len(candidats))
    for w in rng.dirichlet(initial * concentration, size=tirages):
        compte[np.argsort(-(normales.to_numpy() @ w), kind="stable")[:top_n]] += 1
    frequence = pd.Series(compte / tirages, index=candidats.index)

    lignes = []
    for nom in VARIABLES:
        for facteur in (0.5, 1.5):
            w = initial.copy()
            w[VARIABLES.index(nom)] *= facteur
            w /= w.sum()
            score = normales.to_numpy() @ w
            top = set(np.argsort(-score, kind="stable")[:top_n])
            lignes.append({"variable": nom, "facteur": facteur,
                           "spearman": spearman(score, reference),
                           "recouvrement_top_n": len(top & top_reference) / top_n})
    return frequence, pd.DataFrame(lignes)


def selection_equite(candidats: pd.DataFrame, prioritaires: set[str], top_n: int, quota: float) -> pd.Series:
    """Top N garantissant au moins `quota` des places aux communes prioritaires (s'il y en a assez)."""
    retenus = candidats.sort_values("rang")
    minimum = int(np.ceil(top_n * quota))
    prio = retenus[retenus["commune_insee"].isin(prioritaires)].head(minimum)
    reste = retenus.drop(prio.index).head(top_n - len(prio))
    choisis = pd.concat([prio, reste]).sort_values("rang")
    return pd.Series(np.arange(1, len(choisis) + 1), index=choisis.index).reindex(candidats.index).astype("Int64")
