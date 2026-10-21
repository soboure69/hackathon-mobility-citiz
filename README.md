# hackathon-mobility-citiz

Outil d'aide à la décision pour implanter de nouvelles stations d'autopartage Citiz,
d'arrêts de transport ou de stations vélo, là où elles couvrent le plus d'habitants
à 5 minutes à pied, au moindre coût, sans doublonner l'offre existante.

Hackathon Epitech x Citiz — sujet « Hackathon Mobility » (v0.4.0).

## Territoire

Communauté d'agglomération de La Rochelle (EPCI 241700434), 28 communes, 174 016 habitants,
choisie par une grille de portes et de notes (87,5 / 100) : voir `docs/selection_territoire.md`.
Choix verrouillé le 21/10/2026 (vérifications V-a à V-d).

## Statut

État au 21/10/2026 (`docs/plan_de_travail.md`).

| Étape | État | Preuve |
|---|---|---|
| E0 Cadrage | fait | `docs/cahier_des_charges.md` |
| E1 Territoire | fait, verrouillé | `docs/selection_territoire.md` |
| E2 Registre des sources | fait | `docs/registre_des_sources.xlsx` (26 sources) |
| E3 Bronze | fait (lot 1 : S01, S02, S03, S03d, S04, S05, S08) | `data/bronze/**/_manifest.json` |
| E4 Silver et qualité | fait | `data/silver/`, 52 indicateurs de qualité |
| E5 Accessibilité 5 min | fait | `data/gold/accessibility/` |
| E6 O1 et O2 | fait | Application, page 2 |
| E7 Candidats et score K10 | fait | `docs/score_potentiel.md`, `docs/model_card.md` |
| E8 Modèle H6 | **non livré** (conçu ; lot 2 non ingéré) | `docs/model_card.md` § 9 |
| E9 Optimisation, budgets, équité | fait (12 scénarios) | `docs/optimisation.md` |
| E10 Restitution et soutenance | fait (application Streamlit, slides, vidéo) | `docs/application.md`, `docs/soutenance/` |

Résultat de référence : 85 000 € sur 3 ans (budget de simulation), 10 stations, +18 816 habitants
nouvellement à 5 min d'une station Citiz, 4,52 € par habitant ; couverture Citiz 9,8 % → 20,6 %.

## Ce que produit le projet

1. Carte des options de mobilité accessibles à 5 min par cellule de 200 m (O1).
2. Population desservie par chaque station ou arrêt (O2).
3. Liste priorisée d'implantations sous budget (O3). La valeur qui décide est la
   population nouvellement couverte. Le score de potentiel (K10) n'est
   **pas** une prédiction de fréquentation.

## Structure

| Dossier | Rôle |
|---|---|
| `docs/` | cadrage, méthode, risques, pitch, conventions |
| `data/bronze/` | données brutes, non modifiées, traçables |
| `data/silver/` | données nettoyées, standardisées, dédoublonnées, jointes |
| `data/gold/` | tables de décision et exports de restitution |
| `notebooks/` | `07_hackathon_demo.ipynb` : résultats et contrôles, lus dans Gold |
| `src/` | fonctions réutilisables appelées par les notebooks et les scripts |
| `scripts/` | exécution rejouable du pipeline |
| `tests/` | tests des règles critiques (double comptage, budget, jointures) |
| `config/` | paramètres : seuils, coûts étiquetés |
| `app/` | application de restitution Streamlit (5 pages) |
| `powerbi/` | conception du rapport : pages, modèle, mesures, maquettes (appliquée par `app/`) |
| `reports/` | figures et tableaux de restitution |

Les conventions de nommage sont dans `docs/conventions.md`.

## Installation (Windows)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Toujours activer `.venv` avant de travailler. Dans Jupyter ou VS Code, choisir le noyau « Python (hackathon-citiz) ». Ne pas utiliser `py` sans `-3.11`.

## Application de restitution

```powershell
.\.venv\Scripts\python.exe scripts/build_exports.py --territoire larochelle
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Cinq pages : synthèse, couverture actuelle, candidats et score, optimisation budgétaire, méthode et limites. L'application lit seulement `data/gold/exports/`. Sans Internet, désactiver « Fond de carte » : carreaux, communes et stations restent affichés. Détails : `docs/application.md`.

## Données

Aucune donnée n'est versionnée : seuls les manifestes (`_manifest.json`) le sont. Toutes les
sources sont publiques et listées dans le registre des sources, avec URL, date, licence et
empreinte. Le pipeline les retélécharge dans `data/bronze/`.

## Licences des données

Chaque source garde sa licence (Licence Ouverte 2.0, ODbL…). Les jeux sous ODbL
(OpenStreetMap, certains GTFS) imposent l'attribution, et le partage à l'identique
des bases de données dérivées. Le détail est dans le registre des sources.

## Licence du code

Aucune licence pour l'instant : tous droits réservés. L'accès au dépôt est ouvert au jury pour la soutenance.

## Reproduire

Depuis la racine, `.venv` activé. Chaque script refuse de continuer si un contrôle échoue,
et chaque table produite porte un `run_id` (date UTC + commit ; `-modifie` si le code n'était
pas commité : committer avant de lancer).

| Ordre | Étape | Commande |
|---|---|---|
| 1 | Bronze (une fois par source : S01, S02, S03, S03d, S04, S08) | `python scripts/ingest_bronze.py --source S01` (options : `docs/plan_ingestion_bronze.md`) |
| 2 | Bronze, réseau piéton | `python scripts/ingest_osm.py --admin-express <dossier Bronze S04>` |
| 3 | Vérification du territoire | `python scripts/verifier_territoire.py` |
| 4 | Silver (une fois par source) | `python scripts/build_silver.py --source S02 --bronze <dossier Bronze S02>` |
| 5 | Jointures spatiales | `python scripts/build_spatial.py` |
| 6 | Accessibilité (paires carreau – option) | `python scripts/build_paires.py` |
| 7 | Qualité | `python scripts/build_qualite.py` |
| 8 | KPI d'accès | `python scripts/build_kpi_acces.py` |
| 9 | Candidats et score | `python scripts/build_candidats.py` |
| 10 | Optimisation (12 scénarios) | `python scripts/build_optimisation.py` |
| 11 | Exports de restitution | `python scripts/build_exports.py` |
| 12 | Tests | `python -m pytest -q` |

Les étapes 5 à 11 prennent `--territoire larochelle` par défaut. Pour la démonstration seule,
les étapes 11 puis l'application suffisent si `data/gold/` est présent.
