# hackathon-mobility-citiz

Outil d'aide à la décision pour implanter de nouvelles stations d'autopartage Citiz,
d'arrêts de transport ou de stations vélo, là où elles couvrent le plus d'habitants
à 5 minutes à pied, au moindre coût, sans doublonner l'offre existante.

Hackathon Epitech x Citiz — sujet « Hackathon Mobility » (v0.4.0).

## Territoire

Communauté d'agglomération de La Rochelle (EPCI 241700434), choisie par une grille
de portes et de notes : voir `docs/selection_territoire.md`.
Le choix est décidé, pas encore verrouillé (vérifications V-a à V-d, §9).

## Statut

| Étape | État |
|---|---|
| E0 Cadrage | fait |
| E1 Territoire | décidé |
| E2 Registre des sources | à faire |
| E3 et suivantes | à faire |

## Ce que produit le projet

1. Carte des options de mobilité accessibles à 5 min par cellule de 200 m (O1).
2. Population desservie par chaque station ou arrêt (O2).
3. Liste priorisée d'implantations sous budget (O3). La valeur qui décide est la
   population nouvellement couverte. Le score de potentiel territorial (H6) n'est
   **pas** une prédiction de fréquentation.

## Structure

| Dossier | Rôle |
|---|---|
| `docs/` | cadrage, méthode, risques, pitch, conventions |
| `data/bronze/` | données brutes, non modifiées, traçables |
| `data/silver/` | données nettoyées, standardisées, dédoublonnées, jointes |
| `data/gold/` | tables de décision et exports Power BI |
| `notebooks/` | récit numéroté de l'analyse |
| `src/` | fonctions réutilisables appelées par les notebooks et les scripts |
| `scripts/` | exécution rejouable du pipeline |
| `tests/` | tests des règles critiques (double comptage, budget, jointures) |
| `config/` | paramètres : seuils, coûts étiquetés |
| `powerbi/` | schéma, mesures DAX, maquettes |
| `reports/` | figures et tableaux de restitution |

Les conventions de nommage sont dans `docs/conventions.md`.

## Installation (Windows)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Données

Aucune donnée n'est versionnée. Toutes les sources sont publiques et listées dans le
registre des sources (étape E2), avec URL, date, licence et empreinte. Le pipeline les
retélécharge dans `data/bronze/`.

## Licences des données

Chaque source garde sa licence (Licence Ouverte 2.0, ODbL…). Les jeux sous ODbL
(OpenStreetMap, certains GTFS) imposent l'attribution, et le partage à l'identique
des bases de données dérivées. Le détail est dans le registre des sources.

## Reproduire

À compléter quand le pipeline existera (E3 et suivantes).
