# Checklist finale de livraison et de démonstration

**Statut :** Mission 15, 21/10/2026. La colonne **État** donne ce qui a été constaté dans le dépôt le 21/10/2026 à 12 h 30 (commit `db040e7`) : ✓ fait et prouvé · ✗ manquant · ? à vérifier par l'équipe. À mettre à jour à chaque passage.

**Priorité.** **B** = bloquant (sans lui, la soutenance ou la livraison échoue) · **I** = important (un jury le remarque) · **+** = bonus.

**Responsables** (`repartition_equipe.md`) : M1 porteur·se du projet · M2 données et pipeline · M3 qualité et éthique · M4 accessibilité et territoire · M5 candidats et score · M6 optimisation, application et démo. Projet mené seul : tous les rôles reviennent à la même personne.

## Les 8 actions encore ouvertes, par ordre d'urgence

| # | Action | Prio. | Resp. |
|---|---|---|---|
| 1 | Donner au jury l'accès au dépôt GitHub (public ou invitations) — R22 | B | M1 |
| 2 | Exporter les slides (PDF + PPTX) dans `docs/soutenance/` et les committer | B | M1 |
| 3 | Mettre les vrais prénoms sur les slides et dans `repartition_equipe.md` | B | M1 |
| 4 | Sauvegarder `data/` (Silver, Gold, exports) hors du PC : clé USB + cloud | B | M2 |
| 5 | ~~Mettre à jour le tableau « Statut » du `README.md`~~ fait le 21/10 | I | M2 |
| 6 | ~~Remplir `docs/model_card.md` comme fiche du score K10~~ fait le 21/10 | I | M5 |
| 7 | Remplir la colonne « Code » des compétences UE (`strategie_soutenance.md` § 4) : intitulés du référentiel nécessaires | I | M1 |
| 8 | ~~Ajouter un notebook de démonstration~~ fait le 21/10 (`notebooks/07_hackathon_demo.ipynb`) | I | M2 |

## 1. Dépôt Git

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| G1 | Le jury peut ouvrir le dépôt | Lien testé depuis un navigateur privé, ou invitations acceptées | B | M1 | ? |
| G2 | Rien en attente | `git status` vide ; `git log origin/main..main` vide après `git push` | B | M2 | ✓ |
| G3 | Les trois livrables du sujet sont dans le dépôt : code, slides, liste des sources | `src/`, `scripts/`, `app/` ; `docs/soutenance/*.pdf` ; `docs/registre_des_sources.xlsx` | B | M1 | ✗ slides |
| G4 | Le README dit comment installer, reconstruire et lancer | Sections Installation, Application, Reproduire ; tableau Statut à jour | I | M2 | ✓ |
| G5 | Les tests passent sur une copie propre | `python -m pytest -q` : tout passe | B | M2 | ? |
| G6 | Dépendances figées | `requirements-lock.txt` régénéré après l'ajout de Streamlit, pydeck, altair | I | M2 | ? |
| G7 | Aucun fichier sensible ou lourd versionné | Pas de `.env`, pas de `~$*.xlsx`, pas de Parquet (`.gitignore`) | B | M3 | ✓ |
| G8 | Notebooks présents, comme l'annonce la structure | `notebooks/07_hackathon_demo.ipynb` exécuté sans erreur (relit Gold, contrôles à zéro) | I | M2 | ✓ |
| G9 | `environment.yml` (prévu par la structure) | Fichier présent, ou mention dans le README qu'on utilise `requirements*.txt` | + | M2 | ✗ |
| G10 | Un tag de version pour la soutenance | `git tag v1.0-soutenance` poussé | + | M2 | ✗ |

## 2. Données Bronze

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| BR1 | Chaque source utilisée a son dossier daté et son manifeste | `data/bronze/<famille>/<territoire>/<source>_<date>/_manifest.json` pour S01, S02, S03, S03d, S04, S05, S08 | B | M2 | ✓ |
| BR2 | Les empreintes correspondent aux fichiers | `verifier_manifeste` sans écart (CS-06) | I | M2 | ✓ |
| BR3 | Licence et URL notées pour chaque source | Onglet `sources` du registre : licence, URL, date de consultation | B | M2 | ✓ |
| BR4 | Bronze jamais modifié | Aucun fichier Bronze plus récent que son manifeste | I | M2 | ✓ |
| BR5 | Sources non intégrées assumées | Omphale (S09), S07 et lot H6 marqués « identifiée » ou « vérifiée », cités en limites | I | M3 | ✓ |

## 3. Données Silver

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| SI1 | Contrôles d'exécution passés | CS-01 à CS-12 sans arrêt au dernier `build_silver` | B | M2 | ✓ |
| SI2 | Arrêts dédoublonnés | 981 quais → 534 arrêts ; `dedup_correspondances_S02` | B | M2 | ✓ |
| SI3 | Projection unique | Tables Silver et Gold en EPSG:2154, exports en WGS84 | B | M4 | ✓ |
| SI4 | Rejets et alertes tracés | `data/silver/quality/rejets_*`, `alertes_*` | I | M3 | ✓ |
| SI5 | Périmètre exact | 28 communes de l'EPCI 241700434 (CS-09) | B | M4 | ✓ |

## 4. Données Gold

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| GO1 | Toutes les tables Gold existent avec leur manifeste | `accessibility/`, `candidates/`, `analytics/`, `dashboards/`, `optimization/`, `exports/` | B | M2 | ✓ |
| GO2 | Aucune table produite par du code non commité | Aucun `run_id` finissant par `-modifie` (page 5 de l'application : pas de message rouge) | B | M2 | ? |
| GO3 | Optimisation complète | 12 scénarios dont 3 équité (X-06) | B | M6 | ✓ |
| GO4 | Exports cohérents | `build_exports` : « X-01 à X-07 : ok » | B | M6 | ✓ |
| GO5 | Copie de sauvegarde hors du PC | Archive de `data/silver` et `data/gold` sur clé USB et dans le cloud (les données ne sont pas versionnées) | B | M2 | ✗ |

## 5. Qualité et couverture

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| Q1 | Indicateurs calculés | 52 indicateurs dans `qualite_donnees_larochelle` : 40 ok, 3 alertes, 9 info | B | M3 | ✓ |
| Q2 | Chaque alerte expliquée avec son effet | Slide 5 et `questions_jury.md` C10 | I | M3 | ✓ |
| Q3 | Couverture des données ≠ couverture de mobilité | Les deux familles séparées (`famille`), vocabulaire tenu dans les slides | B | M3 | ✓ |
| Q4 | Jointures mesurées | Taux de rattachement carreaux / offres au réseau ; 1 paire sur 3 016 perdue sans les arêtes trunk (R26) | I | M4 | ✓ |
| Q5 | Fraîcheur affichée | Âge des flux (alerte vélo 126 jours), millésime Filosofi | I | M3 | ✓ |

## 6. KPI

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| K1 | Couverture actuelle à 5 min par mode | Tous modes 77,8 % · bus 76,1 % · vélo 28,5 % · Citiz 9,8 % | B | M4 | ✓ |
| K2 | Population desservie / non desservie | 135 344 / 38 672 (tous modes), sur 174 016 | B | M4 | ✓ |
| K3 | Options par habitant (objectif 1 du sujet) | 2,25 tous modes ; carte au carreau | B | M4 | ✓ |
| K4 | Habitants servis par chaque station (objectif 2) | Tableau de la page 2 de l'application | B | M4 | ✓ |
| K5 | Nouvellement couverts, coût total, coût par habitant | K6, K7, K8 par scénario (page 4) | B | M6 | ✓ |
| K6 | Redondance et équité | Taux de redondance par site ; part des gains en communes prioritaires ; quintiles de revenu | I | M4 | ✓ |
| K7 | Recoupement application / pipeline | Page 5 : « 6 / 6 à zéro » | B | M3 | ✓ |

## 7. Score ou modèle

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| S1 | Score K10 calculé et décomposable | 2 200 sites Citiz, 5 contributions par site (page 3) | B | M5 | ✓ |
| S2 | Pondérations justifiées et affichées | `config/score.yaml`, `docs/score_potentiel.md` | B | M5 | ✓ |
| S3 | Sensibilité testée | Un poids à la fois (×0,5, ×1,5) : Spearman ≥ 0,978, top 20 commun 35 % à 90 % ; 500 tirages : `frequence_top_n` | I | M5 | ✓ |
| S4 | « Score, pas prédiction » partout | Bandeau page 3, slide 7, notes ; aucune occurrence de « prédiction de fréquentation » présentée comme un résultat | B | M5 | ✓ |
| S5 | Fiche du score (model card) | `docs/model_card.md` : cible, variables, validation, limites, absence de fuite | I | M5 | ✓ |
| S6 | Réponse préparée « où est le modèle prédictif ? » | `questions_jury.md` B2 su par M5 et M1 | B | M5 | ✓ |
| S7 | Modèle H6 appris et validé ville par ville | Lot S06a-d ingéré, évaluation par ville | + | M5 | ✗ (limite assumée) |

## 8. Optimisation

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| O1 | Contrôles bloquants passés | « O-T1 à O-T8 : ok » au dernier build | B | M6 | ✓ |
| O2 | Optimum prouvé | `statut_solution` optimal, écart garanti 0,1 % dans `scenarios` | B | M6 | ✓ |
| O3 | Hypothèses de coût sourcées et étiquetées | `docs/registre_couts.md` ; étiquette à côté de chaque coût dans l'application | B | M6 | ✓ |
| O4 | Prix de l'équité chiffré | 3 034 / 4 371 / 4 570 habitants aux 3 budgets | B | M4 | ✓ |
| O5 | Glouton de contrôle | Optimum = glouton dans 8 cas sur 9 | I | M6 | ✓ |
| O6 | Tests | `tests/test_optimisation.py` (piège du glouton, double compte, équité réelle) | I | M6 | ✓ |
| O7 | Optimisation bus et vélo | Même modèle, coûts validés | + | M6 | ✗ (limite assumée) |

## 9. Application Streamlit

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| A1 | Les 5 pages s'ouvrent sans erreur | `pytest tests/test_app.py` ; ouverture manuelle de chaque page | B | M6 | ✓ |
| A2 | Lancement en une commande sur le PC de démo | `python -m streamlit run app/streamlit_app.py` → http://localhost:8501 | B | M6 | ? |
| A3 | Fonctionne sans Internet | Fond de carte désactivé : carreaux, communes et stations restent | B | M6 | ✓ |
| A4 | Chiffres identiques aux slides | Pages 1, 2, 4, 5 comparées aux slides 2, 6, 9, 10 | B | M1 | ? |
| A5 | Date des données visible | Barre latérale « Données Gold au … » | I | M6 | ✓ |
| A6 | Message clair sur combinaison absente | Équité + coût bas → avertissement | I | M6 | ✓ |
| A7 | Accessibilité visuelle | Couleurs Okabe-Ito doublées d'un libellé ; texte lisible au projecteur (zoom 100 à 125 %) | I | M3 | ? |

## 10. Documentation

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| D1 | Registre des sources complet | `docs/registre_des_sources.xlsx` (26 sources, statut, licence) | B | M2 | ✓ |
| D2 | Méthode traçable | `methodologie.md`, `strategie_jointures.md`, `kpi_acces.md`, `score_potentiel.md`, `optimisation.md` | B | M2 | ✓ |
| D3 | Dictionnaire de données à jour | `data_dictionary.md` (tables Gold et exports) | I | M2 | ✓ |
| D4 | Architecture | `architecture_data.md` | I | M2 | ✓ |
| D5 | Registre des risques à jour | `suivi_risques.md` R1 à R29 | I | M3 | ✓ |
| D6 | Fiche du score | voir S5 | I | M5 | ✓ |
| D7 | Documentation de l'application | `docs/application.md` | I | M6 | ✓ |
| D8 | Finale nationale : prototype et documentation de reprise | README « Reproduire » (ordre des 12 étapes) | + | M2 | ✓ |

## 11. Slides

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| SL1 | Support complet | 12 slides + 2 annexes, titres-réponses | B | M1 | ✓ |
| SL2 | Prénoms réels | Slide 1 et notes sans « [Membre n] » | B | M1 | ✗ |
| SL3 | Export dans le dépôt | `docs/soutenance/soutenance.pdf` (+ `.pptx`) committés | B | M1 | ✗ |
| SL4 | Copie hors ligne | PDF sur clé USB et sur le PC de démo | B | M1 | ✗ |
| SL5 | Partagé avec l'équipe | Chaque membre ouvre le support et lit ses notes | I | M1 | ? |
| SL6 | Sources en bas de chaque slide chiffrée | Pied de page « Source : … » | I | M3 | ✓ |
| SL7 | Lisible au fond de la salle | Aucun texte sous 24 px ; test sur le projecteur | I | M1 | ? |

## 12. Démonstration

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| DE1 | Parcours répété | 5 répétitions du parcours de 75 s sans hésitation (`strategie_soutenance.md` § 5) | B | M6 | ? |
| DE2 | Vidéo de secours lisible hors ligne | `reports/demo/demo_application.mp4` ouvert sur le PC de démo | B | M6 | ✓ |
| DE3 | Bascule vers la vidéo en moins de 10 s | Répétée 2 fois | I | M6 | ? |
| DE4 | Vidéo avec fond de carte | `scripts/enregistrer_demo.py` relancé sur un PC connecté | + | M6 | ✗ |
| DE5 | Aucune action risquée en direct | Pas de build, pas de notebook, pas de saisie | B | M6 | ✓ (règle) |

## 13. Soutenance

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| SO1 | Temps tenu | 10 min ±15 s chronométrées ×2 ; version 5 min ×3 | B | M1 | ? |
| SO2 | Chacun peut expliquer toute la démarche | Fil rouge en 3 phrases dit par chaque membre sans support | B | Tous | ? |
| SO3 | Questions préparées par responsable | `questions_jury.md` réparti selon `repartition_equipe.md` ; 15 tirées au hasard en 45 s | B | Tous | ? |
| SO4 | Preuves des compétences UE | Tableau § 4 de `strategie_soutenance.md`, colonne « Code » remplie | I | M1 | ✗ |
| SO5 | Répétition devant un non-technicien | Il répète la recommandation en sortant | I | M1 | ? |
| SO6 | Répétition devant un profil data | Liste des failles trouvées, chacune avec une réponse | I | M5 | ? |

## 14. Éthique, limites et réglementation

| # | Vérifier | Preuve attendue | Prio. | Resp. | État |
|---|---|---|---|---|---|
| E1 | Aucune donnée personnelle | Population INSEE agrégée à 200 m ; aucune donnée individuelle d'usage | B | M3 | ✓ |
| E2 | Secret statistique respecté et dit | 42 % des carreaux (6 % des habitants) imputés par l'INSEE ; jamais présentés comme observations individuelles | B | M3 | ✓ |
| E3 | Vocabulaire non stigmatisant | « communes prioritaires », jamais « mal desservies » (slides, application, notes) | B | M3 | ✓ |
| E4 | Équité chiffrée, non tranchée | Variante équité et son prix ; la décision reste aux élus | B | M4 | ✓ |
| E5 | Licences respectées | Licence Ouverte 2.0, ODbL (OSM) : attribution dans les slides et le README | I | M3 | ? |
| E6 | Limites dites sans les cacher | Slide 11 ; page 5 ; `strategie_soutenance.md` § 6 | B | M3 | ✓ |
| E7 | Carbone : pas de chiffre inventé | Réponse A6 prête | I | M3 | ✓ |
| E8 | Accessibilité PMR des stations non mesurée, et dit | Limite listée page 5 | I | M3 | ✓ |
| E9 | Aucune charte ni logo Citiz imité sans accord | Slides neutres | I | M1 | ✓ |

## Erreurs éliminatoires

| Erreur | Pourquoi c'est éliminatoire | Parade |
|---|---|---|
| Présenter le score comme une prédiction de fréquentation | Faute de rigueur ; contredit l'absence de données d'usage | « Score de potentiel, classement », dans toutes les bouches |
| Additionner des habitants touchés par plusieurs stations | Double comptage : tout l'impact devient faux | Ne citer que K6 (compté une fois) |
| Une démo qui ne démarre pas, sans plan B | Le sujet exige une démo en direct sur données réelles | Vidéo ouverte en pause dans un onglet |
| Des chiffres différents entre slides, application et oral | Le jury ne croit plus aucun chiffre | Vérification A4 la veille ; une seule source : l'application |
| Un dépôt inaccessible ou sans slides ni registre des sources | Livrables du sujet manquants | G1, G3 |
| Un membre incapable d'expliquer la démarche d'ensemble | Exigence explicite du sujet | SO2 |
| Présenter 85 000 € comme le budget de la collectivité, ou 8 500 € comme un devis | Hypothèse cachée | Toujours « budget de simulation », « coût estimé » |
| Inventer un chiffre en réponse (carbone, usage, devis) | Perte de crédibilité immédiate | « Je ne sais pas ; voici comment je le vérifierais » |
| Relancer le pipeline ou un build pendant la soutenance | Risque de panne en direct | Tout est construit la veille |

## Plan de secours

| Panne | Signe | Action immédiate (moins de 30 s) | Préparé à l'avance |
|---|---|---|---|
| L'application ne répond pas | Page blanche ou spinner au-delà de 5 s | Phrase : « Je vous montre la même chose en vidéo, sur les mêmes données. » Onglet vidéo, lecture | `demo_application.mp4` ouvert en pause |
| Une page de l'application plante | Message d'erreur rouge | Passer à la page suivante du parcours ; la montrer en vidéo | Parcours qui n'impose aucun ordre strict |
| Pas d'Internet | Carte sans fond | Désactiver « Fond de carte » : la carte reste lisible | Testé (A3) |
| Exports absents ou corrompus | « Aucun export trouvé » | Avant la séance seulement : `python scripts/build_exports.py --territoire larochelle` (≈ 15 s, n'utilise que Gold) | Sauvegarde GO5 |
| Application et vidéo indisponibles | — | Montrer `reports/figures/carte_couverture_tous_modes.png` et `courbe_budget_impact.png`, puis les slides | Figures produites par le notebook 07 |
| Gold ou Silver perdu | Build qui échoue | Ne pas reconstruire sur place : restaurer l'archive de `data/` depuis la clé USB ou le cloud | Archive GO5 (`Compress-Archive data\silver, data\gold -DestinationPath sauvegarde_data.zip`) |
| PC de démo en panne | Pas d'écran | Second PC : slides PDF + vidéo depuis la clé USB ; démo en vidéo intégrale | Clé USB : PDF, PPTX, MP4, archive `data/` |
| Projecteur incompatible | Pas d'image | Adaptateur de rechange ; sinon démo sur l'écran du PC tourné vers le jury | Adaptateurs HDMI et USB-C |
| Question sur un chiffre absent des slides | — | Ouvrir l'application à la bonne page, ou l'annexe A | Annexes A et B |

## Les dix dernières minutes

| Minute | Action | Resp. |
|---|---|---|
| −10 | PC branché au secteur et au projecteur ; résolution vérifiée ; notifications et mises à jour coupées | M6 |
| −9 | Application lancée ; les 5 pages ouvertes une fois ; retour à la page 1 | M6 |
| −8 | Wi-Fi testé : sans Internet fiable, « Fond de carte » désactivé | M6 |
| −7 | Onglet vidéo `demo_application.mp4` ouvert, en pause à 0:00 | M6 |
| −6 | Slides en plein écran sur la slide 1, notes visibles sur l'écran du présentateur ; PDF prêt en secours | M1 |
| −5 | Navigateur à 100 à 125 %, barre latérale de l'application repliée | M6 |
| −4 | Chaque membre relit ses deux premières phrases et sa phrase de relais | Tous |
| −3 | Ordre de passage et places debout confirmés ; minuteur visible confié à un membre | M1 |
| −2 | Eau, téléphone en silencieux, clé USB en poche | Tous |
| −1 | Le fil rouge dit à voix basse : question, réponse, arbitrage | Tous |
