# Architecture des données

**Statut :** architecture cible validée le 21 octobre 2026. Conception du nettoyage Silver ajoutée le même jour, sans code. L'étape `spatial/` n'est pas spécifiée ici.

Décisions AD1 à AD6 retenues. Les tables sont dans `data_dictionary.md`. Les noms et les clés sont dans `conventions.md`.

## Décisions

| ID | Décision | Statut |
|---|---|---|
| AD1 | Silver et Gold géométriques en EPSG:2154 (Lambert-93). Exports Power BI en EPSG:4326. Le CRS est écrit dans les métadonnées GeoParquet. | Retenue |
| AD2 | Power BI lit du Parquet, pas du CSV. | Retenue |
| AD3 | `gold/exports/` est le seul dossier lu par Power BI. `gold/dashboards/` contient les agrégats calculés en Python. | Retenue |
| AD4 | Les tables de paires (cellule × offre, candidat × cellule) ne vont jamais dans Power BI. | Retenue |
| AD5 | Pas de partitionnement en dossiers. Une colonne `territoire` dans les tables multi-villes. | Retenue |
| AD6 | Filosofi est restreint aux 5 EPCI dès `silver/standardized` : larochelle, angers, poitiers, nantes, rennes. Constat S03d du 21/10/2026 : `lcog_geo` porte le code officiel géographique au 01/01/2021 de la ou des communes du carreau, triées par surface d'intersection décroissante. Le séparateur n'est pas indiqué sur la page : il se constate dans le fichier à E4. Le filtre est un filtre d'attribut. Le test d'intersection avec l'emprise ne sert que si `lcog_geo` est inutilisable. Aucune commune n'est rattachée ici. | Retenue |

## 1. Définition des couches

| Couche | Rôle | Autorisé | Interdit | Format | Versionné |
|---|---|---|---|---|---|
| Bronze | Copie fidèle de la source, à une date | Télécharger, ranger, calculer l'empreinte, écrire le manifeste | Modifier, renommer, filtrer, convertir | Format d'origine | Manifeste seulement |
| Silver | Données fiables, sans interprétation métier | Typage, renommage, CRS, règles de nettoyage, dédoublonnage, jointures spatiales et administratives, mesure de la qualité | KPI, scores, pondérations, agrégation métier, imputation sans indicateur, suppression silencieuse | GeoParquet / Parquet | Manifeste seulement |
| Gold | Tables de décision | Accessibilité, KPI, candidats, H6, optimisation, agrégats, exports | Relire Bronze directement ; corriger une donnée (ça se fait en Silver) | GeoParquet / Parquet ; exports Parquet, plus un GeoJSON de carte si le test E10 le retient | Manifeste seulement |

Règle de sens unique : Bronze, puis Silver, puis Gold. Une table ne lit que la couche du dessus, ou sa propre couche.

## 2. Jeux attendus dans Bronze

Chemin : `data/bronze/<famille>/<territoire>/<source_id>_<AAAA-MM-JJ>/`. Les fichiers sont attendus : leur présence se constate au téléchargement.

| Source | Dossier | Fichiers attendus |
|---|---|---|
| S01 Citiz La Rochelle | `gbfs/larochelle/S01_…` | `gbfs.json`, `system_information.json`, `station_information.json`. `station_status.json` est facultatif : instantané, jamais utilisé pour l'offre |
| S02 GTFS Yélo | `gtfs/larochelle/S02_…` | `gtfs.zip` (référence). Les fichiers publiés séparément ne servent que si le zip est incomplet (V-a) |
| S03 Filosofi 200 m | `insee_filosofi/national/S03_…` | Fichier national et documentation du millésime |
| S04 Admin Express | `admin_express/national/S04_…` | Archive de l'édition (couches communes et EPCI) |
| S05 OSM piéton | `osm/larochelle/S05_…` | Graphe OSMnx `walk` sauvegardé tel que reçu. Paramètres de la requête et emprise dans le manifeste |
| S06a–d Citiz H6 | `gbfs/<ville>/S06x_…` | Comme S01 |
| S07 Arrêts France | `gtfs/national/S07_…` | Fichier national |
| S08 Yélo vélo | `gbfs/larochelle/S08_…` | `gbfs.json` (export figé) |
| S09, S10, S11 | `insee_omphale/…`, `external/national/…` | Fichiers publiés |
| S12 Populations légales | — | Pas de fichier : valeur de référence, déjà citée |
| S13–S17 | selon la famille | Seulement si l'extension est ouverte |

## 3. Transformations dans Silver

Dans l'ordre d'exécution.

| Ordre | Dossier | Transformations | Tables produites |
|---|---|---|---|
| 1 | `standardized/` | Noms de colonnes en snake_case, types, CRS 2154, `source_id` et identifiant d'origine conservés. Restriction de Filosofi aux 5 EPCI par `lcog_geo` (AD6). | `gtfs_stops_larochelle`, `gtfs_stops_national`, `gbfs_stations_citiz_<ville>` (cinq villes), `gbfs_stations_yelo_larochelle`, `filosofi_carreaux_5epci`, `admin_communes`, `admin_epci`, `osm_walk_nodes_larochelle`, `osm_walk_edges_larochelle`, `ref_densite_communes` |
| 2 | `cleaned/` | Règles `RC-xx` et `RG-xx` de `methodologie.md`. Une ligne retirée va dans `rejets`. Une ligne gardée mais signalée va dans `alertes`. Hors emprise : marqueur `dans_emprise`, pas un rejet. | Mêmes noms, version nettoyée |
| 3 | `deduplicated/` | S02 : une option par `parent_station` (981 quais sur 981). S07 : `parent_station`, sinon distance et nom normalisé, seuil à fixer après constat. Pas de fusion entre modes. | `offre_arrets_larochelle`, `offre_arrets_h6`, `dedup_correspondances` |
| 4 | `spatial/` | Rattachement carreau, commune, EPCI. Point vers le nœud du graphe le plus proche, avec la distance de rattachement. Table unifiée des options (H4). | `cellules_larochelle`, `offre_points_larochelle`, `cellules_h6`, `offre_points_h6` |
| 5 | `quality/` | Indicateurs Q1 à Q8, journal des rejets et des alertes. | `qualite_indicateurs`, `rejets`, `alertes` |

`offre_points_larochelle` réunit toutes les options (arrêts dédoublonnés, stations Citiz, stations vélo) : `offre_id`, `mode`, `source_id`, `node_id`. C'est la définition opérationnelle d'une option pour K1.

## 7. Stratégie de stockage

| Format | Où | Quand | Jamais |
|---|---|---|---|
| Format d'origine | Bronze | Toujours | — |
| GeoParquet | Silver, Gold | Toute table avec une géométrie | Pour Power BI, qui ne le lit pas |
| Parquet | Silver, Gold, exports | Tables sans géométrie ; tous les exports Power BI | — |
| GeoJSON | `gold/exports/` | Une couche de carte, si le visuel Power BI la prend. Test à E10, pas une hypothèse. | Comme format intermédiaire |
| CSV | `reports/tables/` | Petit tableau lisible pour le jury (top des recommandations) | Comme format intermédiaire ou comme entrée de Power BI |

Cartes dans Power BI : exporter les carreaux en points (centroïde en latitude / longitude) colorés par K1. Les carrés en polygones dépendent du visuel disponible. Test à E10.

## 8. Dépendances

```text
BRONZE                SILVER                                         GOLD
S02 ─┐
S01 ─┼─► standardized ─► cleaned ─► deduplicated ─┐
S08 ─┘                                             ├─► spatial/offre_points_larochelle ─┐
S05 ─────► standardized ─► cleaned (RC graphe) ────┤                                     ├─► paires_cellule_offre ─► acces_cellule ─► kpi_couverture
S03 ─┐                                             ├─► spatial/cellules_larochelle ─────┘            │                    └─► agg_distribution_acces
S04 ─┴───► standardized ───────────────────────────┘                                                ├─► desserte_offre
                                                                                                     │
S06a–d, S07, S03, S04 ─► … ─► spatial/cellules_h6, offre_points_h6 ─► h6_jeu_apprentissage ─► h6_evaluation
                                                                                         └─► h6_scores_larochelle ─┐
config (coûts étiquetés) ─► candidats ─► paires_candidat_cellule ─────────────────────────► valeur_candidat ◄──────┘
                                                                                                 │
                                                       scenarios ─► selection_scenario ─► kpi_scenario ─► agg_equite
toutes les tables ─► quality/qualite_indicateurs, rejets, alertes   registre ─► ref_sources        S10 ─► ref_communes
                                                      GOLD ─► exports/pbi_* ─► Power BI
```

Chemin critique du MVP, jusqu'à E7 : S02, S01, S03, S04, S05, puis `offre_points` et `cellules`, puis paires, accès et KPI, candidats, valeur (K6), scénarios. H6 (E8) n'est pas sur le chemin critique : si H6 prend du retard, `valeur_candidat` fonctionne sans `score_h6`.

Les agrégats `agg_distribution_acces` et `agg_equite` servent les pages de démonstration. Ils ne bloquent pas E7.

## 9. Traçabilité

| Niveau | Règle |
|---|---|
| Ligne | Chaque ligne Silver garde les colonnes d'audit de `data_dictionary.md`. Une ligne retirée est dans `rejets`. Une ligne gardée mais signalée est dans `alertes`, et elle reste dans sa table. |
| Table | Chaque table Gold a une colonne `run_id` (date et heure, et hash court du commit Git). |
| Exécution | Un `_manifest.json` par dossier Silver ou Gold à chaque exécution : tables d'entrée et leur SHA-256, tables de sortie et leur SHA-256, hash de `config/`, commit Git, `requirements-lock.txt`. Il est versionné par l'exception déjà en place. |
| Paramètres | Aucun seuil ni coût dans le code. Tout est dans `config/`, chaque coût avec son étiquette. |
| Reproductibilité | Même Bronze, même `config/`, même commit : mêmes SHA-256 en sortie. C'est un test à écrire, à partir de E4. |
| Bronze | Immuable. Une nouvelle date crée un nouveau dossier. |
