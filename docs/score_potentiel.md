# Sites candidats et score de potentiel territorial (K10)

**Statut :** calculé le 21/10/2026 sur la CA de La Rochelle (`scripts/build_candidats.py`, `src/scoring/candidats.py`, paramètres dans `config/score.yaml`).
**Nature du score :** une **note de priorité multicritère**, construite à partir de données observées. Aucune donnée d'usage n'existe (H5) : le score **n'est pas** une prédiction de fréquentation, de réservations ou de chiffre d'affaires, et il ne doit jamais être présenté ainsi.
**Hors périmètre :** optimisation budgétaire (le score note chaque site **seul**).
**H6** (modèle sur cible proxy, option A) reste un complément à E8. Il ne remplace pas K10.

## 1. Définition d'un site candidat

- Un **site candidat** est un **nœud routable** du réseau piéton auquel au moins un carreau peuplé est rattaché. Une station se pose sur le réseau, pas au milieu d'un carreau.
- 2 637 carreaux → **2 547 sites** (plusieurs carreaux peuvent partager un nœud).
- Identifiant : `C_<cell_id du carreau le plus peuplé rattaché à ce nœud>`.
- Un site est évalué pour **3 types d'équipement** : `citiz` (cible principale), `velo`, `bus`.
- **Zone atteinte** d'un site : les carreaux à ≤ 400 m, soit l'accès du carreau + la distance réseau jusqu'au site (même règle que pour l'offre existante).

## 2. Règles d'exclusion (par type)

| Ordre | Règle | Types | Motif écrit | Exclus (citiz / vélo / bus) |
|---|---|---|---|---|
| 1 | Site hors du contour de l'EPCI (dans le tampon) | tous | `hors EPCI` | 17 / 17 / 17 |
| 2 | Aucune voie carrossable autour du nœud (sentier, piéton, `trunk`) | citiz, bus | `pas d'accès voiture` | 299 / — / 299 |
| 3 | Aucun habitant nouvellement couvert : toute la zone atteinte est déjà desservie par ce type | tous | `aucun habitant nouvellement couvert` | 14 / 118 / 728 |
| 4 | Redondance > 80 % : moins d'1 habitant atteint sur 5 est nouveau | tous | `redondance excessive` | 17 / 74 / 444 |

**Retenus :** 2 200 Citiz, 2 338 vélo, 1 059 bus.

Les sites exclus restent dans la table, avec leur motif. **Contraintes physiques non disponibles dans nos données** : foncier, places de stationnement, règles d'urbanisme, accord de la commune. Elles se valident avec Citiz et la collectivité, après le classement.

## 3. Variables (toutes observées, aucune apprise)

| Variable | Calcul sur la zone atteinte | Hypothèse de demande | Utilisée dans le score |
|---|---|---|---|
| `impact` | Population nouvellement couverte par ce type (K6 du site seul) | Plus d'habitants gagnent un accès | ✅ |
| `besoin` | Part de la population sans **aucune** option aujourd'hui | Priorité aux zones sans alternative | ✅ |
| `complementarite_bus` | Part de la population desservie par le bus | L'autopartage complète les transports collectifs | ✅ |
| `logement_collectif` | Part des ménages en logement collectif (`men_coll` / `men`) | Densité, stationnement contraint | ✅ |
| `petits_menages` | Part des ménages d'une personne (`men_1ind` / `men`) | Moins de besoin d'une voiture à soi | ✅ |
| `pop_rayon` | Population atteinte | — | Information |
| `taux_redondance` (K9) | 1 − `pop_nouvelle` / `pop_rayon` | — | Exclusion |
| `niveau_vie_moyen_zone` | `ind_snv` / `ind` | — | Équité (affichage) |

Les trois dernières variables du score sont des **hypothèses de demande** issues du sens commun sur l'autopartage. Elles ne sont validées par aucune donnée d'usage, d'où leurs poids plus faibles.

**Aucune fuite d'information :** aucune variable n'utilise la position des stations Citiz existantes, sauf, par construction, `impact` (un habitant déjà desservi n'est pas nouveau). C'est voulu : le score cherche l'**ajout**, pas l'imitation de l'existant.

## 4. Formule

```text
score(site, type) = 100 × Σ_i  w_i × N(variable_i)        avec Σ w_i = 1
contribution_i     = 100 × w_i × N(variable_i)            (Σ contributions = score)
```

## 5. Normalisation

**Rang centile** parmi les sites retenus du même type : `N(x)` = part des candidats qui font moins bien ou aussi bien.

- La note se lit simplement : « meilleur que 90 % des sites ».
- Elle est robuste aux valeurs extrêmes : un site exceptionnel n'écrase pas les autres, contrairement au min-max.
- Elle est comparable entre variables qui n'ont pas la même unité (habitants, parts).

Limite : deux sites très proches en valeur peuvent avoir des rangs éloignés si beaucoup de sites se tiennent. La sensibilité (section 6) le mesure.

## 6. Pondérations et sensibilité

| Variable | Poids | Justification |
|---|---:|---|
| `impact` | **0,40** | C'est la décision elle-même : maximiser la population nouvellement couverte |
| `besoin` | 0,20 | Équité : priorité aux habitants sans alternative |
| `complementarite_bus` | 0,15 | Hypothèse de demande |
| `logement_collectif` | 0,15 | Hypothèse de demande |
| `petits_menages` | 0,10 | Hypothèse de demande, la plus faible |

**Deux analyses de sensibilité :**

1. **Un facteur à la fois :** chaque poids × 0,5 puis × 1,5 (puis renormalisation). On mesure le Spearman avec le classement de référence, et le recouvrement du top 20.
   - Citiz : **Spearman ≥ 0,978** (le classement global est stable), **recouvrement du top 20 ≥ 35 %** (la composition exacte du top est sensible, car les scores de tête sont serrés, de 79,9 à 81,0).
2. **Tirages aléatoires :** 500 jeux de poids tirés autour des valeurs initiales (loi de Dirichlet, concentration 20, graine 2026). `frequence_top_n` = part des tirages où le site est dans le top 20. C'est la **robustesse** du site.

**Lecture :** il faut présenter des **zones prioritaires** (sites robustes, fréquence élevée) plutôt qu'un site au mètre près.

## 7. Garde-fous d'équité

1. **Commune prioritaire :** couverture actuelle tous modes < 60 % (K2 par commune).
2. **Quota :** le top 20 « équité » (`rang_equite`) réserve au moins **30 %** des places aux meilleurs sites des communes prioritaires.
   - Constaté pour Citiz : **0** site en commune prioritaire dans le top 20 brut, **6** avec le quota.
3. **Le score n'est pas modifié :** l'équité agit sur la sélection, et l'écart entre les deux classements est montré. Le décideur voit le prix de l'équité.
4. **Stigmatisation :** vocabulaire « potentiel d'amélioration », jamais « quartier mal desservi » ; aucun classement de quartiers nommés.
5. **Vie privée :** une zone atteinte agrège plusieurs carreaux ; la population est arrondie à l'affichage ; aucun carreau imputé n'est présenté comme une observation.

## 8. Tables Gold

`gold/candidates/candidats_larochelle` : GeoParquet EPSG:2154, clé (`candidat_id`, `type_equipement`), 7 641 lignes (2 547 sites × 3 types).

| Groupe | Colonnes |
|---|---|
| Site | `candidat_id`, `type_equipement`, `node_id`, `cell_id_origine`, `commune_insee`, `geometry`, `lon_wgs84`, `lat_wgs84` |
| Exclusion | `dans_epci`, `acces_voiture`, `retenu`, `motif_exclusion` |
| Variables brutes | `pop_rayon`, `pop_nouvelle`, `taux_redondance`, `impact`, `besoin`, `complementarite_bus`, `logement_collectif`, `petits_menages`, `niveau_vie_moyen_zone`, `n_carreaux_zone` |
| Score | `n_<variable>` (normalisée), `contribution_<variable>`, `score` |
| Classement | `rang`, `rang_commune`, `frequence_top_n`, `commune_prioritaire`, `rang_equite` |
| Audit | `run_id` |

Également :

- `gold/candidates/paires_candidat_cellule_larochelle` : clé (`candidat_id`, `cell_id`), avec les distances. **C'est la base de K6 marginal pour l'optimisation.**
- `gold/candidates/sensibilite_ponderations_larochelle` : clé (`type_equipement`, `variable`, `facteur`), avec `spearman` et `recouvrement_top_n`.

## 9. Classement attendu

Pour chaque type, parmi les sites retenus :

- `rang` : score décroissant, puis `impact`, puis `candidat_id` ;
- `rang_commune` : le meilleur site de chaque commune ;
- `rang_equite` : le top 20 avec quota.

Top Citiz du 21/10 : tous les sites de tête sont dans la commune de La Rochelle, avec des scores de 79,9 à 81,0 et de +889 à +1 609 habitants nouvellement couverts chacun. Ils sont **voisins** : l'optimisation choisira parmi eux sans compter deux fois les mêmes habitants.

## 10. Expliquer le score à un jury non technique

> « Pour chaque endroit où l'on pourrait ouvrir une station, nous donnons une note sur 100. Cette note additionne cinq critères. Le plus important, pour 40 %, est le **nombre d'habitants qui gagneraient un accès à moins de 5 minutes à pied**. Viennent ensuite les habitants qui n'ont **aucune** solution aujourd'hui, la présence du bus, et deux signes de besoin : des logements collectifs et des personnes seules. Chaque critère est noté comme un classement : 100 % signifie « le meilleur de tous les sites ». Ce n'est **pas** une prévision de réservations : Citiz ne nous a pas transmis de données d'usage. C'est une **priorité d'implantation**, et nous montrons sa robustesse. »

**Visuel recommandé :** pour chaque site du top, une barre empilée des 5 contributions. Leur somme est la note, et l'on voit d'un coup d'œil pourquoi un site est bien classé.
