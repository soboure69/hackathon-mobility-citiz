# Cahier des charges — cadrage fonctionnel

**Statut :** territoire retenu le 20 octobre 2026 : CA de La Rochelle. Le rattachement géométrique des stations reste à confirmer à E3.
**Documents liés :** [sélection du territoire](selection_territoire.md), [plan de travail](plan_de_travail.md), [coûts](strategie_couts.md), [risques](suivi_risques.md), [pitch](jury_pitch.md).

> **H6 est tranché.** Le sujet officiel (PDF v0.4.0) demande d'estimer la valeur d'une nouvelle station avec un modèle prédictif rigoureusement évalué. Citiz n'a fourni aucun historique d'usage, et n'en a pas promis. La valeur principale reste déterministe : la population nouvellement couverte (K6). H6 est un **score de potentiel territorial** servant à prioriser des emplacements. S'il est produit par un modèle, la cible d'apprentissage est une proxy observable (présence ou capacité d'une station Citiz déjà implantée ailleurs). Ce score n'est pas une prédiction de fréquentation.

---

## 1. Problème métier reformulé

| Élément | Formulation |
|---|---|
| **Constat** | L'offre de mobilité (bus, tram, vélos et trottinettes en libre-service, autopartage) se multiplie mais reste très inégalement répartie. On ne sait pas précisément qui a une option à moins de 5 minutes à pied de chez lui. |
| **Problème** | Citiz et les collectivités choisissent leurs nouvelles implantations sans outil objectif qui croise l'offre existante, la population réelle, le réseau piéton et le coût. |
| **Question centrale** | *Pour un territoire et un budget donnés, où implanter de nouvelles stations (Citiz en priorité, puis arrêt de bus ou station vélo) pour toucher le plus d'habitants au moindre coût, sans doublonner l'existant et sans délaisser les territoires peu denses ?* |
| **Valeur attendue** | Passer d'un inventaire de données ouvertes (GTFS, GBFS, INSEE, OSM) à une **liste priorisée et chiffrée d'implantations**, défendable et reproductible. |

**Correspondance avec les 3 objectifs officiels :**

| Objectif du sujet | Rôle | Brique du projet |
|---|---|---|
| O1 : Cartographier l'accès (options accessibles par habitant à 5 min à pied, du froid au chaud) | Diagnostic | Accessibilité sur réseau piéton OSM × grille INSEE 200 m |
| O2 : Montrer qui est concerné (stations et arrêts par type, population desservie par chacun) | Diagnostic | Zone de desserte de chaque station → population |
| O3 : Proposer où investir (modèle de valeur, coût par équipement, liste priorisée sous budget) | **Décision (cœur du projet)** | Candidats → K6 → score H6 → coût étiqueté → optimisation |

---

## 2. Parties prenantes et besoins

| Partie prenante | Rôle | Besoin principal | Ce que la solution doit lui montrer |
|---|---|---|---|
| **Citiz** (partenaire, opérateur) | Décideur d'implantation | Savoir où ouvrir les prochaines stations pour trouver des usagers | Top des emplacements, population touchée, coût, complémentarité avec l'offre existante |
| **Collectivités / AOM** (autorités organisatrices de la mobilité) | Financeurs, aménageurs | Réduire les zones blanches, défendre l'équité territoriale | Couverture actuelle, population non desservie, équité dense / peu dense |
| **Opérateurs TC et vélos partagés** | Opérateurs complémentaires | Savoir où un arrêt ou une station vélo serait plus utile qu'une station Citiz | Comparaison par type d'équipement |
| **Urbanistes et chercheurs** | Utilisateurs experts | Méthode transparente et réutilisable | Sources, hypothèses, code reproductible |
| **Jury (non technique)** | Évaluateur | Un problème concret, une recommandation claire, un impact chiffré | Dashboard simple, 3 chiffres clés, une carte |
| **Jury (data scientist)** | Évaluateur | Choix justifiés, modèle rigoureusement évalué, limites assumées | Validation du modèle, absence de fuite d'information, qualité des données |
| **Habitants** (indirects) | Bénéficiaires | Accès de proximité, pas de stigmatisation, vie privée | Vocabulaire neutre, aucune donnée individuelle |

---

## 3. Décision finale à soutenir

> **Pour le territoire T et un budget B, quel portefeuille d'implantations (emplacement × type d'équipement) financer en priorité pour maximiser la population nouvellement couverte à 5 minutes à pied, en évitant la redondance avec l'offre existante et en respectant un plancher d'équité territoriale ?**

| Composante | Détail |
|---|---|
| Entrée décideur | Territoire T (choisi par la grille, pas encore fixé), budget B, types d'équipement autorisés, poids éventuel de l'équité |
| Sortie | Liste ordonnée d'emplacements avec type, coût estimé et son étiquette, population nouvellement couverte, coût par habitant, score de potentiel territorial, justification |
| Format | Carte et tableau dans Power BI, alimentés par un export CSV ou Parquet. Le calcul est fait en Python. |
| Statut de la sortie | **Recommandation d'aide à la décision**, pas une décision automatique : Citiz garde la main (foncier, voirie, partenariats locaux) |

---

## 4. Décisions secondaires

Le porteur prépare chaque décision et l'écrit. Citiz et les collectivités restent les destinataires de la recommandation.

| # | Décision secondaire | Qui tranche dans le projet | Indicateur d'appui |
|---|---|---|---|
| D1 | Quel territoire étudier ? | Porteur, via la grille | Portes G1–G6 puis score S1–S7. Voir `selection_territoire.md`. |
| D2 | Quel type d'équipement à chaque endroit : Citiz, arrêt de bus ou station vélo ? | Porteur, pour la recommandation | Coût par habitant nouvellement couvert, par type |
| D3 | Quel niveau de budget retenir ? | Porteur, comme scénario | Courbe impact / budget (rendements décroissants) |
| D4 | Quel arbitrage entre efficacité et équité ? | Porteur, deux scénarios montrés | Écart entre « max population » et « équité » |
| D5 | Quelles zones sous-desservies traiter d'abord ? | Porteur | Population non desservie, densité, revenus |
| D6 | Où densifier un réseau Citiz déjà présent ? | Porteur | Stations d'amorçage, score de potentiel territorial |
| D7 | Quelles zones écarter par prudence (fiabilité faible, petits effectifs) ? | Porteur | KPI qualité, seuil de population |

D6 ne porte pas sur un territoire sans Citiz : la porte G1 exige un flux Citiz exploitable.

---

## 5. KPI métier principaux

Unité spatiale de référence : **cellule INSEE 200 m** (hypothèse H3, à confirmer sur le territoire une fois celui-ci choisi). « Option » = une station ou un arrêt distinct (H4).

**Règle de comptage :** une cellule est comptée **une seule fois** dans la population du territoire (K3, K4, K6). On n'additionne jamais les zones de desserte des stations entre elles.

| ID | KPI | Définition | Formule (principe) | Usage |
|---|---|---|---|---|
| K1 | **Options accessibles par habitant** (carte O1) | Nombre de stations ou arrêts distincts atteignables en ≤ 5 min de marche sur réseau piéton depuis la cellule | `n_options(cellule)` ; variante : options pour 1 000 hab. | Carte chaude / froide |
| K2 | **Taux de couverture à 5 min** | Part de la population ayant au moins 1 option à ≤ 5 min | `Σ pop(cellules avec n≥1) / Σ pop totale` | Executive |
| K3 | **Population desservie** | Population des cellules avec n ≥ 1, chaque cellule comptée **une seule fois** | `Σ pop(n≥1)` | Executive |
| K4 | **Population non desservie** | Complément de K3 | `Σ pop(n=0)` | Diagnostic |
| K5 | **Population desservie par station** (O2) | Population des cellules à ≤ 5 min de la station. **Non exclusive** : la somme de toutes les stations peut dépasser la population totale | `Σ pop(zone 5 min de la station)` | Carte O2 |
| K6 | **Population nouvellement couverte** | Population des cellules passant de n=0 à n≥1 grâce au scénario. **Valeur principale de la décision.** | `Σ pop(avant=0 ET après≥1)` | Valeur des candidats |
| K7 | **Coût total du scénario** | Somme des coûts des équipements retenus, chaque poste avec son étiquette | `Σ coût(type)` | Budget |
| K8 | **Coût par habitant nouvellement couvert** | Efficacité du scénario. Hérite de l'étiquette de coût la plus faible des postes utilisés. | `K7 / K6` | Comparaison |
| K9 | **Taux de redondance** | Part de la population de la zone du candidat déjà couverte par le même mode | `pop déjà couverte / pop zone du candidat` | Anti-doublon |
| K10 | **Score construit** | Indice 0–100, somme pondérée documentée (population, besoin, complémentarité, facteurs de demande) | Pondérations écrites avant le calcul | Classement explicable |
| K11 | **Score de potentiel territorial (H6)** | Priorisation des candidats. Si un modèle est utilisé, sa sortie est ce score, appris sur une cible proxy. Ce n'est pas un volume de locations. | Voir la définition H6, section 9 | Exigence « modèle évalué » |
| K12 | **Équité territoriale** | Couverture et population nouvellement couverte par classe de densité et par quintile de revenu | Ratio couverture (classe la plus faible / moyenne) | Défense éthique |
| K13 | **CO₂ évité (ordre de grandeur)** | Estimation fondée sur des hypothèses sourcées de report modal | `pop touchée × taux d'adoption × gain CO₂` (hypothèses citées) | Éthique et sociétal |

**Distinctions à toujours afficher :**

| À ne pas confondre | avec |
|---|---|
| Couverture **des données** (avons-nous la donnée ?) | Couverture **de mobilité** (les habitants ont-ils une option ?) |
| Population **totale couverte** (K3) | Population **nouvellement couverte** (K6) |
| **Score construit** (K10) | **Score de potentiel territorial** (K11 / H6) |
| Potentiel d'implantation | Fréquentation réelle (aucune donnée d'usage) |
| Population d'une station (K5, avec recouvrements) | Population du territoire (sans double comptage) |
| Coût documenté | Estimation publique, ou hypothèse de simulation |

---

## 6. KPI de qualité des données

| ID | KPI | Définition | Exemple d'application | Seuil indicatif (à valider) |
|---|---|---|---|---|
| Q1 | Complétude | % de champs obligatoires renseignés | GTFS `stop_lat/lon`, GBFS `capacity` | ≥ 95 % sur les champs clés |
| Q2 | Validité | % d'enregistrements conformes (coordonnées dans l'emprise, géométrie valide, format conforme) | Arrêts hors du territoire, géométries invalides | ≥ 98 % |
| Q3 | Taux de doublons | % d'arrêts ou stations en double avant / après dédoublonnage | Le fichier national des arrêts n'est pas dédupliqué (selon le sujet) | Mesuré et documenté |
| Q4 | Taux de jointure | % d'objets correctement rattachés (cellule → commune/IRIS, arrêt → nœud du graphe piéton avec distance de rattachement < seuil) | Distance arrêt → nœud OSM | ≥ 95 % |
| Q5 | Fraîcheur | Âge de la donnée vs date d'analyse | GTFS `feed_info`, GBFS `last_updated`, millésime Filosofi | Date affichée pour chaque source |
| Q6 | Couverture des sources | % des réseaux présents sur T qui ont un flux trouvé et ingéré ; % du territoire couvert par la grille | Réseaux TC, opérateurs vélo, Citiz | Liste exhaustive des manques |
| Q7 | Connexité du graphe piéton | % de nœuds dans la composante principale | À mesurer sur le territoire retenu | ≥ 99 % |
| Q8 | Cellules sous secret statistique | % de population ou de cellules avec valeurs imputées ou masquées (Filosofi) | Petits effectifs | Mesuré et affiché |

---

## 7. Périmètre MVP

Un seul territoire, choisi après la grille. Calculs en Python local. Durée visée : 2,5 jours, donc la coupe est stricte.

| Bloc | Inclus dans le MVP | Niveau de rigueur |
|---|---|---|
| Territoire | Un EPCI ou une métropole qui passe G1–G6 | Choix écrit dans `selection_territoire.md` |
| Sources | GTFS du réseau de T, GBFS Citiz de T, GBFS vélo si la porte S4 le permet, Filosofi 200 m, Admin Express, OSM piéton | Registre des sources |
| Bronze / Silver / Gold | Trois couches, traçabilité (URL, date, licence, empreinte), Parquet ou GeoParquet | Obligatoire, après E1 |
| Accessibilité | 5 min de marche sur le réseau piéton, depuis le centroïde de chaque cellule | Cœur méthodologique |
| O1 | Carte des options accessibles par cellule | Obligatoire |
| O2 | Arrêts et stations par type, avec population desservie (K5) | Obligatoire |
| Candidats | Centroïdes de cellules peuplées non couvertes, ramenés au réseau | Simple et défendable |
| Valeur | K6 déterministe, puis score H6 évalué sur la cible proxy | K6 d'abord. H6 ensuite, avec model card. |
| Coûts | Un paramètre par type, étiqueté | Aucun montant sans étiquette |
| Optimisation | Couverture maximale sous budget, glouton, sans double comptage | Obligatoire |
| Scénarios | Au moins efficacité et équité. Trois budgets si le temps le permet. | E9 |
| Restitution | Exports CSV ou Parquet, Power BI, pitch, slides | Obligatoire |

**Hors du temps disponible, donc hors MVP :** plusieurs territoires, isochrones 10 min, Omphale intégré au score, sensibilité complète des pondérations, Microsoft Fabric, orchestration de production.

Le détail des étapes et la coupe si le temps manque sont dans `plan_de_travail.md`.

---

## 8. Hors périmètre

| Hors périmètre | Raison |
|---|---|
| Prédiction de fréquentation (nombre de locations) | Aucun historique d'usage. H5 est confirmée. H6 ne la remplace pas. |
| Faisabilité foncière ou de voirie | Données absentes. Relève de Citiz et des collectivités. |
| Business plan et rentabilité d'une station | Hors données ouvertes |
| France entière, ou une région entière, à la cellule 200 m | Infaisable en local. La grille écarte ces périmètres. |
| Données individuelles ou traces de déplacement | RGPD, non nécessaires |
| Horaires, fréquences et temps d'attente dans K1 | Le MVP compte la présence d'une option |
| Disponibilité temps réel des véhicules GBFS | Instantané. L'offre vient des stations et des arrêts. |
| Fabric, CI/CD, orchestration | Le projet tourne en Python local |

---

## 9. Hypothèses

| ID | Hypothèse | Statut | Comment la confirmer |
|---|---|---|---|
| H1 | Territoire = CA de La Rochelle (241700434), score 92,5. Lyon 2e n'est pas le territoire d'étude. | **Tranchée** par la grille du 20 octobre 2026. Confirmation géométrique à E3 (seuil 80 %). | `selection_territoire.md` |
| H2 | 5 min de marche ≈ 400 m (≈ 4,8 km/h) sur le réseau piéton | Hypothèse de travail | Citer une source de vitesse. Tester 300 m et 500 m seulement après E5. |
| H3 | Unité d'analyse = cellule INSEE 200 m, origine = centroïde | Hypothèse, provisoire tant que H1 est ouverte | Vérifier le millésime Filosofi et le secret statistique sur T |
| H4 | Une option = un arrêt ou une station distincts après dédoublonnage | À préciser au nettoyage | Règle `parent_station` ou distance, écrite avant le calcul |
| H5 | Aucun historique d'usage Citiz | **Confirmée.** Rien n'a été fourni ni promis au kick-off. | Close |
| H6 | Score de potentiel territorial, défini ci-dessous | **Validée dans ce sens.** Pas une fréquentation. | Model card au moment du calcul |
| H7 | Les coûts unitaires sont inconnus | **Confirmée.** Rien reçu de Citiz. | `strategie_couts.md` |
| H8 | La population de référence est le carroyage actuel. Omphale, plus grossier, ne sert pas au MVP. | Hypothèse | Ne pas intégrer Omphale au score dans le MVP |
| H9 | Python local, notebooks, scripts, Parquet / GeoParquet, exports CSV ou Parquet pour Power BI | **Tranchée** | Le plan de travail décrit la séquence |

### Définition de H6

H6 priorise des emplacements candidats. Il ne répond pas à la question « combien de locations cette station ferait-elle ».

| Élément | Contenu |
|---|---|
| Nom affiché | Score de potentiel territorial |
| Question autorisée | Ce lieu ressemble-t-il aux contextes où Citiz a déjà implanté une station, une fois retirée l'information qui est la cible ? |
| Cible proxy | Présence d'une station Citiz dans la cellule, ou capacité de cette station si le champ est assez rempli |
| Où le modèle apprend | Sur des villes déjà équipées, autres que le territoire de décision, ou par blocs spatiaux / par ville |
| Sortie | Un score de priorité, pas un volume |
| Valeur qui décide | K6 reste devant H6. H6 départage ou éclaire. Il ne remplace pas la population nouvellement couverte. |
| Évaluation exigée | Métrique adaptée à la cible, validation croisée spatiale, limites écrites dans `model_card.md` |
| Interdit | Découpage aléatoire de cellules voisines. Variable « distance à une station Citiz » pour prédire la présence d'une station Citiz. Toute phrase du type « X locations prévues ». |

K10 reste le score construit à la main, avec pondérations écrites. K11 est la sortie du modèle proxy. Les deux portent des noms différents dans les tableaux et dans Power BI.

---

## 10. Risques majeurs

Le registre tenu à jour est [`suivi_risques.md`](suivi_risques.md). Les risques ouverts par ce cadrage sont : périmètre trop grand (R1, R16), H6 lu comme une fréquentation (R2), coût hypothétique présenté comme un fait (R7), et démarrage géospatial avant le choix du territoire (R14).

---

## 11. Critères d'acceptation

| # | Critère | Vérifiable par |
|---|---|---|
| A1 | Le territoire est celui de la grille, avec URL, date et raison écrite. Tant que cette ligne est vide, le critère est en échec. | `selection_territoire.md` |
| A2 | Chaque source a une URL, une date, une licence et une empreinte | Registre des sources |
| A3 | Bronze, silver et gold sont rejouables en Python local | Notebooks et scripts, après E1 |
| A4 | Les KPI qualité Q1–Q8 sont calculés | Export ou page Power BI |
| A5 | La carte O1 fonctionne sur les données réelles du territoire retenu | Restitution |
| A6 | La carte O2 affiche chaque arrêt ou station avec son type et sa population desservie | Restitution |
| A7 | La population desservie du territoire ne dépasse pas la population du territoire | Test |
| A8 | Chaque candidat a K6, K9, K10 ou K11 selon l'étape atteinte, et un coût étiqueté | Table gold |
| A9 | H6 est évalué (métrique, validation spatiale) et la model card dit qu'il ne s'agit pas de fréquentation | `model_card.md` |
| A10 | Le scénario respecte le budget. Les hypothèses de coût sont visibles à côté des montants. | Restitution |
| A11 | Au moins deux scénarios sont comparés (efficacité, équité) si E9 est atteint | Restitution |
| A12 | CO₂, équité, stigmatisation et vie privée sont traités | Pitch et restitution |
| A13 | Démonstration en moins de 5 min, avec un plan B sur tables déjà calculées | Répétition |
| A14 | Le porteur peut expliquer l'ensemble de la chaîne, du flux Citiz jusqu'au scénario | Répétition |
| A15 | Code, slides et sources sont sur le dépôt Git | Dépôt |
| A16 | Aucun coût n'est affiché sans l'étiquette coût documenté, estimation publique ou hypothèse de simulation | `strategie_couts.md` et restitution |
| A17 | Aucun chiffre de fréquentation, de locations ou de chiffre d'affaires n'est produit | Pitch, model card, Power BI |
| A18 | Aucun fichier sous `data/` avant la décision. Les preuves de la grille sont des captures dans `docs/annexes/selection_territoire/`. | Dépôt au moment de E1 |

---

## Décisions actées

| Sujet | Décision |
|---|---|
| Territoire | CA de La Rochelle. Grille et preuves dans `selection_territoire.md`. |
| Historique d'usage | Absent. H5 confirmée. |
| H6 | Score de potentiel territorial sur cible proxy. Pas une fréquentation. |
| Coûts | À sourcer publiquement. Sinon, hypothèses paramétrables et étiquetées. |
| Outils | Python local. Exports pour Power BI. |
