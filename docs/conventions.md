# Conventions

## Général
- Noms en minuscules, snake_case, sans accents ni espaces.
- Dates au format ISO : AAAA-MM-JJ dans les noms de fichiers et les colonnes.
- Slug de territoire : larochelle, nantes, rennes, angers, poitiers.
  Les 4 derniers servent uniquement à l'apprentissage H6 (option A).

## Notebooks — `NN_couche_objet.ipynb`
- NN = ordre d'exécution sur 2 chiffres.
- 00_source_audit, 01_bronze_ingestion, 02_silver_cleaning_join_quality,
  03_gold_kpi_accessibility, 04_candidate_scoring, 05_budget_optimization,
  06_powerbi_export, 07_hackathon_demo.
- Un notebook raconte et appelle `src/`. Il ne contient pas de longue logique métier.
- Les sorties sont vidées avant commit (nbstripout).

## Code — `src/<domaine>/<verbe_objet>.py`, scripts — `scripts/<verbe>_<objet>.py`
- Exemples de forme (fichiers non créés à ce stade) : `src/ingestion/download_gtfs.py`,
  `scripts/run_pipeline.py`, `scripts/build_gold.py`.
- Tests : `tests/test_<règle>.py`.

## Données
| Couche | Chemin | Nom |
|---|---|---|
| Bronze | `data/bronze/<famille>/<territoire>/<source_id>_<AAAA-MM-JJ>/` | nom d'origine du fichier, jamais renommé ni modifié |
| Silver | `data/silver/<étape>/` | `<source>_<objet>_<territoire>.parquet` |
| Gold | `data/gold/<domaine>/` | `<objet>_<territoire>.parquet` |
| Exports Power BI | `data/gold/exports/` | `pbi_<table>.csv` ou `.parquet` |

- Bronze : un fichier `_manifest.json` par dossier daté (URL, date, licence, empreinte SHA-256). Le `source_id` est celui de `docs/registre_des_sources.xlsx`. Deux flux de la même famille ne partagent pas le même dossier.
- Les noms exacts des tables Gold sont fixés à la mission « schéma Gold ».

## Géographie
- Stockage et exports : EPSG:4326 (latitude / longitude).
- Calculs de distance et de surface : EPSG:2154 (Lambert-93).
- Le système de coordonnées est vérifié à chaque jointure spatiale, jamais supposé.

## Colonnes
- snake_case ; identifiants suffixés `_id` ; populations `pop_` ; coûts `cout_` + colonne `cout_etiquette`.

## Git
- Commits : `type(portée): message` — types docs, chore, feat, fix, test, data.
- Une étape (E0 à E10) = au moins un commit.
