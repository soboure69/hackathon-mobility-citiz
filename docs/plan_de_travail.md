# Plan de travail

**Outils :** Python en local. Notebooks pour le récit, scripts pour les transformations rejouables. Parquet et GeoParquet pour les couches. CSV ou Parquet pour Power BI. Power BI est la restitution, pas l'atelier de données.

On ne démarre pas l'étape suivante tant que le point de validation de l'étape en cours n'est pas coché.

| Étape | Contenu | Point de validation | Dans le MVP |
|---|---|---|---|
| E0 | Cadrage : problème, H6, coûts, outils, critères | Ce dossier `docs/` relu | Fait |
| E1 | Choisir le territoire avec la grille | Décision écrite : CA de La Rochelle, 87,5/100 | Fait. Structure `data/` vide créée ; aucun fichier de données. |
| E2 | Registre des sources du territoire retenu | Registre validé ; V-a et V-b faits avec empreinte ; empreinte des autres sources à E3 | Oui |
| E3 | Bronze : dépôt brut, sans nettoyage | Les fichiers bruts sont relisibles et cités | Oui |
| E4 | Silver : dédoublonnage, qualité Q1–Q8 | Les KPI qualité sont calculés | Oui |
| E5 | Accessibilité 5 min sur le réseau piéton | Une cellule, une fois, depuis son centroïde | Oui |
| E6 | O1 et O2 | Carte des options et population par station (K5) | Oui |
| E7 | Candidats, K6, coûts étiquetés, un scénario glouton | Budget respecté, pas de double comptage, étiquette de coût visible | Oui |
| E8 | Score de potentiel H6 et son évaluation | `model_card.md` : métrique, validation spatiale, phrase « pas une fréquentation » | Oui, après E7 |
| E9 | Budgets et variante équité | Au moins deux scénarios comparés | Si E8 tient |
| E10 | Exports, Power BI, pitch, slides | Démonstration de moins de 5 min et plan B | Oui, sur les tables déjà prêtes |

Si le temps manque après E7, E8 reste dû sous une forme minimale (cible proxy, une métrique, une validation par ville ou par bloc, limites écrites). On ne le remplace pas par un chiffre de fréquentation. E9 peut se réduire à deux scénarios. Les extensions restent fermées : plusieurs territoires, isochrones 10 min, Omphale dans le score, sensibilité complète des pondérations, Fabric, industrialisation.

---

## Structure du dépôt

La structure est décrite dans la section « Structure » de `README.md`.

Pas d'`environment.yml` : `requirements.txt` + `requirements-lock.txt` font foi.

---

## Livrables

| Livrable | Moment |
|---|---|
| `docs/cahier_des_charges.md` | E0 |
| `docs/selection_territoire.md` avec décision écrite | E1 |
| `docs/strategie_couts.md` puis registre chiffré étiqueté | E0 pour la méthode, E7 pour les montants |
| `docs/suivi_risques.md` | tenu à chaque étape |
| `docs/jury_pitch.md` | E10, crochets remplis avec les résultats réels |
| Registre des sources | E2 |
| Couches bronze, silver, gold | E3 à E7 |
| `model_card.md` | E8 |
| Exports Power BI dans `data/gold/exports/` et démonstration | E10 |
| Slides et dépôt Git | E10 |
