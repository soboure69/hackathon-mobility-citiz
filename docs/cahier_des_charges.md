# Cahier des charges — cadrage fonctionnel

**Statut :** brouillon, en attente de validation par l'équipe.
**Points à trancher en priorité :** H1 (territoire), H5 (historique d'usage), H6 (cible proxy du modèle), H7 (coûts unitaires).

> **Écart à trancher avant de continuer.** Le sujet officiel (PDF v0.4.0) exige *« estimates […] the value of a new station […] using a predictive model »* et *« a rigorously evaluated model »*. Les consignes de projet disent au contraire : sans historique d'usage, on parle d'un score multicritère et non d'une prédiction. Position proposée, qui tient les deux (voir H6) : la **valeur principale** est calculée de façon déterministe (population nouvellement couverte), et un **modèle prédictif de potentiel** est entraîné sur une **cible proxy observable** (présence ou taille des stations Citiz existantes dans d'autres villes). Ce modèle est présenté honnêtement comme une prédiction de potentiel d'implantation, pas de fréquentation. C'est à valider avec l'équipe et, si possible, avec les encadrants.

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
| O3 : Proposer où investir (modèle de valeur, coût par équipement, liste priorisée sous budget) | **Décision (cœur du projet)** | Candidats → valeur → coût → optimisation |

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
| **Équipe projet (6 pers.)** | Producteurs | Un cadre commun, des rôles clairs | Ce cahier des charges |

---

## 3. Décision finale à soutenir

> **Pour le territoire T et un budget B, quel portefeuille d'implantations (emplacement × type d'équipement) financer en priorité pour maximiser la population nouvellement couverte à 5 minutes à pied, en évitant la redondance avec l'offre existante et en respectant un plancher d'équité territoriale ?**

| Composante | Détail |
|---|---|
| Entrée décideur | Territoire T, budget B, types d'équipement autorisés, poids éventuel de l'équité |
| Sortie | Liste ordonnée d'emplacements avec type, coût estimé, population nouvellement couverte, coût par habitant, score de potentiel, justification |
| Format | Carte et tableau dans Power BI, avec export CSV |
| Statut de la sortie | **Recommandation d'aide à la décision**, pas une décision automatique : Citiz garde la main (foncier, voirie, partenariats locaux) |

---

## 4. Décisions secondaires

| # | Décision secondaire | Qui décide | Indicateur d'appui |
|---|---|---|---|
| D1 | Quel territoire étudier en priorité ? | Équipe (justification jury) | Disponibilité des données, présence Citiz, taille faisable |
| D2 | Quel type d'équipement à chaque endroit : Citiz, arrêt de bus ou station vélo ? | Citiz / AOM | Coût par habitant nouvellement couvert, par type |
| D3 | Quel niveau de budget retenir ? | Financeur | Courbe impact / budget (rendements décroissants) |
| D4 | Quel arbitrage entre efficacité et équité ? | Collectivité | Écart entre le scénario « max population » et le scénario « équité » |
| D5 | Quelles zones sous-desservies traiter d'abord ? | AOM | Population non desservie, densité, revenus |
| D6 | Si Citiz est absent du territoire : faut-il entrer, et par où ? | Citiz | Stations d'amorçage, potentiel prédit |
| D7 | Quelles zones écarter par prudence (fiabilité faible, petits effectifs) ? | Équipe | KPI qualité, seuil de population |

---

## 5. KPI métier principaux

Unité spatiale de référence : **cellule INSEE 200 m** (à valider, H3). « Option » = une station ou un arrêt distinct (H4).

**Règle de comptage :** une cellule est comptée **une seule fois** dans la population du territoire (K3, K4, K6). On n'additionne jamais les zones de desserte des stations entre elles.

| ID | KPI | Définition | Formule (principe) | Usage |
|---|---|---|---|---|
| K1 | **Options accessibles par habitant** (carte O1) | Nombre de stations ou arrêts distincts atteignables en ≤ 5 min de marche sur réseau piéton depuis la cellule | `n_options(cellule)` ; variante : options pour 1 000 hab. | Carte chaude / froide |
| K2 | **Taux de couverture à 5 min** | Part de la population ayant au moins 1 option à ≤ 5 min | `Σ pop(cellules avec n≥1) / Σ pop totale` | Executive |
| K3 | **Population desservie** | Population des cellules avec n ≥ 1, chaque cellule comptée **une seule fois** | `Σ pop(n≥1)` | Executive |
| K4 | **Population non desservie** | Complément de K3 | `Σ pop(n=0)` | Diagnostic |
| K5 | **Population desservie par station** (O2) | Population des cellules à ≤ 5 min de la station. **Non exclusive** : la somme de toutes les stations dépasse la population totale | `Σ pop(zone 5 min de la station)` | Carte O2 |
| K6 | **Population nouvellement couverte** | Population des cellules passant de n=0 à n≥1 grâce au scénario (par mode et tous modes) | `Σ pop(avant=0 ET après≥1)` | Valeur des candidats |
| K7 | **Coût total du scénario** | Somme des coûts estimés des équipements retenus | `Σ coût(type)` | Budget |
| K8 | **Coût par habitant nouvellement couvert** | Efficacité du scénario | `K7 / K6` | Comparaison |
| K9 | **Taux de redondance** | Part de la population de la zone du candidat déjà couverte par le même mode | `pop déjà couverte / pop zone du candidat` | Anti-doublon |
| K10 | **Score de potentiel** | Indice 0–100 combinant population, besoin, complémentarité et facteurs de demande (motorisation, revenus, emplois…) | Somme pondérée et normalisée (pondérations documentées) | Classement |
| K11 | **Potentiel prédit** | Sortie du modèle sur la cible proxy (H6) | Probabilité ou valeur prédite | Exigence « predictive model » |
| K12 | **Équité territoriale** | Couverture et population nouvellement couverte par classe de densité et par quintile de revenu | Ratio couverture (classe la plus faible / moyenne) | Défense éthique |
| K13 | **CO₂ évité (ordre de grandeur)** | Estimation fondée sur des hypothèses sourcées de report modal | `pop touchée × taux d'adoption × gain CO₂` (toutes hypothèses citées) | Éthique et sociétal |

**Distinctions à toujours afficher :**

| À ne pas confondre | avec |
|---|---|
| Couverture **des données** (avons-nous la donnée ?) | Couverture **de mobilité** (les habitants ont-ils une option ?) |
| Population **totale couverte** (K3) | Population **nouvellement couverte** (K6) |
| **Score** de potentiel (K10, construit) | **Prédiction** (K11, modèle évalué sur une cible proxy) |
| Potentiel d'implantation | Fréquentation réelle (non mesurable sans historique) |
| Population d'une station (K5, avec recouvrements) | Population du territoire (sans double comptage) |

---

## 6. KPI de qualité des données

| ID | KPI | Définition | Exemple d'application | Seuil indicatif (à valider) |
|---|---|---|---|---|
| Q1 | Complétude | % de champs obligatoires renseignés | GTFS `stop_lat/lon`, GBFS `capacity` | ≥ 95 % sur les champs clés |
| Q2 | Validité | % d'enregistrements conformes (coordonnées dans l'emprise, géométrie valide, format conforme) | Arrêts hors du territoire, géométries invalides | ≥ 98 % |
| Q3 | Taux de doublons | % d'arrêts ou stations en double avant / après dédoublonnage | Le fichier national des arrêts **n'est pas dédupliqué** (selon le sujet) | Mesuré et documenté |
| Q4 | Taux de jointure | % d'objets correctement rattachés (cellule → commune/IRIS, arrêt → nœud du graphe piéton avec distance de rattachement < seuil) | Distance arrêt → nœud OSM | ≥ 95 % |
| Q5 | Fraîcheur | Âge de la donnée vs date d'analyse | GTFS `feed_info`, GBFS `last_updated`, millésime Filosofi | Date affichée pour chaque source |
| Q6 | Couverture des sources | % des réseaux présents sur T qui ont un flux trouvé et ingéré ; % du territoire couvert par la grille | Réseaux TC, opérateurs vélo, Citiz | Liste exhaustive des manques |
| Q7 | Connexité du graphe piéton | % de nœuds dans la composante principale | Résultats Lyon 2e : 1 composante après R1 | ≥ 99 % |
| Q8 | Cellules sous secret statistique | % de population ou de cellules avec valeurs imputées ou masquées (Filosofi) | Petits effectifs | Mesuré et affiché |

---

## 7. Périmètre MVP réaliste (2,5 jours)

| Bloc | Inclus dans le MVP | Niveau de rigueur |
|---|---|---|
| Territoire | **Un seul territoire** de taille intermédiaire (piste : une métropole où Citiz est présent, **à confirmer**, voir H1) | Choix justifié |
| Sources | GTFS des réseaux de T, GBFS (Citiz et vélos) de T, Filosofi 200 m, Admin Express, OSM piéton ; Omphale en indicateur de tendance | Registre des sources complet |
| Bronze / Silver / Gold | Les 3 couches avec traçabilité (URL, date, licence, empreinte) | Obligatoire |
| Accessibilité | 5 min de marche sur **réseau piéton réel** (graphe OSMnx), depuis le centroïde de chaque cellule | Cœur méthodologique |
| O1 | Carte des options accessibles par cellule | Obligatoire |
| O2 | Arrêts et stations par type, avec population desservie (K5) | Obligatoire |
| Candidats | Points candidats générés sur le réseau (ex. centroïdes de cellules peuplées non couvertes, ramenés au réseau) | Simple et défendable |
| Valeur | K6 déterministe + score K10 + modèle K11 sur cible proxy, avec validation croisée **spatiale** | Exigence du sujet |
| Coûts | Un coût unitaire par type (Citiz, arrêt de bus, station vélo), **hypothèses sourcées ou présentées comme hypothèses** | Explicite |
| Optimisation | Couverture maximale sous budget (glouton ou PLNE `pulp`), sans double comptage | Obligatoire |
| Scénarios | 3 budgets × 2 variantes (efficacité / équité) | Recommandé |
| Restitution | Power BI 5 pages, démonstration en direct, slides, registre des sources sur le dépôt | Obligatoire |

**Extensions si le temps le permet :** plusieurs territoires, isochrones multi-seuils (5/10 min), projections Omphale intégrées au score, analyse de sensibilité des pondérations, publication dans Fabric.

---

## 8. Hors périmètre (explicitement)

| Hors périmètre | Raison |
|---|---|
| Prédiction de **fréquentation** réelle (nombre de locations) | Aucun historique d'usage Citiz disponible (à confirmer, H5) |
| Étude de faisabilité foncière ou de voirie (places de stationnement, autorisations) | Données non disponibles ; relève de Citiz et des collectivités |
| Business plan complet et rentabilité d'une station | Hors données ouvertes |
| Couverture de toute la France à la cellule 200 m sur réseau piéton | Infaisable en 2,5 jours ; on justifie un territoire |
| Données individuelles ou traces de déplacement | RGPD, non nécessaires |
| Horaires, fréquences et temps d'attente TC dans K1 (MVP) | Extension possible ; le MVP compte la présence d'une option |
| Disponibilité en temps réel des véhicules GBFS | Instantané ponctuel, non représentatif |
| Industrialisation (CI/CD, orchestration de production) | Hors temps du hackathon |

---

## 9. Hypothèses à valider

| ID | Hypothèse | Statut | Comment la valider | Qui |
|---|---|---|---|---|
| H1 | Territoire d'étude = **[à décider]** (Lyon 2e reste une zone test, trop petite pour un arbitrage budgétaire) | À valider | Vérifier la présence d'un flux GBFS Citiz et de flux GTFS sur T | Équipe |
| H2 | 5 min de marche = **≈ 400 m** (≈ 4,8 km/h) sur réseau piéton | Hypothèse | Citer une source de vitesse de marche, tester 300/500 m en sensibilité | Mission 5 |
| H3 | Unité d'analyse = cellule INSEE 200 m, origine = centroïde | Hypothèse | Vérifier le millésime Filosofi et le secret statistique sur T | Équipe |
| H4 | Une option = un arrêt ou une station distincts après dédoublonnage (les arrêts proches d'une même zone d'arrêt comptent pour 1) | À valider | Règle de fusion GTFS `parent_station` ou par distance | Équipe |
| H5 | Aucun historique d'usage Citiz disponible | **À confirmer** au kick-off ou auprès de Citiz | Demander directement | Chef d'équipe |
| H6 | Cible proxy du modèle = présence (ou capacité) d'une station Citiz dans une cellule, apprise sur des villes où Citiz est implanté | À valider | Vérifier le nombre de stations Citiz disponibles en GBFS (assez d'exemples ?) | Équipe data |
| H7 | Coûts unitaires par type d'équipement | **Inconnus** | Sources publiques à trouver, ou fourchettes présentées comme hypothèses ; demander à Citiz | Équipe |
| H8 | Population actuelle (Filosofi) comme base ; Omphale seulement au niveau département ou région, donc utilisé comme tendance | Hypothèse | Vérifier la granularité Omphale | Équipe |
| H9 | Outil : Fabric (suggéré) et/ou Python local + Power BI | À valider | Accès Fabric communiqué au kick-off | Équipe |

---

## 10. Risques majeurs

Le registre détaillé, avec la colonne Responsable à remplir en équipe, est dans [`suivi_risques.md`](suivi_risques.md).

| ID | Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Périmètre trop large (France entière) | Élevée | Critique | Un seul territoire, justifié dès le jour 1 |
| R2 | Jury qui attend un « vrai » modèle prédictif | Élevée | Élevé | H6 : cible proxy, validation croisée spatiale, limites dites franchement |
| R3 | Confusion entre score et prédiction, ou entre couverture et usage | Moyenne | Élevé | Tableau des distinctions (§5) présent dans les slides et dans Power BI |
| R4 | Double comptage de population | Élevée | Élevé | Calcul par cellule, jamais par addition de zones de desserte |
| R5 | Doublons d'arrêts (fichier national non dédupliqué) | Élevée | Moyen | Règle H4, KPI Q3 avant / après |
| R6 | Fuite d'information dans le modèle (variables dérivées de la cible, découpage aléatoire voisin) | Moyenne | Élevé | Validation croisée par blocs spatiaux ou par ville, exclusion des variables « distance à Citiz » de la cible |
| R7 | Coûts non sourcés | Élevée | Moyen | Hypothèses explicites, analyse de sensibilité |
| R8 | Graphe piéton incomplet (ponts, passages) | Moyenne | Moyen | Règles de filtrage documentées, KPI Q7 |
| R9 | Stigmatisation (« quartier mal desservi ») | Moyenne | Moyen | Vocabulaire neutre (« potentiel d'amélioration »), pas de classement de quartiers nommés |
| R10 | Vie privée dans les zones très peu peuplées | Faible | Élevé | Respect du secret Filosofi, agrégation, seuil minimal de population affiché |
| R11 | Biais vers les zones déjà bien desservies (modèle appris sur l'existant) | Élevée | Élevé | Contrainte d'équité dans l'optimisation, scénario « équité » comparé |
| R12 | Démonstration en direct qui plante | Moyenne | Critique | Tables Gold pré-calculées, plan B (captures et vidéo) |
| R13 | Manque de temps pour l'intégration entre les 6 membres | Élevée | Élevé | Schéma Gold figé tôt, points de synchronisation |

---

## 11. Critères d'acceptation de la solution finale

| # | Critère | Vérifiable par |
|---|---|---|
| A1 | Le territoire est choisi et son choix est justifié par écrit | `cahier_des_charges.md` + slide |
| A2 | Chaque source est listée avec URL, date, licence et empreinte de fichier | `registre_des_sources.xlsx` |
| A3 | Les couches `data/bronze`, `data/silver` et `data/gold` sont alimentées et le pipeline est rejouable de bout en bout | Exécution des notebooks 00 → 06 |
| A4 | Les KPI qualité Q1–Q8 sont calculés et affichés | Page 5 de Power BI |
| A5 | La carte O1 (options par cellule, du froid au chaud) fonctionne sur données réelles | Page 2 |
| A6 | La carte O2 affiche chaque arrêt ou station avec son type et sa population desservie | Page 2 |
| A7 | La somme de la population desservie ne dépasse jamais la population du territoire | Test automatique |
| A8 | Chaque candidat a K6, K9, K10, K11 et un coût | Table Gold des candidats |
| A9 | Le modèle est évalué (métrique et validation croisée spatiale) et ses limites sont documentées | `model_card.md` |
| A10 | Le scénario optimal respecte le budget et ses hypothèses sont affichées | Page 4 |
| A11 | Au moins 2 scénarios sont comparés (efficacité / équité) | Page 4 |
| A12 | Les enjeux éthiques (CO₂, équité, stigmatisation, vie privée) sont traités | Page 5 + slide |
| A13 | Démonstration en direct en moins de 5 min, avec plan B | Répétition |
| A14 | Chaque membre peut expliquer l'approche globale et sa partie | Répétition croisée |
| A15 | Code, slides et liste des sources sont sur le dépôt Git | Livrables officiels |

---

## Questions ouvertes avant la mission 2

1. **Territoire :** lequel l'équipe retient-elle ? Un flux GBFS Citiz existe-t-il pour ce territoire sur transport.data.gouv.fr ?
2. **Historique d'usage :** Citiz a-t-il fourni (ou promis) des données d'usage au kick-off ? Sinon, l'équipe valide-t-elle la cible proxy (H6) ?
3. **Coûts :** des ordres de grandeur (station Citiz, arrêt de bus, station vélo) ont-ils été reçus, ou faut-il les sourcer publiquement ?
4. **Outils :** l'équipe travaille-t-elle dans Fabric, en Python local, ou les deux ?
5. **Rôles :** qui porte quelles missions parmi les 6 membres ?
