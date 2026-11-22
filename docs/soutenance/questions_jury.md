# Questions difficiles du jury et réponses

**Statut :** Mission 14, 21/10/2026. Chaque réponse tient en 30 à 45 secondes : **phrase-réponse d'abord**, puis la preuve, puis (si utile) la limite. Le document ou la page de l'application à montrer est indiqué en fin de ligne.

## A. Décideurs et DG Citiz

**A1. Concrètement, qu'est-ce que Citiz gagne avec votre outil ?**
Une liste ordonnée de stations, avec pour chacune les habitants gagnés et le coût par habitant. Pour La Rochelle : 10 stations, 85 000 € sur 3 ans, couverture doublée. Et une méthode rejouable sur les autres villes du réseau, avec les mêmes données ouvertes. *(Page 1, page 4.)*

**A2. Pourquoi ces 10 stations sont-elles toutes à La Rochelle ?**
Parce que c'est là que vivent le plus d'habitants à moins de 400 m d'un site possible et pas encore couverts. C'est le choix le plus efficace. Si vous voulez des stations ailleurs, la variante équité en place 6 sur 10 dans cinq communes prioritaires, et nous en donnons le prix exact : 4 371 habitants de moins. *(Page 4, bouton Équité.)*

**A3. 85 000 €, c'est le vrai budget ?**
Non : c'est un budget de simulation, affiché comme tel. Nous en montrons trois (42 500, 85 000 et 170 000 €) et trois coûts par station. Avec votre budget réel, le résultat se recalcule en quelques secondes. *(Page 4, segments.)*

**A4. D'où vient le coût de 8 500 € par station ?**
D'une convention publique entre une collectivité et Citiz : 4 000 € HT de boîtier par voiture, plus un forfait de garantie de 250 € TTC par mois au maximum. Sur 3 ans, le coût va de 4 000 € (forfait nul) à 13 000 € (forfait plein). 8 500 € est le milieu, une hypothèse. Un devis de Citiz la remplacerait. *(`docs/registre_couts.md`.)*

**A5. Combien de personnes vont réellement utiliser ces stations ?**
Nous ne le savons pas, et nous ne le prétendons pas : aucun historique de locations n'est public. Nous mesurons combien d'habitants auront une station à 5 minutes à pied. C'est la condition de l'usage, pas l'usage. D'où notre troisième recommandation : tester trois stations un an pour mesurer. *(Slide 8.)*

**A6. Quel impact carbone ?**
Nous ne l'avons pas chiffré, volontairement. Il faudrait un taux de report de la voiture personnelle vers l'autopartage, que nous n'avons pas pour ce territoire. Publier un chiffre en inventant ce taux serait trompeur. Le test terrain d'un an fournirait cette donnée.

**A7. Qualifier des communes de « prioritaires », n'est-ce pas les stigmatiser ?**
C'est pour cela que nous ne disons jamais « mal desservies ». Le critère est factuel et affiché : moins de 60 % des habitants ont une option à 5 minutes. Et il sert à leur attribuer des stations, pas à les classer. Le seuil est une hypothèse de travail, réglable.

**A8. Pourquoi ne pas mettre des stations là où il n'y a rien du tout ?**
Le modèle peut le faire : c'est ce que fait la variante équité, qui atteint 2 006 habitants sans aucune option, contre 168 pour la variante efficace. Mais une station Citiz dans une zone très peu dense couvre peu d'habitants : c'est un arbitrage, et il est chiffré.

**A9. Combien de temps pour l'appliquer à une autre ville ?**
La méthode et le code ne changent pas : on change le territoire dans la configuration et on télécharge ses données ouvertes (GTFS, GBFS, carroyage, OpenStreetMap). Le temps dépend surtout de la qualité des données locales, que nos contrôles mesurent à chaque étape.

## B. Jury académique

**B1. Pourquoi La Rochelle et pas une métropole ?**
Nous avons appliqué une grille à sept agglomérations : des critères éliminatoires (flux Citiz ouvert, GTFS publié, carroyage disponible, intérêt métier), puis une note. Lyon (trop peuplée) et le Pays Basque (trop étendu) sont écartés d'office. Nantes et Rennes ont la meilleure note (90), La Rochelle 87,5. La règle, écrite avant la notation : à moins de 5 points du meilleur, on retient le plus compact. La Rochelle (327 km²) l'emporte sur Nantes (523 km²) : tout se calcule sur le réseau piéton réel dans le temps du hackathon, et ses 24 stations Citiz sont toutes dans l'agglomération. Nantes reste le territoire de secours. *(`docs/selection_territoire.md`.)*

**B2. Le sujet demande un modèle prédictif. Où est-il ?**
Nous avons fait un choix assumé : sans cible observée, un modèle « prédictif » d'usage serait une fiction. Nous avons séparé ce qui est mesuré (la couverture, qui décide) de ce qui est estimé (un score de potentiel, qui départage). Un modèle appris, H6, est conçu : il apprend où Citiz est déjà implanté dans cinq villes et se valide en laissant une ville de côté à chaque fois. Les données de quatre villes sont vérifiées ; le modèle n'est pas livré. C'est notre première extension. *(`docs/score_potentiel.md`, `docs/data_dictionary.md`.)*

**B3. Comment savez-vous que votre score est bon ?**
Sans vérité terrain, on ne peut pas mesurer une précision. Nous avons donc vérifié trois choses : il est décomposable (chaque point vient d'un critère visible) ; il est stable (chaque poids divisé ou multiplié par 1,5 : l'ordre global ne bouge presque pas, Spearman ≥ 0,978 ; 500 tirages de poids donnent la robustesse de chaque site) ; et il ne décide pas seul (l'optimisation choisit sur les habitants comptés). Le haut du classement est serré, et nous le disons. *(Page 3, tableau de sensibilité.)*

**B4. Pourquoi Python en local et pas Microsoft Fabric ?**
Projet mené seul en deux jours et demi : nous avons privilégié la reproductibilité (Git, tests, scripts rejouables) et un travail possible hors ligne. L'architecture Bronze / Silver / Gold en Parquet est exactement celle d'un lakehouse Fabric : le passage serait un portage, pas une refonte.

**B5. Et Streamlit plutôt que Power BI ?**
Trois raisons : les cartes affichent les vrais carreaux de 200 m sans service externe ; la logique est en Python testé, pas dans des mesures non testées ; l'application tourne sans licence. Les exports restent lisibles par Power BI, et la conception Power BI complète est dans le dépôt. *(`powerbi/`, `docs/application.md`.)*

**B6. Comment garantissez-vous la reproductibilité ?**
Les données brutes ne sont jamais modifiées et portent leur empreinte SHA-256. Chaque table produite porte un identifiant d'exécution : la date et le commit Git, avec la mention « modifié » si le code n'était pas commité. Des tests automatiques couvrent le double comptage, le budget, les jointures et chaque page de l'application. *(Page 5.)*

**B7. Quels enjeux éthiques et réglementaires ?**
Quatre. Vie privée : aucune donnée personnelle ; la population est agrégée par carreaux de 200 m, et l'INSEE impute les carreaux de moins de 11 ménages (42 % des carreaux, 6 % des habitants). Équité : variante chiffrée. Stigmatisation : vocabulaire neutre. Accessibilité : couleurs lisibles par les daltoniens, toujours doublées d'un libellé ; l'accessibilité des stations aux personnes à mobilité réduite n'est pas mesurée, et nous le disons.

**B8. Qu'auriez-vous fait avec plus de temps ?**
Dans l'ordre : le modèle H6 validé ville par ville ; l'optimisation multi-équipements (bus, vélo, Citiz) avec des coûts validés ; les projections Omphale pour un scénario 2030 ; une analyse de sensibilité des seuils d'équité (60 % et 30 %).

## C. Profils data

**C1. Comment évitez-vous le double comptage ?**
Tout est calculé au carreau. Un carreau est « nouvellement couvert » s'il n'est pas desservi aujourd'hui et qu'au moins une station choisie l'atteint ; il compte une fois, quel que soit le nombre de stations. Trois contrôles le vérifient à chaque exécution : la somme des gains marginaux égale le total, aucun carreau n'apparaît deux fois, et la somme des carreaux gagnés égale le total affiché. *(Page 5, recoupements.)*

**C2. Les arrêts de bus sont-ils dédoublonnés ?**
Oui. Le GTFS de Yélo contient 981 quais rattachés à 534 arrêts. Une option est un arrêt, pas un quai : sinon un arrêt à deux quais compterait double dans le nombre d'options par habitant. *(`docs/methodologie.md`.)*

**C3. Pourquoi 400 m pour 5 minutes ?**
4,8 km/h, une vitesse de marche courante, donne 400 m en 5 minutes. La distance est mesurée sur le réseau piéton OpenStreetMap : accès du carreau au réseau, trajet, accès à la station, le tout sous 400 m. C'est un paramètre de configuration.

**C4. Formulez votre optimisation.**
Couverture maximale sous budget (Church et ReVelle, 1974). Variables binaires x_i (ouvrir le site i) et y_j (carreau j couvert). On maximise Σ pop_j · y_j, sous y_j ≤ Σ x_i sur les sites qui atteignent j, et Σ coût_i · x_i ≤ B. Un terme ε · score départage les solutions de même population, avec ε choisi pour ne jamais valoir un habitant. Résolu par PuLP / CBC. *(Annexe A1, `docs/optimisation.md`.)*

**C5. « Optimum prouvé », vraiment ?**
Oui, à 0,1 % près : nous lisons le statut de la solution renvoyé par le solveur, pas seulement son message. Nous avions constaté que PuLP affiche « Optimal » même quand CBC s'arrête sur sa limite de temps ; le script s'arrête désormais si la preuve manque. Une inégalité valide (pas plus de ⌊B / coût minimal⌋ stations) a ramené le cas le plus lent de plus de 120 s à 0,3 s, sans changer la solution.

**C6. Un glouton aurait suffi, non ?**
Presque : le problème est sous-modulaire, et le glouton a une garantie théorique d'environ 63 % de l'optimum (1 − 1/e). En pratique, il trouve l'optimum dans 8 scénarios sur 9. La méthode exacte apporte la preuve, et fait mieux dans le neuvième (49 284 habitants contre 49 108).

**C7. Comment la contrainte d'équité est-elle écrite ?**
Σ pop_j · y_j sur les carreaux prioritaires ≥ 30 % de Σ pop_j · y_j. Piège évité : sans contrainte supplémentaire, le solveur pourrait laisser des carreaux couverts hors des communes prioritaires à y_j < 1 pour gonfler la part. Nous imposons y_j ≥ x_i pour chaque couple site-carreau, et un contrôle recalcule la part réelle.

**C8. Y a-t-il une fuite d'information dans votre score ?**
Le score n'utilise aucune donnée d'usage ni de résultat : il n'y en a pas. Ses critères sont calculés sur l'état actuel (population, offre existante à la même date), sans regarder les sites choisis par l'optimisation. Pour le futur modèle H6, la cible est la présence de Citiz ; aucune variable n'est dérivée des stations Citiz, et la validation laisse une ville entière de côté.

**C9. Pourquoi une normalisation par rang centile ?**
Les critères ont des échelles et des queues très différentes (des habitants, des parts). Le rang centile les rend comparables et insensibles aux valeurs extrêmes. Contrepartie : on perd l'écart absolu entre deux sites, ce qui est acceptable pour un score qui ne fait que départager.

**C10. Les données sont-elles à jour ?**
Chaque source a sa date dans le registre. Le flux vélo Yélo a 126 jours : c'est une alerte affichée. Le carroyage Filosofi est le millésime 2021. Les KPI sont donc une photographie à ces dates, pas un état en temps réel.

**C11. Quelle est la sensibilité aux coûts ?**
Le coût par station est le même pour tous les sites : il ne change pas l'ordre des sites, seulement le nombre de stations financées. À 85 000 €, on passe de 6 stations (13 000 €) à 21 stations (4 000 €), soit de 12 888 à 30 834 habitants. *(Page 4.)*

**C12. Que se passe-t-il pour un carreau à cheval sur deux communes ?**
Il est rattaché à une seule commune, celle qui en contient la plus grande part, pour qu'aucun habitant ne soit compté deux fois dans les totaux communaux. Ces carreaux sont signalés (`multi_commune`) dans les tables.

## D. Questions pièges (garder son calme)

| Question | Réponse courte |
|---|---|
| « Votre score, c'est arbitraire. » | « Les pondérations sont un choix, affiché et testé : chaque poids varié de ±50 %, plus 500 tirages aléatoires. Et le score ne décide pas : l'optimisation décide sur des habitants comptés. » |
| « Vous n'avez fait qu'un seul type de station. » | « Un type fait jusqu'au bout, contrôlé et prouvé, plutôt que trois à moitié. Le code est paramétré par type. » |
| « Ce n'est pas de l'IA. » | « C'est de l'aide à la décision : de la donnée, de la géographie et de l'optimisation exacte. Nous avons refusé d'appeler “prédiction” ce qui n'en est pas une. » |
| « Pourquoi vous croire ? » | « Ne nous croyez pas : tout est dans le dépôt, rejouable, et la page 5 montre les contrôles à zéro. » |
| Question dont on ne connaît pas la réponse | « Je ne sais pas, et je ne veux pas inventer. Voici comment je le vérifierais : … » |
