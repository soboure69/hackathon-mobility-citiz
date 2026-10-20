# Suivi des risques

**Statut :** registre initial, colonne Responsable à remplir en équipe.
**Source :** section 10 du [cahier des charges](cahier_des_charges.md).

| ID | Risque | Probabilité | Impact | Mitigation | Responsable |
|---|---|---|---|---|---|
| R1 | Périmètre trop large (France entière) | Élevée | Critique | Un seul territoire, justifié dès le jour 1 | |
| R2 | Jury qui attend un « vrai » modèle prédictif | Élevée | Élevé | H6 : cible proxy, validation croisée spatiale, limites dites franchement | |
| R3 | Confusion entre score et prédiction, ou entre couverture et usage | Moyenne | Élevé | Tableau des distinctions (§5) présent dans les slides et dans Power BI | |
| R4 | Double comptage de population | Élevée | Élevé | Calcul par cellule, jamais par addition de zones de desserte | |
| R5 | Doublons d'arrêts (fichier national non dédupliqué) | Élevée | Moyen | Règle H4, KPI Q3 avant / après | |
| R6 | Fuite d'information dans le modèle (variables dérivées de la cible, découpage aléatoire voisin) | Moyenne | Élevé | Validation croisée par blocs spatiaux ou par ville, exclusion des variables « distance à Citiz » de la cible | |
| R7 | Coûts non sourcés | Élevée | Moyen | Hypothèses explicites, analyse de sensibilité | |
| R8 | Graphe piéton incomplet (ponts, passages) | Moyenne | Moyen | Règles de filtrage documentées, KPI Q7 | |
| R9 | Stigmatisation (« quartier mal desservi ») | Moyenne | Moyen | Vocabulaire neutre (« potentiel d'amélioration »), pas de classement de quartiers nommés | |
| R10 | Vie privée dans les zones très peu peuplées | Faible | Élevé | Respect du secret Filosofi, agrégation, seuil minimal de population affiché | |
| R11 | Biais vers les zones déjà bien desservies (modèle appris sur l'existant) | Élevée | Élevé | Contrainte d'équité dans l'optimisation, scénario « équité » comparé | |
| R12 | Démonstration en direct qui plante | Moyenne | Critique | Tables Gold pré-calculées, plan B (captures et vidéo) | |
| R13 | Manque de temps pour l'intégration entre les 6 membres | Élevée | Élevé | Schéma Gold figé tôt, points de synchronisation | |
