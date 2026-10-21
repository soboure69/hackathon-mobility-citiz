# Méthodologie

**Statut :** conception Silver écrite le 21 octobre 2026. Le code n'est pas écrit. Les jointures spatiales (`silver/spatial/`) ne sont pas spécifiées ici.

Plan : accessibilité 5 min, KPI, candidats, K6, H6, optimisation.

Pas de correction automatique dans le MVP. Une donnée fausse est rejetée et comptée. La seule exception est RC-11, qui répare une géométrie sans changer l'information. Les seuils chiffrés non constatés restent dans `config/silver.yaml`, marqués « à fixer après constat ».

Constat S02, lecture seule du zip Bronze le 21/10/2026 : 1 515 arrêts, 981 quais (`location_type = 0`) tous rattachés à un `parent_station`, 534 zones (`location_type = 1`) et 534 noms distincts, 981 quais présents dans `stop_times`, aucune zone dans `stop_times`, aucun `stop_id` en double, 117 couples de coordonnées partagés et chacun est une zone avec un quai, 118 lignes toutes de `route_type` 3 (bus).

## Règles de nettoyage

Rejet : la ligne quitte la table et va dans `rejets`. Alerte : la ligne reste, et une ligne est écrite dans `alertes`. Exclusion : la ligne reste en Silver avec `statut_transformation = exclu`, et elle ne compte pas comme une option.

### RC-01 — Arêtes non piétonnes

Règle : retirer les arêtes `motorroad=yes` sans tag `foot` explicite.

Origine : test sur Lyon 2e (hors périmètre du projet).

À constater sur La Rochelle à E3 : nombre d'arêtes retirées, nombre de composantes avant / après (Q7).

| Règle | Source | Condition | Action |
|---|---|---|---|
| RC-02 | GTFS, GBFS | Identifiant manquant | Rejet |
| RC-03 | GTFS, GBFS | Identifiant en double dans la source | Rejet des deux lignes, et alerte. On ne choisit pas une ligne au hasard |
| RC-04 | GTFS | Quai (`location_type = 0`) absent de `stop_times` sur la période de validité | Exclusion : `desservi = faux`. Sur S02, les 981 quais sont desservis |
| RC-05 | GTFS | Zone (`location_type = 1`) sans aucun quai desservi | Exclusion de l'offre |
| RC-06 | GTFS | `location_type` 2, 3 ou 4 | Exclusion : ce ne sont pas des options. Aucun dans S02 |
| RC-07 | GBFS | Station sans `capacity` | Alerte, `capacite` reste NULL |
| RC-08 | Filosofi | Carreau hors de la couche métropole | Exclusion à la lecture (AD6) |
| RC-09 | Filosofi | Aire du carreau éloignée de 40 000 m² au-delà de la tolérance | Alerte. Tolérance à fixer après constat |
| RC-10 | Filosofi | `idcar_200m` en double | Rejet des deux lignes, et alerte |
| RC-11 | Admin Express | Géométrie invalide | Réparation et alerte. Géométrie vide : rejet |
| RC-12 | Admin Express | L'EPCI 241700434 n'a pas 28 communes | Échec bloquant |
| RC-13 | OSM | Arête de longueur nulle, ou nœud sans coordonnées | Rejet |
| RC-14 | S08 | Champs de disponibilité de l'export figé | Non repris. Seules les positions restent (R18) |

Les règles des sources non ingérées (S01, S04, S05, S07, S08) s'appliquent sous réserve du constat à l'ingestion.

### RF-01 — Restriction de Filosofi aux EPCI d'étude (AD6)

Attribut : `lcog_geo` = code(s) commune au 01/01/2021, triés par surface d'intersection décroissante. Séparateur constaté le 21/10/2026 : la virgule. Les codes font 5 caractères.

Règle : un carreau est gardé si au moins un de ses codes appartient à l'EPCI.

Marqueurs : `multi_commune` (plusieurs codes) ; `partiel_epci` (au moins un code hors EPCI). Le carreau n'est jamais découpé : sa population compte une fois.

Prérequis : vérifier que les codes 2021 des communes de l'EPCI sont identiques à ceux de la géographie de S04. Si une commune a changé, il faut une table de passage entre les deux millésimes du code officiel géographique (nouvelle source à enregistrer), et non une correspondance écrite à la main.

Repli : test d'intersection avec l'emprise, si `lcog_geo` est inutilisable.

## Coordonnées

Ces contrôles portent sur les points GTFS et GBFS, avant la conversion en Lambert-93. L'emprise métropolitaine, la précision minimale et le seuil de distance quai–zone sont des paramètres. RG-06 et le seuil de distance de S07 ne sont pas chiffrés.

| Règle | Contrôle | Action |
|---|---|---|
| RG-01 | Latitude ou longitude absente, ou non numérique | Rejet |
| RG-02 | (0, 0), ou hors de l'emprise métropolitaine | Rejet |
| RG-03 | Latitude et longitude probablement inversées | Rejet, sans les échanger |
| RG-04 | Moins de 4 décimales | Alerte |
| RG-05 | Hors de l'emprise de l'EPCI élargie du tampon de S05 | Marqueur `dans_emprise`, pas de rejet et pas de rattachement |
| RG-06 | Quai à plus de X mètres de sa zone | Alerte. X à fixer après constat de la distribution |
| RG-07 | Plusieurs options distinctes aux mêmes coordonnées | Alerte, toutes gardées |

Les 117 couples de S02 sont chacun une zone et son quai. Ils ne déclenchent pas RG-07 : après dédoublonnage, il ne reste qu'une option.

RG-05 ne rejette pas : un arrêt juste au-delà de la limite peut desservir l'EPCI. La décision de le garder se prend à `spatial/`.

## Noms et identifiants

Les colonnes GTFS gardent le nom de la norme (`stop_id`, `parent_station`). Les colonnes communes à toutes les offres sont `offre_id`, `source_id`, `id_origine`, `mode`, `nom`, `nom_normalise`, `lat_wgs84`, `lon_wgs84`, `geometry`.

`id_origine` reste du texte. `offre_id` vaut `<mode>_<source_id>_<id_origine>`. Pour une zone GTFS, `id_origine` est l'identifiant de la zone. `cell_id` est `idcar_200m`, en texte. `idcar_nat` est un attribut, pas la clé. Le code commune est un texte de 5 caractères. Le SIREN d'EPCI est un texte de 9 caractères.

`nom_normalise` sert seulement à comparer : minuscules, sans accents, ponctuation retirée, espaces réduits. `nom` n'est pas modifié. Les dates GTFS `AAAAMMJJ` deviennent des dates. `last_updated` devient une date et une heure avec fuseau. La lecture tolère une marque d'ordre d'octets en tête. `mode` est fermé : `bus`, `citiz`, `velo`, et `autre` si une source s'ajoute.

## Dédoublonnage

| Source | Méthode | Résultat |
|---|---|---|
| S02 | `parent_station`, applicable aux 981 quais | Une option est une zone avec au moins un quai desservi. Au plus 534 |
| S07 | `parent_station` s'il est présent, sinon distance et `nom_normalise` identiques | Seuil de distance à fixer après constat |
| GBFS | Pas de fusion. `station_id` fait foi | Coordonnées identiques : RG-07 |
| Entre modes | Jamais | Un arrêt de bus et une station Citiz au même endroit sont deux options |

Les coordonnées d'une zone sont celles de la zone. Un écart avec les quais est signalé (RG-06), pas recalculé.

`dedup_correspondances` a une ligne par élément d'origine : `source_id`, `id_origine`, `offre_id`, `methode`, `distance_m`. Chaque quai pointe vers une seule zone. Chaque identifiant d'origine apparaît au moins une fois.

### Stations GBFS (bloc S-2)

- Fichier lu : `station_information.json` quand il existe ; sinon (export figé S08) les stations embarquées dans `gbfs.json`.
- Nom : texte en `fr` si la source donne une liste localisée (GBFS v3), sinon le premier ; texte simple en v1/v2.
- RC-14 : seuls les champs descriptifs sont repris (`station_id`, `name`, `lat`, `lon`, `capacity`, `address`, `parking_type`, `is_virtual_station`, `station_opening_hours`). Les champs écartés sont listés dans le manifeste et dans `qualite_indicateurs` : rien n'est écarté sans trace.
- RC-07 : capacité absente → NULL et alerte ; elle n'est jamais déduite des disponibilités.
- RG-07 : stations distinctes aux mêmes coordonnées → alerte, toutes gardées (pas de fusion GBFS).
- Une station de test placée hors de la métropole est rejetée par RG-02 comme toute coordonnée hors emprise.

## Coordonnées selon le calcul

La lecture GTFS et GBFS reste en EPSG:4326, et ces valeurs sont gardées dans `lat_wgs84` et `lon_wgs84`. Le stockage Silver géométrique est EPSG:2154 (AD1), via pyproj. Filosofi métropole est déjà en EPSG:2154. Admin Express est reprojeté en 2154 si son CRS constaté est différent. Le graphe OSM arrive en 4326, avec des longueurs en mètres ; sa projection en 2154 se fait à `spatial/`. Les distances à vol d'oiseau, les aires et les tampons se calculent en 2154. Les exports Power BI restent en 4326, en Gold.

Chaque table géométrique Silver déclare exactement EPSG:2154. Une table sans CRS fait échouer l'exécution.

## Valeurs manquantes

| Type de champ | Règle |
|---|---|
| Identifiant, coordonnées, géométrie | Rejet (RC-02, RG-01) |
| Nom, `wheelchair_boarding`, `capacity` | NULL conservé, avec un indicateur (`capacite_manquante`) |
| `wheelchair_boarding` vide ou 0 | Inconnu, pas « non accessible » |
| Carreau Filosofi imputé | Valeurs gardées. `est_impute` vaut vrai si `i_est_200 = 1` (Q8) |
| Population égale à 0 | Valeur, pas un manque |

Remplacer un manque par 0, ou par une moyenne, est interdit en Silver.

## Contrôles d'exécution

Les tests `pytest` utilisent de petits tableaux fabriqués par le test. Les contrôles ci-dessous tournent sur les vraies données et arrêtent le pipeline.

| ID | Contrôle | Échec si |
|---|---|---|
| CS-01 | Entrée = sortie + rejets, à chaque étape | La différence n'est pas nulle |
| CS-02 | Colonnes et types du schéma | Colonne absente ou de mauvais type |
| CS-03 | Clé primaire unique | Doublon |
| CS-04 | CRS = EPSG:2154 | Autre CRS, ou CRS absent |
| CS-05 | Géométries valides et non vides | Une géométrie invalide |
| CS-06 | Empreinte Bronze = manifeste | Empreinte différente |
| CS-07 | Chaque quai a une seule zone, et chaque `id_origine` est dans `dedup_correspondances` | Quai orphelin ou en double |
| CS-08 | Stations GBFS = effectif du manifeste − rejets | Écart |
| CS-09 | EPCI 241700434 = 28 communes | Autre effectif (RC-12) |
| CS-10 | `i_est_200` dans {0, 1}, aire dans la tolérance | Hors domaine |
| CS-11 | Même Bronze, même config et même `run_id` imposé : même empreinte de sortie | Empreinte différente |
| CS-12 | Colonnes d'audit renseignées | NULL |

`run_id` est une colonne des tables Silver, donc leur empreinte change à chaque exécution réelle. CS-11 se vérifie en imposant le même `run_id` (test, ou vérification manuelle), pas en comparant deux exécutions successives.

## Indicateurs de qualité

### Q8 — Carreaux imputés (secret statistique)

Définition : part des carreaux de l'EPCI avec `i_est_200 = 1` (valeurs imputées en dessous de 11 ménages fiscaux, selon S03d).

Mesure aussi : part de la population de l'EPCI dans ces carreaux.

Usage : afficher en page 5 ; ne jamais présenter un carreau imputé comme une observation individuelle (vie privée, R10).

## Code prévu, non écrit

État au 21/10/2026 — écrits : `audit.py`, `normalisation.py`, `coordonnees.py`, `gtfs.py` (dédoublonnage inclus), `gbfs.py`, `src/evaluation/qualite.py`, `src/utils/lignage.py`, `scripts/build_silver.py`, `config/silver.yaml`. Non écrits : `regles.py`, `schemas.py`, `dedup.py`, `filosofi.py`, `admin.py`, `osm.py`, notebook.

L'implémentation attend le script d'ingestion et le lot 1. Le notebook appelle `src/` et ne contient pas les règles.

| Fichier | Rôle |
|---|---|
| `src/cleaning/regles.py` | Catalogue RC et RG |
| `src/cleaning/audit.py` | Colonnes d'audit, `rejets`, `alertes`, CS-01 |
| `src/cleaning/schemas.py` | Schémas Silver, CS-02 |
| `src/cleaning/normalisation.py` | Noms, identifiants, dates |
| `src/cleaning/coordonnees.py` | RG-01 à RG-07, conversion vers 2154 |
| `src/cleaning/gtfs.py`, `gbfs.py`, `filosofi.py`, `admin.py`, `osm.py` | Une source par module |
| `src/cleaning/dedup.py` | Dédoublonnage et `dedup_correspondances` |
| `src/evaluation/qualite.py` | Q1–Q8 et CS-xx |
| `scripts/build_silver.py` | `--source`, `--etape` ou `--all` |
| `config/silver.yaml` | Emprise, précision, tolérance d'aire, seuils encore ouverts |
| `notebooks/02_silver_cleaning_join_quality.ipynb` | Sections 0 à 9 : manifestes, sources, dédoublonnage, qualité. La section 10 est réservée aux jointures |
