# Protocole qualité et couverture

**Statut :** appliqué le 21/10/2026 à la CA de La Rochelle. Table produite : `data/gold/analytics/qualite_donnees_larochelle.parquet` (script `scripts/build_qualite.py`, seuils dans `config/qualite.yaml`).
**Hors périmètre :** score de potentiel, optimisation.

## 0. Trois notions à ne jamais confondre

| Famille | Question | Exemple | Préfixe |
|---|---|---|---|
| **Qualité des données** | La donnée est-elle juste, complète, unique, cohérente, fraîche, traçable ? | 136 stations vélo sans capacité | `QC-` |
| **Couverture des données** | Nos sources décrivent-elles tout le territoire ? | Filosofi décrit 95,4 % de la population légale | `CD-` |
| **Couverture de mobilité** | Quelle part des habitants a une option à ≤ 5 min de marche ? | 77,8 % de la population | `CM-` |

Une donnée de bonne qualité peut couvrir mal le territoire. Un territoire bien couvert par les données peut être mal desservi. Chaque indicateur appartient à **une seule** famille (colonne `famille`).

## 1. Dimensions de qualité

| Dimension | Définition | Indicateurs |
|---|---|---|
| Complétude | Les champs nécessaires sont renseignés | QC-COMP-01 (coordonnées), 02 (capacité), 03 (population) |
| Validité | Les lignes respectent les règles RC et RG | QC-VAL-01 par source |
| Unicité | Les clés ne sont pas dupliquées ; le dédoublonnage est mesuré | QC-UNI-01 par table ; QC-UNI-02 |
| Cohérence | Les tables sont compatibles entre elles et avec elles-mêmes | QC-COH-01 (conservation), 02 (attribut / géométrie), 03 (réseau ⊂ vol d'oiseau), 04 (sensibilité RC-01), 05 (anti-double comptage) |
| Fraîcheur | La donnée est récente par rapport à la date de référence | QC-FRA-GBFS, OSM, GTFS, ADMIN, FILOSOFI |
| Traçabilité | On peut prouver d'où vient chaque table | QC-TRA-01 (Bronze), 02 (empreintes Silver et Gold), 03 (code commité) |

## 2. Formules

| ID | Formule |
|---|---|
| QC-COMP-01 | lignes avec lat et lon / lignes (table standardisée de la source) |
| QC-COMP-02 | stations avec `capacity` / stations |
| QC-COMP-03 | carreaux avec `ind` / carreaux |
| QC-VAL-01 | 1 − rejets / lignes standardisées |
| QC-UNI-01 | 1 − lignes en double sur la clé / lignes |
| QC-UNI-02 | 1 − options bus / quais |
| QC-COH-01 | 1 si lignes standardisées = lignes nettoyées + rejets, sinon 0 |
| QC-COH-02 | carreaux dont le centroïde est dans la commune RF-01 / carreaux |
| QC-COH-03 | paires réseau aussi trouvées à vol d'oiseau / paires réseau |
| QC-COH-04 | paires de référence absentes sans arêtes trunk / paires de référence |
| QC-COH-05 | 1 si Σ pop des carreaux spatiaux = Σ `ind` Filosofi du territoire et clés uniques |
| QC-FRA-GBFS | date de référence − `last_updated` le plus ancien des fichiers lus (jours) |
| QC-FRA-OSM | date de référence − date de la requête Overpass (jours) |
| QC-FRA-GTFS | `feed_end_date` − date de référence (jours de validité restants) |
| QC-FRA-ADMIN | date de référence − date d'édition (jours) |
| QC-FRA-FILOSOFI | année de référence − millésime (années) |
| QC-TRA-01 | dossiers Bronze lus par Silver sans anomalie (`verifier_manifeste`) / dossiers |
| QC-TRA-02 | tables Silver et Gold dont le SHA-256 = manifeste / tables |
| QC-TRA-03 | tables dont le `run_id` ne finit pas par `-modifie` / tables |

Toutes les dates de fraîcheur sont lues dans les **manifestes Bronze** (`version_producteur`), jamais saisies à la main. La date de référence est un paramètre (`--date-reference`) : avec la même date, le tableau est reproductible.

## 3. Seuils

| Seuil | Origine |
|---|---|
| Complétude ≥ 95 % des champs clés ; validité ≥ 98 % | Cahier des charges (Q1, Q2), fixés **avant** constat |
| Clés uniques, conservation, traçabilité = 100 % | Règles bloquantes de l'architecture |
| Centroïde concordant ≥ 95 % | Fixé après constat (97,7 %) : alerte si la qualité géométrique se dégrade |
| Sensibilité RC-01 ≤ 1 % de paires perdues | Décision option B |
| GBFS ≤ 30 j, OSM ≤ 90 j, Admin ≤ 365 j, GTFS ≥ 14 j de validité restante | Rythmes de mise à jour habituels des sources ; paramètres |
| Population imputée ≤ 10 % ; Filosofi / population légale dans [0,85 ; 1,05] | Constats sur les 5 EPCI (de 0,875 à 0,954) |
| Composante principale ≥ 99 % | Cahier (Q7), fixé **avant** constat : en alerte (98,3 %) ; l'effet sur la population est mesuré par QC-JOI-02 (99,99 %) |

Un statut `alerte` n'arrête rien : il signale une limite à expliquer. Les règles bloquantes (CS-01, CS-03, CS-04, RC-12) arrêtent déjà les scripts **avant** l'écriture.

## 4. KPI de jointure

| ID | Formule | Seuil |
|---|---|---|
| QC-JOI-01 | options rattachées à une commune de l'EPCI / options | ≥ 99 % |
| QC-JOI-02 | Σ pop des carreaux à ≤ 400 m du réseau / Σ pop | ≥ 99 % |
| QC-JOI-03 | options à ≤ 400 m du réseau / options | ≥ 99 % |
| QC-JOI-04 | quais rattachés par `parent_station` / quais | 100 % |
| QC-JOI-05 | nœuds de la composante principale / nœuds | ≥ 99 % |

## 5. Couverture des données

```text
CD = population (ou communes) du territoire décrite par une source utilisable
     ─────────────────────────────────────────────────────────────────────────
                     population (ou communes) du territoire
```

| ID | Application |
|---|---|
| CD-01 | communes de l'EPCI avec au moins un carreau / communes |
| CD-02 | Σ `ind` Filosofi 2021 / Σ population légale (Admin Express) |
| CD-03 | Σ pop à ≤ 400 m du réseau piéton / Σ pop |
| CD-04 | modes décrits par une source (bus, Citiz, vélo) ; train et navettes non recherchés (R24) |
| CD-05 | Σ pop des carreaux imputés / Σ pop (Q8) |

## 6. Couverture de mobilité à 5 minutes

```text
            Σ pop des carreaux c tels qu'il existe une option o avec
            accès(c) + réseau(c → o) + accès(o) ≤ 400 m
CM-01 =  ──────────────────────────────────────────────────────────────
            Σ pop de tous les carreaux du territoire
```

- Paires de la méthode `reseau`, variante `reference` uniquement.
- CM-02 à CM-04 : même formule, paires d'un seul mode.
- CM-05 : Σ pop totale − Σ pop desservie.
- CM-06 : même formule à vol d'oiseau, **pour comparaison seulement** (elle surestime).

## 7. Éviter les doubles comptes de population

1. **La population n'existe qu'à un endroit :** la colonne `pop` des carreaux. Les paires, les options et les communes n'en portent pas.
2. **Un carreau, une commune :** RF-01 choisit une seule commune et le carreau n'est jamais découpé.
3. **On compte des carreaux distincts :** une couverture se calcule sur l'**ensemble** des carreaux atteints. Un carreau qui atteint trois options compte une fois.
4. **La population par option (K5) n'est pas additive :** une somme sur les options dépasse la population totale. Aucune mesure Power BI ne l'additionne (AD4).
5. **Contrôle automatique :** QC-COH-05 vérifie que Σ pop des carreaux spatiaux = Σ `ind` Filosofi du territoire, avec des clés uniques ; la couverture est toujours ≤ 1 par construction.

## 8. Tableau qualité exporté dans Gold

`data/gold/analytics/qualite_donnees_larochelle.parquet`, une ligne par indicateur, clé `indicateur_id` (`QC-VAL-01:S08`…).

| Colonne | Contenu |
|---|---|
| `indicateur_id`, `dimension`, `famille` | Identifiant, dimension, famille (`qualite`, `couverture_donnees`, `couverture_mobilite`) |
| `source_id`, `perimetre` | Source et table ou périmètre mesuré |
| `libelle`, `formule` | Texte lisible et formule exacte |
| `valeur`, `valeur_texte`, `unite` | Valeur numérique ; précision textuelle éventuelle |
| `sens`, `seuil`, `statut` | Règle, seuil, `ok` / `alerte` / `info` |
| `date_reference`, `run_id` | Date de référence de la fraîcheur ; exécution |

## 9. Visuels Power BI (page 5, « Méthodologie, qualité, limites »)

| Visuel | Contenu | Pourquoi |
|---|---|---|
| Trois cartes de synthèse | Nombre d'indicateurs `ok` / `alerte` / `info` | Lecture en 2 secondes |
| Matrice source × dimension | Statut coloré (vert, orange, gris) | Montre où se trouvent les limites |
| Tableau filtrable | `libelle`, `valeur`, `seuil`, `statut`, `formule` | Le data scientist vérifie la formule |
| Barres horizontales de fraîcheur | Âge par source, avec la ligne de seuil | Montre l'export vélo figé à 126 jours |
| Entonnoir de jointure | Lignes Bronze → nettoyées → rattachées → paires | Montre qu'aucune ligne ne se perd sans trace |
| Deux barres côte à côte | CM-01 réseau contre CM-06 vol d'oiseau | Justifie le réseau réel (77,8 % contre 95,3 %) |
| Encadré texte | Les trois familles (section 0) | Évite la confusion devant un décideur |

## 10. Trame « limites des données » pour la soutenance (environ 1 min 30)

1. **Ce qui est solide.** « Les données sont tracées de bout en bout. Chaque fichier a une empreinte vérifiée, et 100 % des tables correspondent à leur manifeste. La population n'est comptée qu'une fois. »
2. **La population.** « Filosofi 2021 décrit 95,4 % de la population légale. 6,3 % des habitants sont dans des carreaux à valeurs imputées par l'INSEE pour le secret statistique : on ne les présente jamais comme des observations individuelles. »
3. **L'offre.** « Bus, Citiz et vélo sont couverts. Le train et les navettes ne sont pas dans nos sources. L'offre vélo vient d'un export figé de juin 2026, et sa capacité n'est pas publiée. »
4. **Le réseau piéton.** « Les distances suivent le réseau OpenStreetMap réel. Les accès au réseau sont à vol d'oiseau. Les tags des voies rapides n'ont pas été récupérés, mais leur effet est mesuré : 1 paire sur 3 016. »
5. **Ce que ça change.** « À vol d'oiseau, on aurait annoncé 95 % de la population desservie. Sur le vrai réseau, c'est 78 %. La rigueur change la conclusion. »
6. **Ce que nous ne mesurons pas.** « La fréquentation : aucune donnée d'usage n'existe. Nous mesurons un **accès**, pas un usage. »
