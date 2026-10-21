"""Ingestion Bronze du réseau piéton (S05), sur le contour de l'EPCI (S04) élargi d'un tampon.

Usage (depuis la racine) :
    python scripts/ingest_osm.py --admin-express data/bronze/admin_express/national/S04_2026-10-21 \
        --licence-constatee "ODbL ... (lue le AAAA-MM-JJ)"
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import osmnx as ox

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from src.ingestion.admin_express import lire_contour_epci  # noqa: E402
from src.ingestion.http_download import creer_dossier_date  # noqa: E402
from src.ingestion.osm import (  # noqa: E402
    PARAMETRES_GRAPHE, construire_emprise, ecrire_emprise, telecharger_graphe_pieton,
)
from src.ingestion.registre import lire_source  # noqa: E402
from src.utils.journal import Journal  # noqa: E402
from src.utils.manifest import (  # noqa: E402
    NOM_MANIFESTE, construire_run_id, decrire_fichier, ecrire_manifeste, lire_manifeste, verifier_manifeste,
)

REGISTRE = RACINE / "docs" / "registre_des_sources.xlsx"
BRONZE = RACINE / "data" / "bronze"
LOGS = RACINE / "logs"
PARIS = ZoneInfo("Europe/Paris")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingestion Bronze du graphe piéton OSM.")
    parser.add_argument("--source", default="S05")
    parser.add_argument("--admin-express", required=True, help="Dossier Bronze S04, relatif à la racine.")
    parser.add_argument("--siren", default="241700434")
    parser.add_argument("--tampon-m", type=float, default=500.0)
    parser.add_argument("--licence-constatee", default=None)
    parser.add_argument("--suffixe", type=int, default=None)
    args = parser.parse_args(argv)

    run_id = construire_run_id()
    journal = Journal(LOGS, run_id)
    source = lire_source(REGISTRE, args.source)
    if source["famille"] != "osm":
        journal.evenement(args.source, "registre", "echec", f"Famille {source['famille']!r} : pas une source OSM.")
        return 2

    # Chaîne de confiance : S04 doit être intact AVANT d'en tirer l'emprise.
    dossier_s04 = RACINE / args.admin_express
    anomalies_s04 = verifier_manifeste(dossier_s04)
    if anomalies_s04:
        journal.evenement(args.source, "amont", "echec", f"S04 non conforme : {anomalies_s04}")
        return 1
    manifeste_s04 = lire_manifeste(dossier_s04)
    archive_s04 = dossier_s04 / manifeste_s04["fichiers"][0]["nom"]
    journal.evenement(args.source, "amont", "ok", f"S04 conforme ({manifeste_s04['run_id']})")

    maintenant = datetime.now(timezone.utc)
    dossier = creer_dossier_date(BRONZE, "osm", source["territoire"], args.source,
                                 maintenant.astimezone(PARIS).date(), args.suffixe)
    journal.evenement(args.source, "dossier", "ok", str(dossier.relative_to(RACINE)))

    controles: list[dict] = []
    url_overpass = ox.settings.overpass_url
    controles.append({"id": "url_overpass", "resultat": "ok" if url_overpass == source["url_ressource"] else "alerte",
                      "valeur": f"utilisée {url_overpass} / registre {source['url_ressource']}"})
    try:
        contour = lire_contour_epci(archive_s04, args.siren)
        emprise = construire_emprise(contour, args.tampon_m)
        ecrire_emprise(emprise, dossier / "emprise_requete.geojson")
        journal.evenement(args.source, "emprise", "ok", f"tampon {args.tampon_m} m ; requête Overpass en cours…")
        stats = telecharger_graphe_pieton(emprise, dossier / "walk_graph.graphml")
        controles += [
            {"id": "nb_noeuds", "resultat": "ok" if stats["nb_noeuds"] > 0 else "echec", "valeur": stats["nb_noeuds"]},
            {"id": "nb_aretes", "resultat": "ok" if stats["nb_aretes"] > 0 else "echec", "valeur": stats["nb_aretes"]},
            {"id": "nb_composantes", "resultat": "ok", "valeur": stats["nb_composantes"]},  # constaté, traité en Silver
        ]
    except Exception as erreur:
        controles.append({"id": "telechargement", "resultat": "echec", "valeur": f"{type(erreur).__name__}: {erreur}"})
        journal.evenement(args.source, "download", "echec", f"{type(erreur).__name__}: {erreur}")

    controles.append({"id": "licence_constatee", "resultat": "ok" if args.licence_constatee else "alerte",
                      "valeur": args.licence_constatee or "non constatée"})
    fichiers = [decrire_fichier(f) for f in sorted(dossier.iterdir()) if f.is_file() and f.name != NOM_MANIFESTE]
    statut = ("echouee" if any(c["resultat"] == "echec" for c in controles)
              else "reussie_avec_alertes" if any(c["resultat"] == "alerte" for c in controles) else "reussie")

    ecrire_manifeste(dossier, {
        "source_id": args.source,
        "nom": source["nom"],
        "run_id": run_id,
        "date_heure": maintenant.isoformat(timespec="seconds"),
        "url_demandee": source["url_ressource"],
        "url_effective": url_overpass,
        "http_status": None,  # OSMnx ne l'expose pas
        "fichiers": fichiers,
        "version_producteur": {
            "date_requete": maintenant.isoformat(timespec="seconds"),
            "note": "OSM évolue en continu : la version de référence est ce graphe sauvegardé.",
        },
        "licence_registre": source["licence"],
        "licence_constatee": args.licence_constatee,
        "outil": {"mode": "script", "script": "scripts/ingest_osm.py", "osmnx": ox.__version__},
        "parametres": {
            **PARAMETRES_GRAPHE,
            "use_cache": False,
            "tampon_m": args.tampon_m,
            "siren": args.siren,
            "crs_emprise": "EPSG:4326",
            "source_contour": {
                "source_id": manifeste_s04["source_id"],
                "dossier": args.admin_express,
                "sha256": manifeste_s04["fichiers"][0]["sha256"],
                "run_id": manifeste_s04["run_id"],
                "couche": "epci",
                "colonne": "code_siren",
            },
        },
        "controles": controles,
        "statut_ingestion": statut,
    })

    for controle in controles:
        journal.evenement(args.source, "controle", controle["resultat"], f"{controle['id']} = {controle['valeur']}")
    anomalies = verifier_manifeste(dossier)
    journal.evenement(args.source, "manifest", "ok" if not anomalies else "echec",
                      f"statut_ingestion = {statut} ; anomalies = {anomalies}")
    return 0 if statut != "echouee" and not anomalies else 1


if __name__ == "__main__":
    sys.exit(main())
