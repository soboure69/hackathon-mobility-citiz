"""Ingestion Bronze d'une source GBFS du registre.

Usage (depuis la racine du dépôt) :
    python scripts/ingest_bronze.py --source S01 --licence-constatee "Licence Ouverte 2.0 (fiche lue le AAAA-MM-JJ)"
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))  # pour importer src/ en lançant le script depuis la racine

from src.ingestion.gbfs import FLUX_RETENUS, ingerer_gbfs  # noqa: E402
from src.ingestion.http_download import DELAI_PAR_DEFAUT, creer_dossier_date  # noqa: E402
from src.ingestion.registre import lire_source  # noqa: E402
from src.utils.journal import Journal  # noqa: E402
from src.utils.manifest import (  # noqa: E402
    construire_run_id, decrire_fichier, ecrire_manifeste, verifier_manifeste, NOM_MANIFESTE,
)

REGISTRE = RACINE / "docs" / "registre_des_sources.xlsx"
BRONZE = RACINE / "data" / "bronze"
LOGS = RACINE / "logs"
PARIS = ZoneInfo("Europe/Paris")
ESSAIS = 3


def statut_global(controles: list[dict]) -> str:
    resultats = {c["resultat"] for c in controles}
    if "echec" in resultats:
        return "echouee"
    if "alerte" in resultats:
        return "reussie_avec_alertes"
    return "reussie"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingestion Bronze d'une source GBFS.")
    parser.add_argument("--source", required=True, help="source_id du registre, ex. S01")
    parser.add_argument("--licence-constatee", default=None, help="Licence lue sur la fiche le jour même.")
    parser.add_argument("--suffixe", type=int, default=None, help="2, 3… pour un second téléchargement le même jour.")
    args = parser.parse_args(argv)

    run_id = construire_run_id()
    journal = Journal(LOGS, run_id)
    source = lire_source(REGISTRE, args.source)
    if source["famille"] != "gbfs":
        journal.evenement(args.source, "registre", "echec", f"Famille {source['famille']!r} non prise en charge ici.")
        return 2

    maintenant = datetime.now(timezone.utc)
    dossier = creer_dossier_date(BRONZE, source["famille"], source["territoire"], args.source,
                                 maintenant.astimezone(PARIS).date(), args.suffixe)
    journal.evenement(args.source, "dossier", "ok", str(dossier.relative_to(RACINE)))

    fichiers, version, controles = [], None, []
    try:
        with requests.Session() as session:
            fichiers, version, controles = ingerer_gbfs(source["url_ressource"], dossier,
                                                        session=session, essais=ESSAIS)
    except Exception as erreur:
        controles.append({"id": "telechargement", "resultat": "echec",
                          "valeur": f"{type(erreur).__name__}: {erreur}"})
        fichiers = [decrire_fichier(f) for f in sorted(dossier.iterdir())
                    if f.is_file() and f.name != NOM_MANIFESTE]
        journal.evenement(args.source, "download", "echec", f"{type(erreur).__name__}: {erreur}")

    controles.append({
        "id": "licence_constatee",
        "resultat": "ok" if args.licence_constatee else "alerte",
        "valeur": args.licence_constatee or "non constatée : lire la fiche et relancer avec --licence-constatee",
    })

    index = fichiers[0] if fichiers else {}
    statut = statut_global(controles)
    ecrire_manifeste(dossier, {
        "source_id": args.source,
        "nom": source["nom"],
        "run_id": run_id,
        "date_heure": maintenant.isoformat(timespec="seconds"),
        "url_demandee": source["url_ressource"],
        "url_effective": index.get("url_effective"),
        "http_status": index.get("http_status"),
        "fichiers": fichiers,
        "version_producteur": version,
        "licence_registre": source["licence"],
        "licence_constatee": args.licence_constatee,
        "outil": {"mode": "script", "script": "scripts/ingest_bronze.py", "requests": requests.__version__},
        "parametres": {"flux_retenus": list(FLUX_RETENUS), "delai_s": list(DELAI_PAR_DEFAUT), "essais": ESSAIS},
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
