"""Verrouillage du territoire : V-b, V-c, V-d par lecture croisée de Bronze.

Lecture seule : aucune table Silver n'est produite. Le rapport JSON est écrit
dans docs/annexes/selection_territoire/ (versionné), sans jamais en écraser un.
Usage, depuis la racine : python scripts/verifier_territoire.py
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pyogrio

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.ingestion.admin_express import _extraire_gpkg  # noqa: E402
from src.utils.manifest import construire_run_id, lire_manifeste, verifier_manifeste  # noqa: E402

SIREN = "241700434"
NB_COMMUNES = 28
SEUIL_V_C = 0.80
POP_REFERENCE_S12 = 182_435  # RP2023, comparateur INSEE (S12), cité dans selection_territoire.md
COUCHE_FILOSOFI = "carreaux_200m_met"
DOSSIERS = {
    "S01": "data/bronze/gbfs/larochelle/S01_2026-10-21",
    "S03": "data/bronze/insee_filosofi/national/S03_2026-10-21",
    "S04": "data/bronze/admin_express/national/S04_2026-10-21",
    "S05": "data/bronze/osm/larochelle/S05_2026-10-21_2",
}


def verifier_amont() -> dict:
    """Chaque source lue doit être conforme à son manifeste, avant toute lecture."""
    amont = {}
    for source_id, relatif in DOSSIERS.items():
        dossier = RACINE / relatif
        anomalies = verifier_manifeste(dossier)
        if anomalies:
            raise RuntimeError(f"{source_id} non conforme : {anomalies}")
        manifeste = lire_manifeste(dossier)
        amont[source_id] = {"dossier": relatif, "run_id": manifeste["run_id"],
                            "fichiers": {f["nom"]: f["sha256"] for f in manifeste["fichiers"]}}
    return amont


def lire_admin(chemin_7z: Path) -> tuple:
    """Communes membres (via SIREN trouvés dans codes_siren_des_epci) et contour de l'EPCI."""
    with tempfile.TemporaryDirectory() as temporaire:
        gpkg = _extraire_gpkg(chemin_7z, temporaire)
        communes = pyogrio.read_dataframe(gpkg, layer="commune", read_geometry=False,
                                          columns=["code_insee", "nom_officiel", "codes_siren_des_epci"])
        contour = pyogrio.read_dataframe(gpkg, layer="epci", where=f"code_siren = '{SIREN}'")
    # Séparateur non supposé : on extrait tous les SIREN (9 chiffres) présents dans la valeur.
    est_membre = communes["codes_siren_des_epci"].fillna("").map(lambda v: SIREN in re.findall(r"\d{9}", v))
    return communes[est_membre], contour


def v_b(chemin_zip: Path, codes: set[str], contour: gpd.GeoDataFrame) -> dict:
    """RF-01 : carreau gardé si au moins un code de lcog_geo est une commune de l'EPCI."""
    vsi = f"/vsizip/{chemin_zip.as_posix()}/{COUCHE_FILOSOFI}.gpkg"
    filtre = " OR ".join(f"lcog_geo LIKE '%{code}%'" for code in sorted(codes))
    carreaux = pyogrio.read_dataframe(vsi, layer=COUCHE_FILOSOFI, where=filtre,
                                      columns=["idcar_200m", "idcar_nat", "lcog_geo", "ind", "i_est_200"])
    if carreaux.crs.to_epsg() != contour.crs.to_epsg():
        raise ValueError(f"CRS différents : {carreaux.crs} / {contour.crs}")

    listes = carreaux["lcog_geo"].str.split(",")  # séparateur constaté le 21/10
    garde = listes.map(lambda l: any(c in codes for c in l))
    carreaux, listes = carreaux[garde], listes[garde]

    codes_absents = sorted(codes - {c for l in listes for c in l})
    hors_contour = int((~carreaux.geometry.intersects(contour.geometry.iloc[0])).sum())
    imputes = carreaux["i_est_200"] == 1
    pop = float(carreaux["ind"].sum())
    return {
        "resultat": "ok" if not codes_absents and hors_contour == 0 else ("echec" if codes_absents else "alerte"),
        "carreaux": len(carreaux),
        "idcar_200m_uniques": int(carreaux["idcar_200m"].nunique()),
        "multi_commune": int((listes.map(len) > 1).sum()),
        "partiel_epci": int(listes.map(lambda l: any(c not in codes for c in l)).sum()),
        "codes_2026_absents_de_lcog_geo_2021": codes_absents,
        "carreaux_hors_contour": hors_contour,
        "population_filosofi_2021": round(pop),
        "rapport_a_population_legale_2023": round(pop / POP_REFERENCE_S12, 3),
        "q8_part_carreaux_imputes": round(float(imputes.mean()), 3),
        "q8_part_population_imputee": round(float(carreaux.loc[imputes, "ind"].sum()) / pop, 3),
    }


def v_c(dossier_s01: Path, contour: gpd.GeoDataFrame) -> dict:
    contenu = json.loads((dossier_s01 / "station_information.json").read_text(encoding="utf-8"))
    stations = contenu["data"]["stations"]
    points = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy([s["lon"] for s in stations], [s["lat"] for s in stations]),
        crs=4326).to_crs(contour.crs)
    dedans = points.within(contour.geometry.iloc[0])
    part = float(dedans.mean())
    return {"resultat": "ok" if part >= SEUIL_V_C else "echec",
            "stations": len(stations), "dans_le_contour": int(dedans.sum()),
            "part": round(part, 3), "seuil": SEUIL_V_C}


def v_d(chemin_graphml: Path) -> dict:
    debut = time.perf_counter()
    graphe = ox.load_graphml(chemin_graphml)
    duree_chargement = time.perf_counter() - debut
    composantes = list(nx.weakly_connected_components(graphe))
    principale = max(composantes, key=len)

    debut = time.perf_counter()
    origine = min(principale)  # nœud choisi de façon déterministe
    atteints = nx.single_source_dijkstra_path_length(graphe, origine, cutoff=400, weight="length")
    duree_calcul = time.perf_counter() - debut
    return {"resultat": "ok", "noeuds": graphe.number_of_nodes(), "aretes": graphe.number_of_edges(),
            "composantes": len(composantes),
            "part_noeuds_composante_principale": round(len(principale) / graphe.number_of_nodes(), 4),
            "chargement_s": round(duree_chargement, 1),
            "essai_400m": {"origine": origine, "noeuds_atteints": len(atteints), "calcul_s": round(duree_calcul, 3)}}


def main() -> int:
    run_id = construire_run_id()
    amont = verifier_amont()
    membres, contour = lire_admin(RACINE / DOSSIERS["S04"] / next(iter(amont["S04"]["fichiers"])))
    if len(membres) != NB_COMMUNES:
        raise RuntimeError(f"{len(membres)} communes membres, {NB_COMMUNES} attendues (G2).")
    codes = set(membres["code_insee"])

    rapport = {
        "run_id": run_id,
        "date_heure": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "epci": SIREN, "communes": sorted(codes), "amont": amont,
        "V-b": v_b(RACINE / DOSSIERS["S03"] / next(iter(amont["S03"]["fichiers"])), codes, contour),
        "V-c": v_c(RACINE / DOSSIERS["S01"], contour),
        "V-d": v_d(RACINE / DOSSIERS["S05"] / "walk_graph.graphml"),
    }
    rapport["verrouille"] = all(rapport[v]["resultat"] == "ok" for v in ("V-b", "V-c", "V-d"))

    jour = datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()
    sortie = RACINE / "docs" / "annexes" / "selection_territoire" / f"verrouillage_{jour}.json"
    with sortie.open("x", encoding="utf-8", newline="\n") as fichier:
        fichier.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: rapport[k] for k in ("V-b", "V-c", "V-d", "verrouille")}, ensure_ascii=False, indent=2))
    print(f"Rapport : {sortie.relative_to(RACINE)}")
    return 0 if rapport["verrouille"] else 1


if __name__ == "__main__":
    sys.exit(main())
