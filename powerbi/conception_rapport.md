# Conception du rapport Power BI

**Statut :** conception validée le 21/10/2026 (P-1 à P-6). **P-1 révisée le 21/10/2026 : la restitution est une application Streamlit** (`app/`), qui applique cette conception page par page ; équivalences dans `docs/application.md`. Les chiffres d'équité de la page 4 sont ceux du run `20261021T084710Z_5c8ceff` (12 scénarios).

Documents liés : `dataset_schema/modele_donnees.md` (tables, relations, contrôles d'export), `measures_dax.md` (code DAX), `pages_wireframe.md` (maquettes textuelles), `assets/theme_hackathon.json` (thème).

## 0. Principes

| # | Principe | Conséquence |
|---|---|---|
| 1 | Une page = une question de décision | Le titre de page est la réponse, pas le sujet (« 10 stations couvrent 18 816 habitants de plus », pas « Optimisation ») |
| 2 | Python calcule, Power BI montre | Aucun KPI recalculé autrement en DAX ; trois mesures de contrôle prouvent l'égalité (page 5) |
| 3 | Un mot = une notion | Toujours distinguer *couverture des données* / *couverture de mobilité* ; *score de potentiel* / *prédiction* (il n'y a pas de prédiction) ; *population couverte* / *nouvellement couverte* |
| 4 | Chaque chiffre a son étiquette de certitude | Valeurs issues de données = certaines ; coûts et budgets = « hypothèse de simulation » ou « estimation publique », affichées à côté du chiffre |
| 5 | Lisible par un décideur en 30 secondes | Au plus 4 cartes KPI et 1 carte géographique par page ; le détail technique est en page 5 |

Canevas 16:9 (1280 × 720). Thème `theme_hackathon.json`. Langue et paramètres régionaux : français (France).

## 1. Page 1 — Executive overview

**Objectif décisionnel.** En 30 secondes : quelle est la situation, que recommande-t-on, combien ça coûte, quel est le compromis équité.

**KPI.** Couverture Citiz actuelle (9,8 %), habitants sans aucune option (38 672), habitants nouvellement couverts par le scénario de référence (K6), coût par habitant (K8), prix de l'équité.

**Tables Gold.** `dim_scenario`, `fact_carte_scenario`, `fact_selection`, `dim_candidat`, `dim_commune`, `fact_kpi_territoire`, `dim_cellule`.

**Visuels et champs.**

| Visuel | Type | Champs |
|---|---|---|
| V1.1 – V1.4 | 4 cartes KPI | `Taux de couverture Citiz` · `Population sans aucune option` · `Habitants nouvellement couverts (référence)` + sous-titre « Couverture Citiz 9,8 % → 20,6 % » · `Coût par habitant (référence)` + étiquette `cout_etiquette` |
| V1.5 | Azure Maps, couche bulles + couche de référence | Lat/Long : `fact_carte_scenario[lat]`, `[lon]` ; Légende : `type_point` ; Taille : `taille` ; Info-bulle : `nom`, `ordre_ajout`. Couche de référence : `pbi_communes_larochelle.geojson` (contour des communes, prioritaires en contour violet) |
| V1.6 | Tableau « Top stations » | `fact_selection[ordre_ajout]`, `dim_commune[nom]`, `pop_nouvelle_marginale`, `pop_nouvelle_cumulee`, `cout_cumule` |
| V1.7 | Carte multiligne « Efficacité ou équité » | Pour le même budget : `Habitants nouvellement couverts` des deux variantes, `Prix de l'équité (habitants)`, `Habitants gagnés en communes prioritaires` |
| V1.8 | Zone de texte | 3 phrases de synthèse (message métier ci-dessous) |

**Filtres et segments.** Aucun segment visible. Filtre de page : `dim_scenario[est_reference] = vrai` sur V1.5 et V1.6 ; V1.7 filtré sur les deux scénarios du budget de référence.

**Interactions.** Clic sur une ligne de V1.6 → met en surbrillance la station sur V1.5. Les cartes KPI ne sont pas filtrées par les clics (interaction « aucune »).

**Mesures DAX.** `Taux de couverture Citiz`, `Population sans aucune option`, `Habitants nouvellement couverts (référence)`, `Coût par habitant (référence)`, `Prix de l'équité (habitants)`.

**Messages métier.**
1. Aujourd'hui, moins d'un habitant sur dix a une station Citiz à 5 minutes à pied.
2. Avec 85 000 € sur 3 ans, 10 stations bien placées doublent cette couverture (9,8 % → 20,6 %), pour 4,52 € par habitant gagné.
3. Ce choix ne profite à aucune commune peu desservie ; imposer 30 % des gains dans ces communes coûte environ un quart de l'impact.

**Erreurs à éviter.** Plus de 4 KPI ; un « score » affiché comme une prévision de fréquentation ; un coût sans son étiquette d'hypothèse ; une carte sans légende ni contour des communes ; vert/rouge comme seul code.

## 2. Page 2 — Couverture actuelle

**Objectif décisionnel.** Où sont les habitants mal desservis aujourd'hui, par quel mode, et qui sont-ils (communes, revenu).

**KPI.** Taux de couverture à 5 min par mode (K2), population desservie / non desservie (K1, K3), options par habitant (K4), habitants sans aucune option, écart de couverture entre quintiles de niveau de vie.

**Tables Gold.** `fact_acces_mode`, `dim_cellule`, `dim_mode`, `dim_commune`, `fact_kpi_commune`, `fact_distribution`, `fact_equite_quintile`, `dim_offre`.

**Visuels et champs.**

| Visuel | Type | Champs |
|---|---|---|
| V2.1 – V2.4 | 4 cartes KPI | `Taux de couverture` · `Population desservie` · `Population non desservie` · `Options par habitant` (mode du segment) |
| V2.5 | Azure Maps, bulles (carreaux) | Lat/Long : `fact_acces_mode[lat]`, `[lon]` ; Légende : `desservi` (« Desservi » / « Non desservi ») ; Taille : `pop` ; Info-bulle : `dim_commune[nom]`, `n_options`, `dist_min_m` |
| V2.6 | Azure Maps, bulles (offre) — même visuel, 2e couche si disponible, sinon visuel séparé | `dim_offre[lat]`, `[lon]`, `mode` |
| V2.7 | Histogramme empilé | Axe : `fact_distribution[classe]` (0, 1-2, 3-5, 6+) ; Valeurs : `pop` |
| V2.8 | Barres horizontales triées | Axe : `dim_commune[nom]` ; Valeur : `fact_kpi_commune[taux_couverture]` ; ligne de référence à 60 % ; couleur par `statut_commune` |
| V2.9 | Colonnes groupées | Axe : `fact_equite_quintile[quintile]` (1 = plus modeste) ; Valeur : `Taux quintile` |
| V2.10 | Tableau « communes sous-desservies » | `dim_commune[nom]`, `fact_kpi_commune[pop_totale]`, `pop_non_desservie`, `taux_couverture` ; filtre visuel : `prioritaire = vrai` |

**Filtres et segments.** Segment `dim_mode[libelle]` en boutons, **sélection unique**, valeur par défaut « Tous modes ». Segment `dim_commune[nom]` en liste déroulante, sélection multiple.

**Interactions.** Le segment mode filtre V2.1-V2.9 ; il ne filtre pas V2.10 (la priorité se définit tous modes). Clic sur une commune de V2.8 → filtre V2.5 et V2.10. Extraction (drillthrough) depuis toute commune des pages 3 et 4 vers cette page.

**Mesures DAX.** `Population desservie`, `Population non desservie`, `Taux de couverture`, `Options par habitant`, `Population sans aucune option`, `Taux quintile`, `Écart Q1 - Q5 (points)`.

**Messages métier.**
1. Le bus couvre 76 % des habitants, Citiz 9,8 %, le vélo en libre-service 29 % ; 22 % n'ont aucune option à 5 minutes.
2. Neuf communes sur 28 sont sous 60 % de couverture tous modes (de 35 % à 59 %).
3. Les ménages les plus modestes (quintile 1) sont les mieux couverts (89 % tous modes, contre 71 % à 77 % pour les autres quintiles) : le manque ne touche pas d'abord les ménages modestes.

**Erreurs à éviter.** Additionner les modes (un habitant desservi par bus et vélo compte une fois en « tous modes ») ; laisser le segment mode en sélection multiple (les mesures renvoient vide) ; une carte de 2 637 bulles toutes de même couleur ; un histogramme en nombre de carreaux au lieu d'habitants.

## 3. Page 3 — Zones candidates et score de potentiel

**Objectif décisionnel.** Quels sites ont le plus de potentiel, pourquoi (composantes), et le classement est-il robuste.

**KPI.** Candidats retenus (2 200 Citiz), score de potentiel K10 (sur 100), habitants gagnés si le site était seul (K6 isolé), taux de redondance (K9), stabilité du rang.

**Tables Gold.** `dim_candidat`, `fact_contribution`, `dim_commune`, `fact_sensibilite`.

**Visuels et champs.**

| Visuel | Type | Champs |
|---|---|---|
| V3.1 – V3.3 | 3 cartes KPI | `Candidats retenus` · `Score` du site sélectionné · `Habitants gagnés (site seul)` |
| V3.4 | Azure Maps, bulles | `dim_candidat[lat]`, `[lon]` ; Légende : `classe_score` (5 classes) ; Taille : `pop_nouvelle_isolee` ; Info-bulle : page info-bulle « Candidat » |
| V3.5 | Barres empilées horizontales (top 20) | Axe : `candidat_id` (libellé commune + rang) ; Légende : `fact_contribution[libelle_critere]` ; Valeur : `Contribution` ; filtre Top N = 20 par `score` |
| V3.6 | Nuage de points « impact / redondance » | X : `taux_redondance` ; Y : `pop_nouvelle_isolee` ; Taille : `score` ; Légende : `commune_prioritaire` |
| V3.7 | Tableau | `rang`, `dim_commune[nom]`, `score`, `pop_nouvelle_isolee`, `taux_redondance`, `frequence_top_n`, `Coût par habitant (site seul)` |
| V3.8 | Tableau de sensibilité | `fact_sensibilite[variable]`, `facteur`, `spearman`, `recouvrement_top_n` |

**Filtres et segments.** `dim_candidat[retenu]` (filtre de page = vrai, non visible) ; segment `dim_commune[nom]` ; segment `commune_prioritaire` ; curseur `score` (plage).

**Interactions.** Clic sur un site (V3.4, V3.5, V3.7) → filtre V3.2, V3.3 et la décomposition. V3.8 n'est filtré par rien.

**Mesures DAX.** `Candidats retenus`, `Score`, `Habitants gagnés (site seul)`, `Coût par habitant (site seul)`, `Redondance moyenne`, `Stabilité top N`, `Contribution`.

**Messages métier.**
1. Le score classe des sites ; il ne prédit pas une fréquentation (aucun historique d'usage n'est disponible).
2. Chaque score se lit par ses composantes : impact, besoin, complémentarité avec le bus, logement collectif, petits ménages.
3. L'ordre d'ensemble est stable quand on change une pondération (Spearman ≥ 0,978), mais le top 20 l'est moins (35 % à 90 % de sites communs) : les meilleurs sites ont des scores très proches (79 à 81 sur 100), et 19 des 20 premiers sont à La Rochelle même.
4. C'est pourquoi le score ne sert qu'à départager : la sélection finale se fait en page 4, en comptant chaque habitant une seule fois.

**Erreurs à éviter.** Additionner les « habitants gagnés » de plusieurs sites (les rayons se chevauchent — la mesure renvoie vide) ; écrire « prédiction », « demande » ou « fréquentation attendue » ; montrer les 2 200 sites en tableau sans tri ni filtre ; une palette arc-en-ciel pour le score.

## 4. Page 4 — Optimisation budgétaire

**Objectif décisionnel.** Pour un budget donné, quel portefeuille financer, avec quel impact, et que coûte l'équité.

**KPI.** Stations financées, K6, K7, K8, couverture Citiz avant → après, gain tous modes, part des gains en communes prioritaires (K12), prix de l'équité, budget non utilisé.

**Tables Gold.** `dim_scenario`, `fact_selection`, `fact_carte_scenario`, `fact_cellules_gagnees`, `dim_cellule`, `fact_courbe`, `dim_candidat`, `dim_commune`.

**Visuels et champs.**

| Visuel | Type | Champs |
|---|---|---|
| V4.0 | Zone de texte dynamique | `Titre page 4` ; `Message scénario` |
| V4.1 – V4.4 | 4 cartes KPI | `Stations financées` · `Habitants nouvellement couverts` · `Coût par habitant` (+ `cout_etiquette`) · `Part des gains en communes prioritaires` |
| V4.5 | Azure Maps | `fact_carte_scenario` (comme V1.5), filtré par le scénario choisi |
| V4.6 | Courbe « budget → impact » | X : `fact_courbe[n_stations]` (ou `budget`) ; Y : `k6` ; colonnes secondaires : `gain_marginal` |
| V4.7 | Nuage « coût / impact des 12 scénarios » | X : `dim_scenario[k7]` ; Y : `k6` ; Légende : `variante` ; Étiquette : `libelle` |
| V4.8 | Colonnes groupées « prix de l'équité » | Axe : `dim_scenario[scenario]` (prudent, central, ambitieux) ; Légende : `variante` ; Valeur : `k6` ; filtre : `hypothese_cout = central` |
| V4.9 | Tableau portefeuille | `fact_selection[ordre_ajout]`, `dim_commune[nom]`, `dim_candidat[score]`, `cout`, `cout_cumule`, `pop_nouvelle_marginale`, `pop_nouvelle_cumulee` |
| V4.10 | Courbe en escalier | X : `ordre_ajout` ; Y : `pop_nouvelle_cumulee` (rendements décroissants du portefeuille) |

**Filtres et segments.** Trois segments en boutons, **sélection unique obligatoire** : budget (`scenario` : prudent 42 500 € / central 85 000 € / ambitieux 170 000 €), coût par station (`hypothese_cout` : bas / central / haut), variante (`variante` : efficacité / équité). Défaut : central, central, efficacité. Signets « Efficacité » / « Équité » sur deux boutons.

**Interactions.** Les segments filtrent V4.0-V4.5, V4.9, V4.10. Ils ne filtrent **pas** V4.6, V4.7, V4.8 (vue d'ensemble, interaction « aucune »). Clic sur une station de V4.9 → surbrillance sur V4.5. Clic sur un point de V4.7 → filtre la page sur ce scénario.

**Mesures DAX.** Dossier `Scénario` de `measures_dax.md`, et `Écart K6` (contrôle, page 5).

**Messages métier.**
1. Les premières stations rapportent le plus : la 1re couvre 4 040 habitants, la 30e moins de 900.
2. Le coût par station pèse autant que le budget : à 85 000 €, entre coût haut et coût bas, l'impact passe de 12 888 à 30 834 habitants.
3. L'équité a un prix mesuré : −23 % d'habitants au budget central, pour 4 674 habitants gagnés dans les communes prioritaires au lieu de 0. Elle touche aussi plus d'habitants sans aucune option.
4. La solution est un optimum prouvé (écart garanti 0,1 %), pas une liste triée ; une règle simple fait presque aussi bien (8 cas sur 9).

**Erreurs à éviter.** Présenter un budget de simulation comme un budget voté ; laisser une combinaison vide sans message (équité au coût bas) ; additionner les K6 de plusieurs scénarios ; une courbe sans unité (stations ou euros) ; masquer le budget non utilisé.

## 5. Page 5 — Méthodologie, qualité, limites et risques

**Objectif décisionnel.** Peut-on faire confiance aux chiffres, et dans quelles limites.

**KPI.** Indicateurs de qualité conformes / en alerte (40 / 3, 9 informatifs), couverture des données du périmètre (CM-01), fraîcheur des sources, contrôles de recoupement (= 0), dernière exécution.

**Tables Gold.** `fact_qualite`, `dim_source`, `ref_hypotheses`, `ref_risques`, `meta_execution`, `fact_kpi_territoire`, `dim_scenario`.

**Visuels et champs.**

| Visuel | Type | Champs |
|---|---|---|
| V5.1 – V5.3 | 3 cartes KPI | `Part des indicateurs conformes` · `Indicateurs en alerte` · `Dernière exécution` |
| V5.4 | Schéma du pipeline (image) | `assets/pipeline.png` : sources → Bronze → Silver → Gold → Power BI |
| V5.5 | Matrice | Lignes : `fact_qualite[dimension]` ; Colonnes : `statut` ; Valeur : nombre ; mise en forme : icône + couleur |
| V5.6 | Tableau des alertes | `indicateur_id`, `libelle`, `valeur`, `seuil`, `source_id` ; filtre : `statut = alerte` |
| V5.7 | Tableau des sources | `dim_source[source_id]`, `nom`, `producteur`, `licence`, `date_donnee` |
| V5.8 | Tableau des hypothèses | `ref_hypotheses[theme]`, `texte`, `valeur`, `nature` (icône : ● certain, ◐ estimé, ○ hypothèse) |
| V5.9 | Tableau des risques | `ref_risques[risque_id]`, `libelle`, `impact`, `mitigation` (risques ouverts) |
| V5.10 | Cartes de contrôle | `Écart couverture PBI - Python`, `Écart K6`, `Écart gains marginaux` → toutes à 0 |

**Filtres et segments.** Segment `fact_qualite[famille]` (qualité / couverture des données / couverture de mobilité).

**Interactions.** Le segment filtre V5.5 et V5.6 seulement.

**Mesures DAX.** Dossier `Qualité` de `measures_dax.md`.

**Messages métier.**
1. Les chiffres sont reproductibles : chaque table porte son `run_id`, ses sources et leurs empreintes.
2. Trois alertes sont connues et sans effet sur la recommandation : capacité des stations GBFS non renseignée, flux GBFS vieux de 126 jours, 98,3 % des nœuds piétons dans la composante principale.
3. Limites : pas d'historique d'usage (donc score, pas prédiction) ; coûts et budgets en hypothèse ; marche à 5 minutes sur réseau OSM ; carreaux imputés par l'INSEE (secret statistique).
4. Enjeux : aucune donnée personnelle ; carreaux de 200 m agrégés par l'INSEE ; accessibilité des stations aux personnes à mobilité réduite non mesurée.

**Erreurs à éviter.** Une page de texte dense ; des alertes cachées ; confondre couverture des données (CM-01) et couverture de mobilité (K2) ; des liens vers des sources sans licence ni date.

## 6. Convention de couleurs accessible

Base : palette Okabe-Ito (lisible par les principales formes de daltonisme). Les couleurs de remplissage ont un contraste d'au moins 3:1 sur blanc (WCAG 1.4.11) ; le texte utilise les variantes foncées, d'au moins 4,5:1 (WCAG 1.4.3). **Jamais la couleur seule** : chaque statut a aussi un libellé ou une icône.

| Rôle | Remplissage | Texte | Contraste (remplissage / texte) | Usage |
|---|---|---|---|---|
| Couvert, existant, efficacité | `#0072B2` | `#0072B2` | 5,2 / 5,2 | Carreaux desservis, stations Citiz existantes, variante efficacité |
| Non desservi, manque, alerte | `#D55E00` | `#A6411A` | 3,9 / 6,2 | Carreaux non desservis, indicateurs en alerte |
| Station proposée, gain | `#009E73` | `#007A5A` | 3,4 / 5,3 | Nouvelles stations, habitants gagnés |
| Équité, commune prioritaire | `#CC79A7` | `#B2186F` | 3,1 / 6,5 | Variante équité, contour des communes prioritaires |
| Neutre, contexte | `#6E6E6E` | `#6E6E6E` | 5,1 / 5,1 | Bus, éléments secondaires |
| Texte | — | `#1A1A1A` | 17,4 | Tout le texte |

Modes (page 2) : Bus `#6E6E6E`, Citiz `#0072B2`, Vélo `#CC79A7`, Tous modes `#1A1A1A`. Le jaune-orangé `#E69F00` (2,3:1) est exclu des marques et du texte.

Échelle séquentielle (score, nombre d'options) : bleus `#EFF3FF` → `#BDD7E7` → `#6BAED6` → `#3182BD` → `#08519C`. Jamais d'arc-en-ciel.

Statuts qualité : ✓ ok `#0072B2` · ⚠ alerte `#D55E00` · ⓘ info `#6E6E6E`.

À vérifier à la construction : mode « contraste élevé » de Windows, et un simulateur de daltonisme sur une capture de chaque page.

## 7. Navigation

| Élément | Choix |
|---|---|
| Barre du haut, sur chaque page | Navigateur de pages natif (5 boutons), page active soulignée ; à droite, « Données au … » (`Dernière exécution`) |
| Ordre de lecture | De gauche à droite et de haut en bas : titre-réponse → KPI → carte → détail |
| Fil de la démonstration | 1 → 2 → 3 → 4 → 1 (retour à la recommandation) ; la page 5 sert aux questions du jury |
| Extraction (drillthrough) | Clic droit sur une commune (pages 3 et 4) → page 2 filtrée sur cette commune ; bouton « Retour » |
| Page info-bulle « Candidat » | Masquée ; mini-barres des 5 contributions, score, rang, habitants gagnés (site seul) |
| Signets | Page 4 : « Efficacité » et « Équité » (segments préréglés au budget central) ; page 1 : « Vue jury » (sans infobulles) |
| Accessibilité | Texte de remplacement sur chaque visuel ; ordre de tabulation réglé ; titres de visuels explicites |

## 8. Carte : choix technique et secours

Les visuels Bing (Carte, Carte remplie) sont annoncés en dépréciation ; Microsoft recommande le visuel **Azure Maps**, qui gère couches de bulles, couche remplie et couche de référence. Il doit être activé (portail d'administration, paramètres d'intégration) et il a besoin d'Internet pendant la démonstration.

| Besoin | Solution retenue | Secours |
|---|---|---|
| Carreaux, stations, candidats | Azure Maps, couche de bulles (lat/lon des centroïdes) | Image PNG générée en Python (vrais carrés de 200 m) dans `powerbi/assets/` |
| Contour des communes | Couche de référence Azure Maps, `pbi_communes_larochelle.geojson` (WGS84, simplifié) — import GeoJSON à confirmer en E-1 | Visuel Carte de formes (préversion) avec TopoJSON |
| Démonstration sans réseau | — | Captures de chaque page + PNG, dans `powerbi/assets/` et le support de soutenance |

Streamlit (si P-1 le décide) : `pydeck`, polygones des carreaux et des communes affichés directement.

## 9. Décisions à valider avant l'export

| # | Décision | Proposition |
|---|---|---|
| P-1 | Outil | **Power BI Desktop** (attendu par le jury, page Méthodologie native). Streamlit seulement en secours, sur les mêmes exports |
| P-2 | Cartes | Azure Maps (bulles + référence) ; PNG Python en secours systématique |
| P-3 | Scénario de référence (page 1) | `SC_central_central` (85 000 €, 8 500 €/station, efficacité), avec sa variante équité à côté. La recommandation finale (efficacité ou équité) reste un choix politique montré, pas tranché par l'outil |
| P-4 | Périmètre des candidats | Citiz seulement (D-1) ; bus et vélo hors rapport |
| P-5 | Export | `scripts/build_exports_powerbi.py` + `config/powerbi.yaml` (hypothèses de la page 5) ; 22 tables `pbi_*` + 1 GeoJSON ; contrôles X-01 à X-07 ; tests |
| P-6 | Prérequis | **Fait** le 21/10/2026 : 12 scénarios commités, run `20261021T084710Z_5c8ceff`. Ne pas relancer l'optimisation pour l'export |
