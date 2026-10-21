# Fiche du score de potentiel (K10)

**Statut :** 21/10/2026. Fiche du score **K10**, livré et utilisé. Le modèle appris **H6**, prévu à l'étape E8, n'est **pas livré** (§ 9). Sources : `docs/score_potentiel.md`, `config/score.yaml`, `src/scoring/candidats.py`, tables `gold/candidates/`.

## 1. Identité

| Champ | Valeur |
|---|---|
| Nom | Score de potentiel territorial K10 (Citiz, vélo, bus) |
| Nature | **Note de priorité multicritère**, construite à partir de données observées. Ce n'est **pas** un modèle appris ni une prédiction |
| Sortie | Note de 0 à 100 par site candidat et par type d'équipement, décomposée en 5 contributions |
| Version | Calcul du 21/10/2026, paramètres de `config/score.yaml` |
| Territoire | CA de La Rochelle (EPCI 241700434) |

## 2. Usage

| Prévu | Non prévu |
|---|---|
| Classer des sites candidats et expliquer pourquoi un site est bien placé | Prévoir des locations, des réservations ou un chiffre d'affaires |
| Départager deux portefeuilles qui couvrent autant d'habitants (terme ε de l'optimisation) | Choisir seul les stations : c'est l'optimisation, sur des habitants comptés une fois, qui choisit |
| Repérer des zones prioritaires (sites robustes, `frequence_top_n` élevée) | Placer une station au mètre près, ou comparer des notes entre territoires différents |

## 3. Données

| Donnée | Source (registre) | Rôle |
|---|---|---|
| Population et ménages par carreau de 200 m (Filosofi 2021) | S03, S03d | Habitants atteints, logement collectif, petits ménages |
| Réseau piéton OpenStreetMap | S05 | Zone atteinte à 400 m de marche, accès voiture |
| Offre existante : bus (GTFS Yélo), Citiz, vélos (GBFS) | S02, S01, S08 | Habitants déjà desservis, besoin, complémentarité bus |
| Communes et EPCI (Admin Express) | S04 | Périmètre, communes prioritaires |

Unité : 2 547 sites (nœuds du réseau rattachés à au moins un carreau peuplé). Après exclusion (hors EPCI, pas d'accès voiture, aucun habitant nouveau, redondance > 80 %) : **2 200 sites Citiz**, 2 338 vélo, 1 059 bus.

## 4. Cible

**Aucune.** Aucune donnée d'usage (locations, réservations) n'est publique pour ce territoire (hypothèse H5). Le score n'est donc entraîné sur rien et n'a pas de précision mesurable : c'est un choix assumé, pour ne pas fabriquer une cible.

## 5. Variables et poids

| Variable | Calcul sur la zone atteinte (≤ 400 m) | Poids |
|---|---|---:|
| `impact` | Habitants nouvellement couverts par ce type, site seul | 0,40 |
| `besoin` | Part des habitants sans aucune option aujourd'hui | 0,20 |
| `complementarite_bus` | Part des habitants desservis par le bus | 0,15 |
| `logement_collectif` | Part des ménages en logement collectif | 0,15 |
| `petits_menages` | Part des ménages d'une personne | 0,10 |

Normalisation : rang centile parmi les sites retenus du même type. `score = 100 × Σ poids × rang centile` ; la somme des 5 contributions est la note.

Les trois dernières variables sont des **hypothèses de demande** (sens commun sur l'autopartage), non validées par des données d'usage, d'où leurs poids plus faibles.

## 6. Évaluation

Sans vérité terrain, on évalue la **stabilité** et la **lisibilité**, pas une précision.

| Test | Méthode | Résultat (Citiz) |
|---|---|---|
| Sensibilité, un poids à la fois | Chaque poids × 0,5 puis × 1,5, renormalisation, 10 variantes | Spearman avec le classement de référence **≥ 0,978** ; top 20 commun **35 % à 90 %** |
| Robustesse par tirages | 500 jeux de poids (Dirichlet, concentration 20, graine 2026) | `frequence_top_n` : part des tirages où un site reste dans le top 20 ; le meilleur site : 69 % |
| Écart en tête | Scores du top 20 | 79,4 à 81,0 sur 100 : la tête est serrée |
| Lisibilité | 5 contributions par site | Affichées page 3 de l'application |

Lecture : l'ordre d'ensemble est stable ; la composition exacte du top 20 ne l'est pas. Le score sert donc à **départager**, et la sélection est faite par l'optimisation (`docs/optimisation.md`).

## 7. Fuite d'information

- Aucune variable n'utilise une donnée de résultat (il n'en existe pas).
- Aucune variable n'utilise les stations Citiz existantes, sauf `impact` **par construction** : un habitant déjà desservi par Citiz n'est pas « nouveau ». C'est voulu : le score cherche l'**ajout**, pas l'imitation de l'existant.
- Les variables sont calculées sur l'état actuel, sans regarder les sites choisis par l'optimisation.

## 8. Limites et éthique

| Limite ou enjeu | Traitement |
|---|---|
| Pas de prédiction d'usage | Dit sur la page 3, la slide 7 et dans les réponses au jury |
| Pondérations choisies, pas apprises | Affichées, justifiées, testées (§ 6) |
| Contraintes physiques absentes (foncier, stationnement, accord de la commune) | À valider avec Citiz et la collectivité après le classement |
| Tête du classement concentrée à La Rochelle | Quota d'équité sur le top 20 (`rang_equite`) et variante équité de l'optimisation |
| Stigmatisation | Vocabulaire « communes prioritaires », aucun classement de quartiers nommés |
| Vie privée | Zones atteintes = plusieurs carreaux agrégés ; carreaux imputés par l'INSEE jamais présentés comme observations |

## 9. Modèle H6 (non livré)

| Élément | Conception |
|---|---|
| Cible proxy | Présence d'une station Citiz dans le carreau, dans des villes où Citiz est implanté |
| Données | Lot 2 : Citiz Angers, Grand Poitiers, Nantes, Rennes (S06a à S06d, vérifiées) et arrêts nationaux (S07) |
| Variables | Celles du § 5 sans `impact` ; aucune variable dérivée des stations Citiz |
| Validation | Une ville laissée de côté à chaque fois (`h6_evaluation`) |
| Statut | **Non livré** : lot 2 non ingéré dans le temps du hackathon. Première extension proposée |

Même livré, H6 apprendrait **où Citiz s'est implanté**, pas **où les stations sont utilisées** : ce serait encore un score de potentiel. Seul un test terrain avec des indicateurs d'usage (slide 12, décision 3) permettrait un vrai modèle de fréquentation.

## 10. Maintenance

Recalcul : `python scripts/build_candidats.py --territoire larochelle`. Paramètres : `config/score.yaml`. Tout changement de poids se refait avec la sensibilité et se documente ici.
