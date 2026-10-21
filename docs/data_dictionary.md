# Dictionnaire de données

**Statut :** niveau tables fixé le 21 octobre 2026. Le tableau colonne par colonne reste vide jusqu'à E4. Les noms de colonnes des fichiers sources se constatent à V-b et E3 : ils ne sont pas écrits ici comme certains.

`K..` renvoie au cahier des charges. GP = GeoParquet. P = Parquet.

## Silver

| Table | Granularité | Clé primaire | Colonnes essentielles | Source | Format |
|---|---|---|---|---|---|
| `cellules_larochelle` | carreau 200 m | `cell_id` | `pop`, revenus et indicateurs Filosofi (noms à constater), `commune_insee`, `epci_siren`, `node_id`, `dist_snap_m`, `secret_stat` | S03, S04, S05 | GP |
| `offre_points_larochelle` | option (arrêt, station) | `offre_id` | `mode` (bus / citiz / velo), `nom`, `source_id`, `id_origine`, `capacite`, `node_id`, `dist_snap_m`, `date_donnee` | S01, S02, S08, S05 | GP |
| `osm_walk_nodes_larochelle` | nœud | `node_id` | identifiant de nœud du graphe sauvegardé | S05 | GP |
| `osm_walk_edges_larochelle` | arête | `u`, `v`, `key` | `length_m`, `highway` si le graphe OSMnx les fournit ; sinon les noms constatés à E3 | S05 | GP |
| `cellules_h6` | carreau, 5 villes | `territoire`, `cell_id` | `territoire`, mêmes descripteurs que `cellules_larochelle`, sans graphe | S03, S04 | GP |
| `offre_points_h6` | option, 5 villes | `territoire`, `offre_id` | `territoire`, mêmes descripteurs que `offre_points_larochelle`, sans graphe | S06, S07 | GP |
| `qualite_indicateurs` | source × indicateur | `source_id`, `q_id` | `valeur`, `seuil`, `statut`, `run_id` | toutes | P |
| `rejets` | ligne rejetée | `source_id`, `id_origine`, `regle_id` | `motif`, `couche` | toutes | P |

### Tables Silver écrites (blocs S-1 et S-2)

| Dossier | Table | Clé | Source | Contenu |
|---|---|---|---|---|
| standardized | `gtfs_stops_larochelle` | `stop_id`, `id_origine` | S02 | `stops.txt` en texte + audit, aucune ligne retirée, pas de géométrie |
| cleaned | `gtfs_stops_larochelle` | `stop_id` | S02 | Après RC-02, RC-03, RG-01 à RG-04, RC-04, RC-06 ; `desservi` ; EPSG:2154 |
| deduplicated | `offre_arrets_larochelle` | `offre_id` | S02 | Une option par zone d'arrêt desservie ; `n_quais`, `n_quais_desservis` |
| deduplicated | `dedup_correspondances_S02` | `id_origine` | S02 | Un quai → une zone ; `methode`, `distance_m`, `desservi` |
| standardized | `gbfs_stations_citiz_larochelle`, `gbfs_stations_yelo_larochelle` | `station_id`, `id_origine` | S01, S08 | Champs repris seulement (RC-14), nom localisé `fr`, coordonnées en texte |
| cleaned | mêmes noms | `station_id` | S01, S08 | Après RC-02, RC-03, RG-01 à RG-04, RC-07 ; EPSG:2154 |
| deduplicated | `offre_citiz_larochelle`, `offre_velo_larochelle` | `offre_id` | S01, S08 | Une option par station ; `capacite` (NULL si absente) ; RG-07 signalé |
| standardized, cleaned | `admin_communes_5epci` | `code_insee` | S04 | Communes des 5 EPCI d'étude ; `epci_siren`, `territoire`, `population` (Admin Express) ; EPSG:2154 |
| standardized, cleaned | `admin_epci_5epci` | `code_siren` | S04 | Contours des 5 EPCI ; `n_membres_declares` (compté dans `codes_insee_des_communes_membres`) |
| standardized, cleaned | `filosofi_carreaux_5epci` | `cell_id` (= `idcar_200m`) | S03 + `admin_communes_5epci` | Carreaux retenus par RF-01 ; les 34 variables Filosofi ; `commune_insee`, `commune_principale`, `territoire`, `epci_siren`, `multi_commune`, `partiel_epci`, `est_impute`, `aire_m2` (cleaned) |
| standardized, cleaned | `osm_walk_nodes_larochelle` | `node_id` | S05 | Nœuds du graphe ; `street_count`, `composante` (0 = principale), `composante_principale` ; EPSG:2154 |
| standardized, cleaned | `osm_walk_edges_larochelle` | `u`, `v`, `key` | S05 | Arêtes, deux sens ; `highway`, `name`, `access`, `service` (listes écrites « a;b »), `length_m`, `composante` ; arêtes `busway` à statut `exclu` (cleaned) |
| quality | `rejets_<source>`, `alertes_<source>`, `qualite_indicateurs_<source>` | voir manifeste | toutes | Journaux par source ; l'union se fait en Gold |

Les tables d'offre partagent le schéma commun ci-dessous. Colonnes propres au mode : `n_quais`, `n_quais_desservis` (bus) ; `capacite` (stations). Elles seront réunies dans `offre_points_larochelle` à l'étape `spatial/`.

## Gold

| Dossier | Table | Granularité | Clé primaire | Colonnes essentielles | Source | Usage métier | Format |
|---|---|---|---|---|---|---|---|
| accessibility | `paires_cellule_offre_larochelle` | carreau × option à 5 min ou moins | `cell_id`, `offre_id` | `dist_reseau_m`, `temps_min` | cellules, offre_points, graphe | Base de K1, K5, K9. Jamais dans Power BI (AD4). | P |
| accessibility | `acces_cellule_larochelle` | carreau × mode, plus « tous » | `cell_id`, `mode` | `n_options` (K1), `desservie` | paires | Carte O1 | P |
| accessibility | `desserte_offre_larochelle` | option | `offre_id` | `pop_5min` (K5, non exclusive), `n_cellules` | paires, cellules | Carte O2 | P |
| accessibility | `kpi_couverture_larochelle` | périmètre × mode | `perimetre_type`, `perimetre_id`, `mode` | `pop_totale`, `pop_desservie` (K3), `pop_non_desservie` (K4), `taux` (K2) | acces, cellules | Page 2, synthèse | P |
| candidates | `candidats_larochelle` | candidat × type d'équipement | `candidat_id`, `type_equipement` | `node_id`, `cell_id_origine`, `cout`, `cout_etiquette` | cellules, config | Emplacements possibles. La méthode est fixée à E7. | GP |
| candidates | `paires_candidat_cellule_larochelle` | candidat × carreau à 5 min ou moins | `candidat_id`, `cell_id` | `dist_reseau_m` | candidats, graphe | Base de K6, K9. Jamais dans Power BI (AD4). | P |
| candidates | `valeur_candidat_larochelle` | candidat × type | `candidat_id`, `type_equipement` | `pop_nouvelle_seule` (K6 isolé), `taux_redondance` (K9), `score_construit` (K10), `score_h6` (K11) | paires, acces, h6 | Page 3 | P |
| analytics | `h6_jeu_apprentissage` | carreau, 5 villes | `territoire`, `cell_id` | variables H6, `cible` (présence Citiz) | cellules_h6, offre_points_h6 | Entraîner H6. Hors chemin critique. | P |
| analytics | `h6_evaluation` | ville de test × métrique | `ville_test`, `metrique` | `valeur`, `n_positifs` | jeu d'apprentissage | Model card, page 5 | P |
| analytics | `h6_scores_larochelle` | carreau | `cell_id` | `score_h6` | modèle | Alimente `valeur_candidat` | P |
| analytics | `ref_communes` | commune | `commune_insee` | `nom`, `epci_siren`, `classe_densite` (S10) | S04, S10 | Équité (K12), filtres | P |
| analytics | `ref_sources` | source | `source_id` | copie de l'onglet `sources` du registre | registre | Page 5 | P |
| optimization | `scenarios` | scénario | `scenario_id` | `budget`, `variante` (efficacité / équité), `hypothese_cout` (basse / centrale / haute), paramètres | config | Page 4 | P |
| optimization | `selection_scenario` | scénario × candidat retenu | `scenario_id`, `candidat_id` | `rang`, `cout_cumule`, `pop_nouvelle_marginale`, `pop_nouvelle_cumulee` | valeur_candidat, paires | Portefeuille retenu | P |
| optimization | `kpi_scenario` | scénario | `scenario_id` | K6 total sans double comptage, K7, K8, `cout_etiquette`, K12 | selection | Synthèse, page 4 | P |
| dashboards | `agg_distribution_acces_larochelle` | mode × classe de `n_options` | `mode`, `classe` | `pop` | acces, cellules | Histogramme, page 2. Hors chemin critique. | P |
| dashboards | `agg_equite_larochelle` | scénario × classe (densité, quintile de revenu) | `scenario_id`, `axe`, `classe` | couverture avant / après | kpi, cellules | Équité, pages 4 et 5 | P |

K6 d'un scénario se calcule sur l'ensemble des carreaux nouvellement couverts, comptés une fois. On n'additionne jamais les `pop_nouvelle_seule` des candidats.

`pop_nouvelle_marginale` dans `selection_scenario` est le gain après les candidats déjà retenus. La somme de cette colonne est donc le K6 du scénario.

`h6_jeu_apprentissage` n'a aucune variable calculée à partir des stations Citiz, ni distance ni nombre. L'évaluation se fait ville par ville : on entraîne sur toutes les villes sauf une, et on teste sur celle-ci. `score_h6` peut manquer : `valeur_candidat` reste calculable.

## Exports Power BI

Dossier `data/gold/exports/` seulement (AD3). Parquet, EPSG:4326 (AD1, AD2). Aucune table de paires (AD4).

| Export | Issu de | Relation | Page |
|---|---|---|---|
| `pbi_dim_cellule` | cellules, ref_communes, h6_scores | `cell_id` (1) | 1, 2, 3 |
| `pbi_dim_commune` | ref_communes | `commune_insee` (1) | filtres |
| `pbi_dim_offre` | offre_points | `offre_id` (1) | 2 |
| `pbi_dim_candidat` | candidats | `candidat_id` (1) | 3, 4 |
| `pbi_dim_scenario` | scenarios | `scenario_id` (1) | 4 |
| `pbi_dim_source` | ref_sources | `source_id` (1) | 5 |
| `pbi_fact_acces_cellule` | acces_cellule | `cell_id` (*) | 2 |
| `pbi_fact_desserte_offre` | desserte_offre | `offre_id` (*) | 2 |
| `pbi_fact_kpi_couverture` | kpi_couverture | `perimetre_id` (*) | 1, 2 |
| `pbi_fact_valeur_candidat` | valeur_candidat | `candidat_id` (*) | 3 |
| `pbi_fact_selection` | selection_scenario | `scenario_id`, `candidat_id` (*) | 1, 4 |
| `pbi_fact_kpi_scenario` | kpi_scenario | `scenario_id` (*) | 1, 4 |
| `pbi_fact_equite` | agg_equite | `scenario_id` (*) | 4, 5 |
| `pbi_fact_distribution_acces` | agg_distribution_acces | — | 2 |
| `pbi_fact_qualite` | qualite_indicateurs | `source_id` (*) | 5 |
| `pbi_fact_h6_evaluation` | h6_evaluation | — | 5 |

Aucune mesure DAX n'additionne `pop_5min` sur plusieurs offres : K5 n'est pas exclusif. Power BI affiche et filtre des KPI déjà calculés.

## Écarts documentation / fichier

Le fichier fait foi pour les noms de colonnes, parce que c'est lui que le code lira. La documentation fait foi pour le sens. L'équivalence ci-dessous est présumée : elle n'est pas encore vérifiée.

| Source | Nom dans la documentation (S03d) | Nom dans le fichier (S03) | Statut |
|---|---|---|---|
| Filosofi 2021 | `id_car_nat` | `idcar_nat` | écart de nom présumé, à confirmer à E4. Ce n'est pas la clé : `idcar_nat` identifie le carreau naturel. |
| Filosofi 2021 | `i_est_1Km` | `i_est_1km` | équivalence présumée, à confirmer à E4 |

Règle : les noms du fichier font foi ; la documentation fait foi pour le sens.

À confirmer à E4 : les 32 autres variables ont le même nom dans la page et dans le fichier ; aucune autre colonne du fichier ne ressemble à ces deux noms ; les valeurs ont le type et les modalités décrits par la page.

## Schéma commun des offres

Il s'applique à `offre_arrets_larochelle`, `offre_arrets_h6` et, plus tard, aux stations GBFS réunies dans `offre_points`. Les noms GTFS d'origine (`stop_id`, `parent_station`) restent dans les tables `gtfs_stops_*`.

| Colonne | Règle |
|---|---|
| `offre_id` | `<mode>_<source_id>_<id_origine>` |
| `source_id` | Identifiant du registre |
| `id_origine` | Identifiant source, en texte. Pour une zone GTFS, c'est l'identifiant de la zone |
| `mode` | `bus`, `citiz`, `velo`, ou `autre` |
| `nom` | Nom d'origine, non modifié |
| `nom_normalise` | Sert seulement à comparer des noms |
| `lat_wgs84`, `lon_wgs84` | Coordonnées d'origine, avant Lambert-93 |
| `geometry` | EPSG:2154 |
| `dans_emprise` | Marqueur. Faux ne retire pas la ligne |
| `desservi` | Faux si la ligne est exclue de l'offre (RC-04, RC-05, RC-06) |

`cell_id` est la valeur de `idcar_200m`, en texte, telle quelle. `idcar_nat` est conservé comme attribut : c'est l'identifiant du carreau naturel, niveau de diffusion des valeurs imputées, et plusieurs carreaux de 200 m le partagent. Sur `cellules_larochelle`, `secret_stat` reprend `est_impute`, vrai lorsque `i_est_200 = 1`. Une population imputée non entière ne s'affiche jamais avec ses décimales comme un nombre d'habitants. `lcog_geo` se découpe sur la virgule (constaté le 21/10/2026) ; les codes font 5 caractères.

## Colonnes d'audit

Présentes sur chaque ligne Silver.

| Colonne | Contenu |
|---|---|
| `source_id` | S01, S02… |
| `id_origine` | Identifiant dans la source, en texte |
| `fichier_origine` | Chemin du fichier Bronze, dossier daté compris |
| `sha256_origine` | Empreinte du fichier Bronze, lue dans le manifeste |
| `date_donnee` | Version du producteur |
| `run_id` | Exécution Silver |
| `statut_transformation` | `inchange`, `standardise`, `repare`, `fusionne` ou `exclu` |
| `regles_appliquees` | RC et RG déclenchées sur la ligne |
| `qualite` | `ok` ou `alerte` |
| `lat_wgs84`, `lon_wgs84` | Points seulement |

`rejets` et `alertes` ont : `source_id`, `id_origine`, `regle_id`, `niveau`, `motif`, `valeur_constatee`, `etape`, `run_id`.

`dedup_correspondances` a : `source_id`, `id_origine`, `offre_id`, `methode`, `distance_m`. Une ligne par quai ou par arrêt d'origine.

## Colonnes

À remplir à E4, après constat des fichiers sources.

| table | colonne | type | définition | source |
|---|---|---|---|---|
