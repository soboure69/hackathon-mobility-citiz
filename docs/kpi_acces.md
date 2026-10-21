# KPI Gold d'accessibilité et de couverture

**Statut :** calculés le 21/10/2026 sur la CA de La Rochelle (script `scripts/build_kpi_acces.py`, module `src/features/kpi_acces.py`).
**Niveau principal :** carreau Filosofi de 200 m (`cell_id` = `idcar_200m`).
**Source unique des distances :** `gold/accessibility/paires_cellule_offre_larochelle`, méthode `reseau`, variante `reference` (accès + réseau + accès ≤ 400 m).
**Hors périmètre :** score de potentiel, optimisation.

## 1. Table principale : `acces_cellule_larochelle` (une ligne par carreau, GeoParquet EPSG:2154)

| Groupe | Colonnes |
|---|---|
| Clé et territoire | `cell_id`, `commune_insee`, `epci_siren`, `code_departement`, `code_region`, `territoire` |
| Population (Filosofi) | `pop` (= `ind`), `men`, `men_pauv`, `ind_snv`, les autres variables Filosofi ; `est_impute`, `multi_commune`, `partiel_epci` |
| Position | `geometry` (carré), `x_centroide`, `y_centroide`, `lon_centroide_wgs84`, `lat_centroide_wgs84`, `node_id`, `dist_snap_m` |
| K1 | `n_options_total`, `n_options_bus`, `n_options_citiz`, `n_options_velo`, `options_pour_1000_hab`, `classe_acces` (0, 1-2, 3-5, 6+) |
| Modes | `n_modes` (0 à 3) |
| Desserte | `desservi`, `desservi_bus`, `desservi_citiz`, `desservi_velo` |
| Distance | `dist_min_m`, `dist_min_bus_m`, `dist_min_citiz_m`, `dist_min_velo_m` (vide si aucune option à ≤ 400 m) |
| Équité | `niveau_vie_moyen` (= `ind_snv` / `ind`), `quintile_niveau_vie` (pondéré par la population) |
| Audit | colonnes d'audit Silver, `run_id` |

## 2–3. KPI : définition métier, technique, formule

| KPI | Définition métier | Formule |
|---|---|---|
| **K1** options accessibles | Combien d'arrêts et de stations un habitant du carreau atteint en 5 min | `n_options_<mode>` = nombre d'`offre_id` distincts avec une paire de référence |
| K1 bis | Même chose ramenée à la population | `n_options_total / pop × 1000` (vide si `pop` < 1) |
| **Modes accessibles** | Combien de **types** de mobilité sont à portée | `n_modes` = nombre de modes avec `n_options_<mode>` > 0 |
| Distance minimale | À quelle distance de marche est l'option la plus proche | `min(dist_totale_m)` sur les paires du carreau |
| **K2** taux de couverture | Part des habitants avec au moins une option | Σ pop (desservi) / Σ pop |
| **K3** population desservie | Habitants avec au moins une option | Σ pop des carreaux `desservi` |
| **K4** population non desservie | Habitants sans option | Σ pop − K3 |
| **K5** population par option | Habitants à 5 min d'un arrêt ou d'une station | `pop_5min` (non exclusive) et `pop_exclusive` |
| **K6** population nouvellement couverte | Habitants qu'un scénario ferait passer de « sans option » à « avec option » | Σ pop des carreaux non desservis aujourd'hui et atteints par le scénario (fonction écrite et testée ; valeur à E7) |
| Options par habitant | Offre moyenne vue par un habitant | Σ (n_options × pop) / Σ pop |
| Multimodalité | Habitants avec au moins 2 modes | Σ pop (`n_modes` ≥ 2) |
| **K12** équité (état actuel) | La couverture dépend-elle du revenu ? | K2 par quintile de niveau de vie |

## 4. Couverte, non desservie, nouvellement couverte

| Notion | Ensemble de carreaux | Dépend d'un scénario ? |
|---|---|---|
| Couverte (K3) | carreaux avec au moins une paire de référence | Non |
| Non desservie (K4) | carreaux sans paire | Non |
| Nouvellement couverte (K6) | carreaux **non desservis aujourd'hui** ∩ carreaux atteints par les nouvelles implantations | Oui |

Un carreau déjà desservi n'ajoute **rien** à K6, même s'il gagne une option. K6 se calcule aussi par mode : un carreau desservi par le bus mais pas par Citiz peut être « nouvellement couvert par Citiz ».

## 5. Compter les modes sans les répéter

- On compte les **options** par mode (`nunique` sur `offre_id`), puis les **modes** comme le nombre de modes dont le compte est positif.
- Deux arrêts de bus à 5 min ajoutent 2 options, mais **un seul** mode.
- Contrôles : `n_options_total` = Σ des options par mode (K-T4) ; `n_modes` = nombre de `desservi_<mode>` vrais (K-T5).

## 6. Éviter le double comptage entre isochrones

Les zones de 5 min de deux arrêts voisins se recouvrent. Additionner leurs populations compterait deux fois les mêmes habitants.

1. **On ne manipule pas de polygones d'isochrones :** l'accessibilité est une propriété du **carreau**, qui n'est compté qu'une fois.
2. **La couverture** (K2, K3) est une somme sur les carreaux distincts atteints.
3. **La population par option** existe en deux versions :
   - `pop_5min`, **non exclusive** : utile pour dire combien d'habitants un arrêt dessert, mais **jamais additionnée** ;
   - `pop_exclusive` : chaque carreau est donné, pour chaque mode, à son option **la plus proche** (à égalité, le plus petit `offre_id`). La somme par mode **égale** la population couverte par ce mode (K-T3).

## 7. Agrégations

`kpi_couverture_larochelle` : une ligne par (`perimetre_type`, `perimetre_id`, `mode`), avec `mode` ∈ {tous, bus, citiz, velo}.

| Périmètre | Colonne | Remarque |
|---|---|---|
| EPCI (= territoire d'étude) | `epci_siren` | Le département et la région ne sont pas agrégés à part : sur ce territoire, ils ne contiennent que l'EPCI. Les codes restent dans la table carreau |
| Commune | `commune_insee` (RF-01) | La somme des 28 communes redonne l'EPCI (K-T2) |

Colonnes : `pop_totale`, `pop_desservie`, `pop_non_desservie`, `taux_couverture`, `n_carreaux`, `n_carreaux_desservis`, `options_moyennes_par_habitant`, `pop_au_moins_2_modes` (mode `tous`).

## 8. Tables Gold produites

| Dossier | Table | Clé | Usage |
|---|---|---|---|
| accessibility | `acces_cellule_larochelle` | `cell_id` | Carte O1, base de tous les KPI |
| accessibility | `desserte_offre_larochelle` | `offre_id` | Carte O2 (K5 non exclusif et exclusif) |
| accessibility | `kpi_couverture_larochelle` | `perimetre_type`, `perimetre_id`, `mode` | Cartes de synthèse, classement des communes |
| dashboards | `agg_distribution_acces_larochelle` | `mode`, `n_options` | Histogramme de la page 2 |
| dashboards | `agg_equite_larochelle` | `quintile_niveau_vie`, `mode` | Équité (K12, état actuel) |

## 9. Indicateurs prioritaires pour Power BI

| Priorité | Indicateur | Visuel | Page |
|---|---|---|---|
| 1 | K2 tous modes (77,8 %) et K4 (38 672 habitants) | Cartes de synthèse | 1, 2 |
| 2 | K1 par carreau | Carte de chaleur des centroïdes (point coloré par `classe_acces`) | 2 |
| 3 | K2 par mode, dont **Citiz : 9,8 %** | Barres horizontales | 1, 2 |
| 4 | K2 par commune | Carte des communes et tableau trié | 2 |
| 5 | K5 par option | Carte des points, taille = `pop_5min` | 2 |
| 6 | Distribution de K1 | Histogramme de population | 2 |
| 7 | K12 actuel | Barres par quintile | 5 (et 4 plus tard) |

## 10. Tests

| Code | Vérification | Où |
|---|---|---|
| K-T1 | population desservie ≤ population totale, partout | script (arrêt) |
| K-T2 | Σ des communes = EPCI, pour chaque mode | script (arrêt) |
| K-T3 | Σ `pop_exclusive` d'un mode = population couverte par ce mode | script (arrêt) |
| K-T4 | `n_options_total` = Σ des options par mode | script (arrêt) |
| K-T5 | `n_modes` = nombre de modes desservis | script (arrêt) |
| K-T6 | taux EPCI tous modes = CM-01 du tableau qualité (deux codes, même chiffre) | script (arrêt) |
| K-T7 | toute distance minimale ≤ 400 m | script (arrêt) |
| K-T8 | un carreau sans paire n'est jamais déclaré desservi | script (arrêt) |
| Tests unitaires | modes comptés une fois, exclusivité, agrégations, K6, quintiles pondérés, paires en double | `tests/test_kpi_acces.py` |

## Résultats du 21/10/2026 (CA de La Rochelle, 174 016 habitants)

| Mode | Population desservie | Taux | Non desservie |
|---|---:|---:|---:|
| Tous | 135 344 | 77,8 % | 38 672 |
| Bus | 132 438 | 76,1 % | 41 578 |
| Vélo | 49 670 | 28,5 % | 124 346 |
| Citiz | 17 084 | 9,8 % | 156 932 |

- Commune de La Rochelle : 90,5 % ; cinq communes de périphérie entre 35 et 48 %.
- 48 896 habitants ont au moins 2 modes à 5 min.
- Équité : le quintile au niveau de vie le plus bas est le mieux couvert (89,2 % ; 71 à 77 % pour les autres). Hypothèse à vérifier : il habite surtout le centre dense. Ce n'est pas encore un constat.
