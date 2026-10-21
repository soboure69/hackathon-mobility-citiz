# Modèle de données Power BI

**Statut :** Mission 13 (21/10/2026). Écrit par `scripts/build_exports.py` sous le nom `<table>_larochelle.parquet` (sans préfixe `pbi_`), plus `communes_larochelle.geojson` et `carreaux_larochelle.geojson` en WGS84. Lu par l'application Streamlit (P-1 révisée) ; reste lisible par Power BI.

Règles reprises de l'architecture : Power BI lit **seulement** `data/gold/exports/` (AD3), en Parquet, coordonnées en WGS84 (`lat`, `lon`, AD1-AD2), aucune table de paires (AD4). Les KPI sont calculés en Python ; Power BI les affiche, les filtre et les recoupe, il ne les recalcule pas autrement.

## 1. Schéma en étoile

```text
                    pbi_dim_mode (mode)
          ┌───────────┬────────┼──────────┬──────────────┬───────────────┐
          ▼           ▼        ▼          ▼              ▼               ▼
 fact_acces_mode  fact_kpi_  fact_kpi_  dim_offre  fact_distribution  fact_equite_quintile
          ▲       commune    territoire     ▲
          │           ▲                     │
   pbi_dim_cellule ───┼─────────────────────┤
          ▲           │                     │
          └──── pbi_dim_commune ────────────┴──────► pbi_dim_candidat ──► fact_contribution
                                                            │
 pbi_dim_scenario ──► fact_selection ◄──────────────────────┘
        │  └────────► fact_carte_scenario
        └───────────► fact_cellules_gagnees ◄── pbi_dim_cellule

 pbi_dim_source ──► fact_qualite

 Tables isolées (sans relation) : fact_courbe, fact_sensibilite, ref_hypotheses, ref_risques, meta_execution
```

## 2. Tables

Préfixe de fichier : `pbi_<nom>_larochelle.parquet`. Clé = colonne(s) unique(s), contrôlée à l'export.

### Dimensions

| Table | Grain | Clé | Colonnes | Issue de |
|---|---|---|---|---|
| `dim_commune` | commune de l'EPCI (28) | `commune_insee` | `nom` (`nom_officiel`), `pop_filosofi`, `taux_tous_modes`, `taux_citiz`, `prioritaire` (bool), `statut_commune` (« Prioritaire » / « Autre ») | Silver `admin_communes`, Gold `kpi_couverture`, seuil `score.yaml` |
| `dim_mode` | mode (4) | `mode` | `libelle` (Bus, Citiz, Vélo, Tous modes), `ordre`, `couleur` | constante du script |
| `dim_cellule` | carreau 200 m (2 637) | `cell_id` | `commune_insee`, `pop`, `lat`, `lon`, `classe_acces`, `n_options_total`, `desservi_tous`, `desservi_citiz`, `quintile_niveau_vie`, `niveau_vie_moyen`, `est_impute`, `prioritaire` | `acces_cellule` |
| `dim_offre` | station ou arrêt (694) | `offre_id` | `mode`, `nom`, `commune_insee`, `lat`, `lon`, `capacite`, `pop_5min`, `pop_exclusive`, `atteinte` | `desserte_offre` |
| `dim_candidat` | site candidat (Citiz seulement, P-4) | `candidat_id` | `commune_insee`, `retenu`, `motif_exclusion`, `score`, `classe_score`, `rang`, `rang_commune`, `rang_equite`, `pop_rayon`, `pop_nouvelle_isolee` (= `pop_nouvelle`), `taux_redondance`, `frequence_top_n`, `commune_prioritaire`, `lat`, `lon` | `candidats` |
| `dim_scenario` | scénario (12) | `scenario_id` | `libelle`, `scenario` (prudent / central / ambitieux), `ordre_budget`, `hypothese_cout`, `variante` (efficacité / équité), `budget`, `cout_station`, `cout_etiquette`, `n_stations`, `k6`, `k7`, `k8`, `couverture_citiz_avant`, `couverture_citiz_apres`, `couverture_tous_avant`, `couverture_tous_apres`, `pop_sans_option_gagnee`, `pop_gagnee_prioritaire`, `k12_part_prioritaire`, `scenario_reference`, `prix_equite_habitants`, `prix_equite_part`, `statut_solution`, `ecart_relatif_garanti`, `k6_glouton`, `est_reference` (P-3) | `scenarios` + `kpi_scenario` (fusion 1-1) |
| `dim_source` | source | `source_id` | `nom`, `producteur`, `licence`, `url`, `date_donnee` | onglet `sources` du registre |

`kpi_scenario` est fusionné dans `dim_scenario` : une relation 1-1 n'apporte rien et brouille le sens des filtres.

### Faits

| Table | Grain | Clé | Colonnes | Issue de |
|---|---|---|---|---|
| `fact_acces_mode` | carreau × mode (2 637 × 4) | `cell_id`, `mode` | `pop`, `n_options`, `dist_min_m`, `desservi`, `lat`, `lon` | `acces_cellule` dépivoté (`tous` = `n_options_total`, `dist_min_m`, `desservi`) |
| `fact_kpi_commune` | commune × mode (112) | `commune_insee`, `mode` | `pop_totale`, `pop_desservie`, `pop_non_desservie`, `taux_couverture`, `options_moyennes_par_habitant`, `pop_au_moins_2_modes` | `kpi_couverture` (lignes commune) |
| `fact_kpi_territoire` | mode (4) | `mode` | mêmes colonnes | `kpi_couverture` (lignes EPCI) |
| `fact_distribution` | mode × nombre d'options | `mode`, `n_options` | `classe`, `pop`, `n_carreaux` | `agg_distribution_acces` |
| `fact_equite_quintile` | quintile × mode (20) | `quintile`, `mode` | `pop`, `pop_desservie`, `taux_couverture` | `agg_equite` |
| `fact_contribution` | candidat × critère (5) | `candidat_id`, `critere` | `libelle_critere`, `ordre`, `valeur_normalisee` (`n_*`), `contribution` (`contribution_*`) | `candidats` dépivoté |
| `fact_selection` | scénario × station retenue | `scenario_id`, `candidat_id` | `ordre_ajout`, `cout`, `cout_cumule`, `pop_nouvelle_marginale`, `pop_nouvelle_cumulee`, `lat`, `lon` | `selection_scenario` |
| `fact_carte_scenario` | scénario × point de carte | `scenario_id`, `point_id` | `type_point` (« Citiz existante » / « Station proposée »), `nom`, `lat`, `lon`, `taille` (`pop_nouvelle_marginale`, ou `pop_5min` pour l'existant), `ordre_ajout` | `selection_scenario` + stations Citiz de `desserte_offre`, répétées par scénario |
| `fact_cellules_gagnees` | scénario × carreau gagné | `scenario_id`, `cell_id` | `pop`, `prioritaire`, `gain_tous_modes` | `cellules_couvertes_scenario` |
| `fact_qualite` | indicateur (52) | `indicateur_id` | `dimension`, `famille`, `source_id`, `perimetre`, `libelle`, `formule`, `valeur`, `valeur_texte`, `unite`, `seuil`, `statut`, `date_reference` | `qualite_donnees` |

### Tables isolées

| Table | Contenu | Issue de |
|---|---|---|
| `fact_courbe` | `n_stations`, `budget`, `k6`, `gain_marginal`, `k8` (30 lignes) | `courbe_budget_impact` |
| `fact_sensibilite` | `variable`, `facteur`, `spearman`, `recouvrement_top_n` (Citiz) | `sensibilite_ponderations` |
| `ref_hypotheses` | `hypothese_id`, `theme`, `texte`, `valeur`, `nature` (certain / estimé / hypothèse), `document` | `config/powerbi.yaml` (saisie manuelle, versionnée) |
| `ref_risques` | `risque_id`, `libelle`, `probabilite`, `impact`, `mitigation` | `docs/suivi_risques.md` (lecture du tableau) |
| `meta_execution` | `table`, `run_id`, `date_execution_utc`, `commit` | manifestes Gold |

`fact_carte_scenario` existe parce qu'un visuel Azure Maps ne lit qu'une table de points. Répéter les 24 stations Citiz existantes dans chacun des 12 scénarios (288 lignes) permet de filtrer la carte par scénario avec une relation simple, sans mesure de filtre.

## 3. Relations

Toutes en **un-à-plusieurs, filtre à sens unique** (de la dimension vers le fait). Aucune relation bidirectionnelle, aucune relation 1-1, aucune relation plusieurs-à-plusieurs.

| De (1) | Vers (*) | Colonne |
|---|---|---|
| `dim_commune` | `dim_cellule`, `fact_kpi_commune`, `dim_offre`, `dim_candidat` | `commune_insee` |
| `dim_mode` | `fact_acces_mode`, `fact_kpi_commune`, `fact_kpi_territoire`, `dim_offre`, `fact_distribution`, `fact_equite_quintile` | `mode` |
| `dim_cellule` | `fact_acces_mode`, `fact_cellules_gagnees` | `cell_id` |
| `dim_candidat` | `fact_contribution`, `fact_selection` | `candidat_id` |
| `dim_scenario` | `fact_selection`, `fact_carte_scenario`, `fact_cellules_gagnees` | `scenario_id` |
| `dim_source` | `fact_qualite` | `source_id` |

Chemins vérifiés sans ambiguïté : `dim_commune` n'atteint `fact_acces_mode` que par `dim_cellule`, et `fact_selection` que par `dim_candidat`. `dim_candidat.type_equipement` n'est **pas** relié à `dim_mode` : le segment « mode » de la page 2 ne doit pas filtrer les candidats de la page 3.

## 4. Contrôles à l'export (bloquants)

| ID | Contrôle |
|---|---|
| X-01 | Clé unique dans chaque table |
| X-02 | Toute clé étrangère existe dans sa dimension (intégrité référentielle) |
| X-03 | `lat` ∈ [45,9 ; 46,4], `lon` ∈ [−1,5 ; −0,7] (emprise large de l'EPCI) |
| X-04 | Σ `fact_acces_mode.pop` (mode = tous) = `fact_kpi_territoire.pop_totale` (tous) |
| X-05 | Pour chaque scénario, Σ `fact_cellules_gagnees.pop` = `dim_scenario.k6` |
| X-06 | 12 scénarios, dont 3 en variante équité, et un seul `est_reference` |
| X-07 | Aucune colonne `geometry` binaire (Power BI ne lit pas le WKB) |

## 5. Équivalent Streamlit (secours, décision P-1)

Mêmes fichiers `pbi_*`, lus par `pandas`. Une page Streamlit par page du rapport (`st.navigation`), cartes en `pydeck` (couche de points et polygones GeoJSON), mesures DAX remplacées par des fonctions Python dans `src/export/mesures.py`, testées par `pytest`. Les contrôles X-01 à X-07 restent identiques.
