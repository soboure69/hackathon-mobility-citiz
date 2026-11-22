# Stratégie de soutenance

**Statut :** Mission 14, 21/10/2026. Tous les chiffres viennent des exports Gold (`data/gold/exports/`, run de l'optimisation `20261021T084710Z_5c8ceff`). Aucun chiffre n'est arrondi au-delà de ce qu'affiche l'application. Documents liés : `narration.md` (texte mot à mot), `questions_jury.md` (questions et réponses), `demo_video.md` (vidéos de démonstration).

**Outil de démonstration :** application Streamlit (`app/`), décision P-1 révisée le 21/10/2026. Partout où le sujet ou la Mission 14 parlent de « démonstration Power BI », lire « démonstration de l'application ».

## 0. Le fil rouge

**Une question, une réponse, un arbitrage.**

> *Question.* Où Citiz et l'agglomération de La Rochelle doivent-elles ouvrir de nouvelles stations d'autopartage ?
>
> *Réponse.* Avec 85 000 € sur 3 ans, 10 stations doublent la part des habitants qui ont Citiz à 5 minutes à pied (9,8 % → 20,6 %), pour 4,52 € par habitant gagné.
>
> *Arbitrage.* Ce choix le plus efficace n'apporte rien aux 9 communes peu desservies. Leur en garantir 30 % coûte 23 % de l'impact, mais touche 12 fois plus d'habitants qui n'avaient aucune option. C'est un choix politique : l'outil le chiffre, il ne le tranche pas.

Trois phrases à pouvoir dire sans support, à tout moment.

### Ce que chaque public doit repartir avec

| Public | Ce qu'il cherche | Ce qu'on lui donne | Moment |
|---|---|---|---|
| DG Citiz | Où ouvrir, combien, pour quel public | Liste ordonnée de 10 stations, coût par habitant, carte | Slides 3, 6, 9 ; démo page 4 |
| Décideurs non techniques (collectivité) | Un choix simple et défendable, l'équité | Un chiffre avant / après, le prix de l'équité en habitants | Slides 2, 7, 9 |
| Jury académique | Les compétences de l'UE, la rigueur, la traçabilité | Pipeline Bronze / Silver / Gold, contrôles, documentation, limites | Slides 4, 8 ; démo page 5 |
| Profils data | Choix justifiés, modèle évalué, pas de fuite | Réseau piéton réel, déduplication, optimum prouvé, glouton de contrôle, sensibilité | Slides 4, 5, 6 ; questions |

### Règles de langage (à tenir du premier au dernier mot)

| Dire | Ne jamais dire |
|---|---|
| « score de potentiel », « classement » | « prédiction », « demande », « fréquentation attendue » |
| « habitants nouvellement couverts » (comptés une fois) | « habitants touchés » additionnés par station |
| « couverture de mobilité » (qui a une option à 5 min) | « couverture » seul, quand on parle de la couverture des données |
| « communes prioritaires » (couverture tous modes < 60 %) | « communes mal desservies », « zones délaissées » (stigmatisant) |
| « budget de simulation », « coût estimé » | « le budget de la collectivité », « le coût d'une station » |
| « optimum prouvé à 0,1 % près » | « la meilleure solution possible » sans condition |

## 1. Pitch de 5 minutes

Objectif : un décideur doit pouvoir répéter la recommandation en sortant. La démo est courte et prévue (60 s) ; le reste passe en questions.

| Temps | Bloc | Slide | Ce qui est dit (résumé) |
|---|---|---|---|
| 0:00 – 0:30 | Accroche | 1 → 2 | Un habitant sur cinq n'a aucune option de mobilité à 5 minutes à pied ; pour Citiz, moins d'un sur dix. |
| 0:30 – 1:00 | Question et périmètre | 3 | Où ouvrir les prochaines stations ? CA de La Rochelle, 28 communes, 174 016 habitants, données ouvertes réelles. |
| 1:00 – 1:45 | Méthode en une image | 4 | 5 sources, réseau piéton réel, carreaux de 200 m, chaque habitant compté une fois, contrôles automatiques. |
| 1:45 – 2:45 | **Démo en direct** | (application) | Page 1 → page 4 : la recommandation, puis le bouton Équité. |
| 2:45 – 3:30 | Recommandation | 6 | 10 stations, +18 816 habitants, 4,52 €/habitant ; rendements décroissants. |
| 3:30 – 4:15 | Arbitrage équité | 7 | −23 % d'impact, mais 0 → 4 674 habitants gagnés en communes prioritaires, et 2 006 sans option au lieu de 168. |
| 4:15 – 4:40 | Limites assumées | 8 | Score, pas prédiction ; coûts en hypothèse ; ce qu'on ferait ensuite. |
| 4:40 – 5:00 | Décision demandée | 9 | Financer le portefeuille de 10 stations, choisir le curseur d'équité, lancer un test sur 3 stations. |

Si la démo en direct échoue : vidéo de secours `reports/demo/demo_application.mp4`, à partir de 0:10 (page 1), puis 2:10 (page 4). Ne pas commenter la panne plus d'une phrase.

## 2. Pitch de 10 minutes

Même fil, avec la preuve méthodologique et une démo complète.

| Temps | Bloc | Slides | Ajouts par rapport au 5 minutes |
|---|---|---|---|
| 0:00 – 0:45 | Accroche, question | 1, 2, 3 | Pourquoi La Rochelle : 7 agglomérations candidates, portes éliminatoires (flux Citiz, GTFS, carroyage, intérêt métier) puis note ; Nantes et Rennes à 90, La Rochelle à 87,5, retenue par la règle écrite d'avance « à moins de 5 points, le plus compact » (327 km² contre 523 pour Nantes) (`docs/selection_territoire.md`). |
| 0:45 – 2:15 | Données et méthode | 4, 5 | Bronze / Silver / Gold ; déduplication des arrêts ; réseau piéton OSM ; contrôles qualité (40 conformes, 3 alertes connues). |
| 2:15 – 3:15 | Diagnostic | 2 (rappel), démo page 2 | Bus 76 %, vélo 29 %, Citiz 9,8 % ; 9 communes prioritaires ; les ménages modestes ne sont pas les moins couverts. |
| 3:15 – 4:15 | Candidats et score | démo page 3 | 2 200 sites ; 5 critères ; sensibilité : ordre stable, haut du classement serré → l'optimisation décide. |
| 4:15 – 6:00 | Optimisation | 6, démo page 4 | Couverture maximale sous budget ; optimum prouvé ; 3 budgets × 3 coûts ; courbe budget → impact ; glouton de contrôle. |
| 6:00 – 7:00 | Équité | 7 | Prix de l'équité aux 3 budgets : 27 %, 23 %, 15 % ; effet sur les habitants sans option. |
| 7:00 – 8:00 | Confiance | 8, démo page 5 | Recoupements à zéro, hypothèses étiquetées, risques ouverts, éthique. |
| 8:00 – 9:00 | Limites et suite | 8, 10 | Pas d'historique d'usage ; modèle H6 conçu, non livré ; bus et vélo ; Omphale ; carbone. |
| 9:00 – 10:00 | Décision | 9 | Trois décisions, un test terrain mesurable. |

## 3. Plan slide par slide

Titre de slide = la réponse (le message clé). Une seule idée par slide. Chiffres en gros, sources en petit en bas de chaque slide.

| N° | Titre (message clé) | Contenu | Preuve / visuel | Public visé |
|---|---|---|---|---|
| 1 | **Où ouvrir les prochaines stations Citiz à La Rochelle ?** | Titre, nom, date, « Hackathon Epitech x Citiz », territoire | Photo ou carte de l'agglomération (capture page 2, sans légende) | Tous |
| 2 | **22 % des habitants n'ont aucune option de mobilité à 5 minutes à pied** | 3 chiffres : tous modes 77,8 % · bus 76,1 % · Citiz 9,8 % ; 38 672 habitants sans option | Capture page 2 (carreaux bleu / vermillon) | Décideurs |
| 3 | **Une question de décision, sur un territoire réel** | CA de La Rochelle, 28 communes, 174 016 habitants ; 24 stations Citiz, 136 stations vélo, 534 arrêts de bus ; décision : quels emplacements financer sous budget | Carte des communes ; encadré « Décision à éclairer » | DG Citiz |
| 4 | **Cinq sources ouvertes croisées, chaque habitant compté une fois** | Schéma Sources → Bronze → Silver → Gold → Application ; réseau piéton OSM (400 m = 5 min) ; carreaux 200 m ; déduplication ; contrôles | Schéma du pipeline (page 5) ; logos de formats (GTFS, GBFS) sans logos de marques | Jury, data |
| 5 | **Des données contrôlées : 40 contrôles conformes, 3 alertes connues et sans effet sur la décision** | Tableau qualité par dimension ; les 3 alertes expliquées ; « recoupements application / pipeline : 6 / 6 à zéro » | Capture page 5 | Jury, data |
| 6 | **10 stations, +18 816 habitants, 4,52 € par habitant** | Couverture Citiz 9,8 % → 20,6 % ; liste des 10 sites ; courbe : 1re station 4 040 habitants, 30e 894 ; optimum prouvé | Capture page 1 (carte + tableau) ; courbe budget → impact | DG Citiz, décideurs |
| 7 | **L'équité a un prix mesurable : −23 % d'impact, ×12 habitants sans option atteints** | Barres efficacité / équité aux 3 budgets ; 10 stations à La Rochelle → 4 à La Rochelle et 6 dans 5 communes prioritaires ; 0 → 4 674 habitants en communes prioritaires ; 168 → 2 006 habitants sans option | Capture page 4 (graphique « prix de l'équité ») | Décideurs, jury (éthique) |
| 8 | **Ce que l'outil dit, et ce qu'il ne dit pas** | 2 colonnes : « Établi » (couverture, coûts relatifs, optimum) / « Hypothèses et limites » (pas de prédiction d'usage, coûts estimés, 5 min sur OSM, carreaux imputés, bus et vélo non optimisés) | Tableau des hypothèses (page 5) avec ● ◐ ○ | Jury, data |
| 9 | **Trois décisions à prendre** | ① Financer le portefeuille de 10 stations (85 000 € sur 3 ans) ② Choisir le curseur d'équité (0 % ou 30 %) ③ Tester 3 stations sur 12 mois avec indicateurs d'usage | Encadré décision ; carte des 10 stations | DG Citiz, décideurs |
| 10 *(10 min, ou annexe)* | **Et ensuite : de la couverture à l'usage** | Modèle H6 (présence Citiz dans 5 villes, validation ville par ville) ; bus et vélo ; Omphale ; bilan carbone ; Fabric | Feuille de route en 3 étapes | Jury, data |
| Annexes | Réponses préparées | A1 formulation mathématique · A2 sensibilité du score · A3 coûts et sources · A4 qualité détaillée · A5 sélection du territoire · A6 RGPD et secret statistique | Tableaux | Questions |

## 4. Preuves par compétence de l'UE

Les intitulés exacts des compétences 7.03.1 à 7.03.5, 7.06.2, 7.06.3, 7.07.1, 7.07.2 et 7.07.4 sont dans le référentiel de l'UE : reporter le code en face de chaque ligne avant la soutenance (colonne « Code »). Les lignes reprennent les huit attendus du cadrage du projet.

| Attendu | Code | Preuve à montrer | Où (dépôt / app) | Quand |
|---|---|---|---|---|
| Consolider des sources ouvertes hétérogènes | | 5 sources de formats différents (GTFS, GBFS, carroyage INSEE, Admin Express, OSM) ; registre des sources ; manifestes SHA-256 | `docs/registre_des_sources.xlsx`, `data/bronze/**/_manifest.json`, `src/ingestion/` | Slide 4 ; page 5 (sources) |
| Mesurer qualité, couverture et limites | | 52 indicateurs (complétude, validité, unicité, jointure, fraîcheur, traçabilité) ; couverture des données ≠ couverture de mobilité | `docs/protocole_qualite.md`, `data/gold/analytics/qualite_donnees_larochelle.parquet` | Slide 5 ; page 5 |
| Construire une analyse d'aide à la décision | | KPI de couverture, score de potentiel décomposé, portefeuille, titres-réponses | `docs/kpi_acces.md`, `docs/score_potentiel.md`, pages 1 à 4 | Slides 2, 6 ; démo |
| Absence de fuite d'information | | Le score n'utilise aucune donnée d'usage ni de résultat ; l'impact d'un site est mesuré contre l'offre existante à la même date ; H6 conçu sans variable dérivée des stations Citiz, validé ville par ville | `docs/score_potentiel.md`, `docs/data_dictionary.md` (h6), `config/score.yaml` | Slide 8 ; question data |
| Optimiser sous contrainte budgétaire | | Couverture maximale sous budget (PuLP / CBC), optimum prouvé, 6 contrôles O-T, glouton de contrôle, 12 scénarios, courbe | `docs/optimisation.md`, `src/optimization/couverture.py`, `tests/test_optimisation.py` | Slides 6, 7 ; page 4 ; annexe A1 |
| Adapter le discours à plusieurs publics | | Titres-réponses, info-bulles, page 5 pour les experts, deux pitchs (5 et 10 min) | `app/`, `docs/soutenance/` | Toute la soutenance |
| Enjeux éthiques, réglementaires, accessibilité | | Variante équité chiffrée ; vocabulaire non stigmatisant ; secret statistique (41,9 % des carreaux imputés, 6,3 % de la population) ; aucune donnée personnelle ; couleurs accessibles | `docs/suivi_risques.md`, `powerbi/conception_rapport.md` § 6, page 5 | Slides 7, 8 |
| Présenter et défendre | | Pitch tenu dans le temps, démo en direct, réponses sourcées | `docs/soutenance/narration.md`, `questions_jury.md` | Soutenance |

Traçabilité transverse à citer une fois : chaque table porte un `run_id` (date UTC + commit Git) ; un run sur du code non commité est marqué `-modifie` ; les tests automatisés (`pytest`) couvrent double comptage, budget, jointures et pages de l'application.

## 5. Démonstration en direct

L'application remplace Power BI (P-1 révisée). Démo **pilotée par la question**, pas par le menu.

### Préparation (la veille et 15 min avant)

1. `python scripts/build_exports.py --territoire larochelle` (contrôles X-01 à X-07 ok) ; vérifier que la barre latérale affiche la bonne date.
2. Lancer `python -m streamlit run app/streamlit_app.py` ; ouvrir les 5 pages une fois (mise en cache).
3. Navigateur en plein écran (F11), zoom 100 %, notifications coupées, barre latérale repliée sauf pour montrer le fond de carte.
4. Tester le Wi-Fi de la salle : sans Internet, désactiver « Fond de carte » dès l'ouverture.
5. Vidéo de secours ouverte dans un second onglet, en pause à 0:00.

### Parcours 5 minutes (60 s)

| Temps | Action | Phrase |
|---|---|---|
| 0 – 15 s | Page 1, pointer les 4 chiffres | « Aujourd'hui 9,8 % ; avec 85 000 €, 10 stations, +18 816 habitants, 4,52 € chacun. » |
| 15 – 30 s | Survoler 2 stations vertes sur la carte | « Les points verts sont les stations proposées, dans l'ordre de leur apport. » |
| 30 – 50 s | Page 4, cliquer **Équité** | « Même budget, contrainte d'équité : 14 446 habitants au lieu de 18 816, mais 4 674 dans les communes prioritaires au lieu de 0. » |
| 50 – 60 s | Revenir sur **Efficacité** | « Le choix vous appartient ; l'outil le chiffre. » |

### Parcours 10 minutes (3 min, en trois passages)

| Passage | Page | Actions | Ce qu'on prouve |
|---|---|---|---|
| Diagnostic (60 s) | 2 | Segment **Citiz** puis **Tous modes** ; tableau « habitants à 5 min de chaque station » | Objectifs 1 et 2 du sujet : carte des options à 5 min, habitants servis par chaque station |
| Score (45 s) | 3 | Cliquer la ligne de rang 2 ; lire la décomposition ; montrer le tableau de sensibilité | Score explicable ; pas de boîte noire ; limites du classement |
| Décision (75 s) | 4 | Budget 42 500 → 170 000 € ; coût 13 000 → 4 000 € ; variante Équité ; montrer le message « équité au coût central seulement » | Optimisation sous budget ; sensibilité aux coûts ; prix de l'équité ; garde-fous |
| Confiance (en questions) | 5 | Recoupements 6 / 6, alertes, hypothèses ● ◐ ○ | Qualité, traçabilité, honnêteté |

**Ne pas faire en direct :** relancer un build, ouvrir un notebook, taper une commande, filtrer une commune au hasard. Tout ce qui n'est pas répété passe en vidéo ou en capture.

## 6. Limites à reconnaître sans fragiliser le projet

Formule : *limite → pourquoi c'est un choix raisonnable → ce que ça change (ou pas) à la décision → ce qu'on ferait ensuite.*

| Limite | Formulation conseillée |
|---|---|
| Pas de modèle prédictif d'usage | « Sans historique de locations, prédire une fréquentation serait inventer une cible. Nous mesurons ce qui est certain, la couverture, et nous classons avec un score transparent. Le modèle H6 (présence de Citiz dans cinq villes, validé ville par ville) est conçu ; il n'est pas livré. La décision repose sur des habitants comptés, pas sur une prédiction. » |
| Coûts et budgets estimés | « Les coûts viennent de sources publiques ou sont des hypothèses étiquetées. Nous montrons trois niveaux : le coût étant le même pour chaque station, l'ordre des sites ne change pas ; c'est le nombre de stations financées qui change. Un devis Citiz remplacerait l'hypothèse en une ligne de configuration. » |
| 5 minutes = 400 m sur OSM | « C'est un réseau piéton réel, pas un cercle à vol d'oiseau. Pentes et traversées ne sont pas modélisées ; la conclusion de proximité tient à quelques dizaines de mètres près. » |
| Citiz seulement optimisé | « Le sujet cite aussi bus et vélo. Les candidats bus et vélo sont déjà scorés ; il manque des coûts validés. Le modèle d'optimisation est le même, paramétré par type. » |
| Pas d'Omphale ni de bilan carbone | « Identifiés dans le registre, non intégrés faute de temps. Le carbone exige un taux de report modal que nous n'avons pas : nous ne publions pas un chiffre inventé. » |
| Alertes qualité (flux vélo Yélo vieux de 126 jours, capacités vélo absentes, 98,3 % du réseau connecté) | « Connues et affichées. Elles portent sur l'offre vélo et sur 1,7 % des nœuds piétons ; la recommandation Citiz n'en dépend pas. » |
| Projet réalisé seul | « Choix de périmètre assumé : un territoire, un type d'équipement, fait jusqu'au bout et contrôlé, plutôt que tout le sujet à moitié. » |

## 7. Conclusion orientée décision (à dire mot pour mot)

> « Nous ne vous demandons pas de croire une prédiction. Nous vous montrons des habitants comptés un par un. Trois décisions : financer les 10 stations du portefeuille, 85 000 € sur 3 ans, pour doubler la couverture Citiz ; choisir le curseur d'équité, et l'outil vous dit exactement ce qu'il coûte ; et tester trois de ces stations pendant un an, pour mesurer enfin l'usage réel et remplacer notre score par un modèle appris. Dès demain, la même méthode s'applique à n'importe quelle agglomération française : il suffit de changer le code du territoire. »

## 8. Répartition de la parole

Le projet est réalisé **seul** : toute la soutenance est portée par une seule voix. Le sujet exige que chaque membre puisse expliquer l'ensemble et répondre en profondeur sur sa partie : seul, cela veut dire maîtriser les 4 blocs ci-dessous.

| Bloc | Slides / pages | Préparation en profondeur |
|---|---|---|
| Problème et décision | 1, 2, 3, 9 | Chiffres de la slide 2 par cœur ; raison du territoire |
| Données et qualité | 4, 5, page 5 | Déduplication, réseau piéton, 3 alertes, secret statistique |
| Score et optimisation | 6, 7, pages 3 et 4 | Formulation (annexe A1), sensibilité, optimum prouvé, glouton |
| Limites et suite | 8, 10 | Réponses du § 6 |

Si une équipe est reconstituée pour la finale (2 à 3 personnes), répartition proposée :

| Personne | Parle | Répond aux questions sur |
|---|---|---|
| A — porteur | Slides 1-3, 9 ; démo page 1 | Décision, Citiz, territoire |
| B — data | Slides 4, 5, 8 ; démo pages 2, 5 | Sources, qualité, réseau piéton, éthique |
| C — modèle | Slides 6, 7 ; démo pages 3, 4 | Score, optimisation, équité |

Passages de relais annoncés par une phrase-pont (« … et c'est là que l'optimisation intervient »), jamais par « je laisse la parole à ».

## 9. Checklist de répétition

### J-2 : contenu

- [ ] Les 9 slides (et l'annexe) existent ; chaque titre est une phrase-réponse.
- [ ] Chaque chiffre des slides est vérifié dans l'application (pages 1, 2, 4, 5).
- [ ] Les intitulés des compétences UE sont reportés dans le tableau § 4.
- [ ] La slide 8 dit « score, pas prédiction » et donne les limites du § 6.
- [ ] Aucun logo ni charte imitant Citiz sans accord ; sources citées en bas de slide.

### J-1 : répétitions chronométrées

- [ ] Pitch 5 min ×3, chronomètre visible ; écart toléré ±15 s.
- [ ] Pitch 10 min ×2.
- [ ] Démo 60 s ×5 sans regarder l'écran plus de 3 s d'affilée.
- [ ] Bascule vers la vidéo de secours ×2 (moins de 10 s).
- [ ] 15 questions de `questions_jury.md` tirées au hasard, réponse en moins de 45 s chacune.
- [ ] Une répétition devant une personne non technique : peut-elle répéter la recommandation ?
- [ ] Une répétition devant un profil data : a-t-il trouvé une faille non couverte ?

### Jour J : matériel

- [ ] Exports reconstruits, application lancée, 5 pages ouvertes une fois.
- [ ] Vidéo `reports/demo/demo_application.mp4` lisible hors ligne ; slides en PDF sur clé USB.
- [ ] Adaptateur HDMI / USB-C, chargeur, résolution testée sur le projecteur.
- [ ] Dépôt Git à jour et accessible au jury (R22) ; README avec la commande de lancement.
- [ ] Eau, montre, fiche des 3 phrases du fil rouge.

### Après chaque répétition

- [ ] Noter les 2 passages les plus lents et les couper.
- [ ] Noter chaque question sans réponse et l'ajouter à `questions_jury.md`.
