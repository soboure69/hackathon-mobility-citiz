# Suivi des risques

**Statut :** mis à jour après les décisions du 20 octobre 2026.
**Source :** [cahier des charges](cahier_des_charges.md).

| ID | Risque | Probabilité | Impact | Mitigation | Responsable |
|---|---|---|---|---|---|
| R1 | Périmètre trop large (France, région, jeu Citiz multi-villes traité en bloc) | Élevée | Critique | Porte G2 de la grille territoire. Un EPCI ou une métropole. | Porteur |
| R2 | Le score H6 est compris comme une prédiction de fréquentation | Élevée | Élevé | H6 est un score de potentiel territorial. Model card, slides et Power BI le disent. Aucun nombre de locations n'est affiché. | Porteur |
| R3 | Confusion entre score construit (K10), score de potentiel (K11) et couverture réelle | Moyenne | Élevé | Tableau des distinctions du cahier, repris dans Power BI | Porteur |
| R4 | Double comptage de population | Élevée | Élevé | Calcul par cellule. Test A7. | Porteur |
| R5 | Doublons d'arrêts dans le fichier national | Élevée | Moyen | Règle H4, KPI Q3 avant et après | Porteur |
| R6 | Fuite d'information dans le modèle proxy (variable tirée de la cible, cellules voisines dans le même pli) | Moyenne | Élevé | Validation par ville ou par bloc spatial. Pas de variable « distance à Citiz » pour prédire la présence Citiz. | Porteur |
| R7 | Un coût hypothétique présenté comme un fait | Élevée | Élevé | Trois étiquettes obligatoires : coût documenté, estimation publique, hypothèse de simulation. Voir `strategie_couts.md`. | Porteur |
| R8 | Graphe piéton incomplet | Moyenne | Moyen | Règles de filtrage documentées, KPI Q7 | Porteur |
| R9 | Stigmatisation (« quartier mal desservi ») | Moyenne | Moyen | Vocabulaire « potentiel d'amélioration ». Pas de classement de quartiers nommés. | Porteur |
| R10 | Vie privée dans les zones très peu peuplées | Faible | Élevé | Secret statistique Filosofi, agrégation, seuil minimal affiché | Porteur |
| R11 | Le modèle, appris sur l'existant, favorise les zones déjà équipées | Élevée | Élevé | K6 reste la valeur principale. Scénario d'équité comparé au scénario d'efficacité. | Porteur |
| R12 | Démonstration en direct qui plante | Moyenne | Critique | Tables gold précalculées, exports déjà ouverts, captures de secours | Porteur |
| R13 | Surcharge de travail et étape bloquante | Élevée | Élevé | Plan séquentiel. On ne saute pas une porte de validation. Extensions fermées si E7 n'est pas tenu. | Porteur |
| R14 | Travail géospatial lancé avant validation du territoire | Élevée | Critique | E1 bloque E2. Dossiers `data/` non créés tant que la décision n'est pas écrite. | Porteur |
| R15 | `station_status` utilisé comme mesure de l'offre | Moyenne | Moyen | L'offre structurelle vient de `station_information` et des arrêts GTFS. Le temps réel reste hors MVP. | Porteur |
| R16 | Métropole dont le graphe piéton ne tient pas en local | Moyenne | Élevé | Porte G5. Si elle échoue, prendre le candidat suivant, plus petit. | Porteur |
| R17 | Effectif Citiz faible sur le territoire retenu (24 stations), donc modèle H6 fragile | Élevée | Élevé | Option A retenue le 20/10/2026 : apprentissage multi-territoires, validation par ville. | Porteur |
| R18 | Offre vélo Yélo disponible seulement en export figé du 17/06/2026 (137 stations) | Certaine | Moyen | Utiliser uniquement les positions des stations comme offre structurelle, ignorer les disponibilités, afficher la date dans Q5 (fraîcheur) et dans Power BI, chercher une autre source publique à E2 sans supposer qu'elle existe. | Porteur |
| R19 | Archive GTFS Yélo non encore ouverte : arrêts sans coordonnées ou réseau incomplet feraient passer S3 à 0 | Moyenne | Élevé | Vérification V-a à E2. Si échec, bascule vers Nantes Métropole (`selection_territoire.md`, §8). | Porteur |
| R20 | Territoire de taille moyenne : un impact en valeur absolue plus faible qu'une grande métropole | Certaine | Moyen | Présenter aussi des ratios (coût par habitant, % de couverture), pas seulement des volumes. | Porteur |
