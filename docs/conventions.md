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
| Exports Power BI | `data/gold/exports/` | `pbi_dim_<objet>.parquet` ou `pbi_fact_<objet>.parquet` |

- Bronze : un fichier `_manifest.json` par dossier daté (URL, date, licence, empreinte SHA-256). Le `source_id` est celui de `docs/registre_des_sources.xlsx`. Deux flux de la même famille ne partagent pas le même dossier.
- Date du dossier Bronze = date locale (Europe/Paris) du téléchargement. `run_id` et `date_heure` du manifeste = UTC. Cohérent avec le lot 0.
- `run_id` = `AAAAMMJJTHHMMSSZ_<hash court du commit>[-modifie]`. Heure UTC. Suffixe `-modifie` si le code (`src`, `scripts`, `config`, `pytest.ini`, `requirements-lock.txt`) diffère du commit, fichiers non suivis compris. `data/` et `logs/` ne comptent pas. Les manifestes manuels du lot 0 gardent leur `run_id` d'origine.

## Nommage Silver, Gold et exports

Pas de dossier de partition (AD5). Les tables multi-villes ont une colonne `territoire`, et un suffixe `_h6` ou `_5epci` dans le nom.

| Élément | Règle |
|---|---|
| Nom Silver | `<source>_<objet>_<territoire>`, ou `<objet>_<territoire>` après fusion de sources |
| Nom Gold | `<objet>_<territoire>` ; tables multi-villes : `h6_<objet>` ; références : `ref_<objet>` ; agrégats : `agg_<objet>` |
| Nom export | `pbi_dim_<objet>` ou `pbi_fact_<objet>`, en Parquet |
| `cell_id` | Identifiant du carreau tel que publié, gardé en texte. Le nom dans le fichier source se constate à V-b. |
| `offre_id` | `<mode>_<source_id>_<id_origine>` |
| `candidat_id` | `C_<cell_id>` |
| `scenario_id` | `SC_<budget>_<variante>_<hypothese>` |
| Règles | Nettoyage `RC-xx`. Qualité `Q1` à `Q8`. Chaque règle est écrite dans `methodologie.md` avant d'être codée. |

La liste des tables est dans `data_dictionary.md`.

## Géographie

- Silver et Gold avec une géométrie : EPSG:2154 (Lambert-93). Le CRS est dans les métadonnées GeoParquet.
- Exports Power BI : EPSG:4326 (latitude / longitude).
- Le système de coordonnées est vérifié à chaque jointure spatiale, jamais supposé.
- Décision AD1, 21 octobre 2026.

## Colonnes
- snake_case ; identifiants suffixés `_id` ; populations `pop_` ; coûts `cout_` + colonne `cout_etiquette`.

## Git
- Commits : `type(portée): message` — types docs, chore, feat, fix, test, data.
- Une étape (E0 à E10) = au moins un commit.
