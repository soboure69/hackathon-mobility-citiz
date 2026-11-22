# Manuel du projet et guide d'architecture

**Hackathon Epitech x Citiz · « Hackathon Mobility » · CA de La Rochelle**

**Statut :** 21/10/2026, après les Missions 1 à 15. Ce manuel raconte le projet de bout en bout : pourquoi chaque étape existait, ce qu'elle a produit, et comment elle a ouvert la suivante. Les détails vivent dans les documents cités ; ce manuel est la porte d'entrée. Tous les chiffres viennent des tables Gold du dépôt (run de l'optimisation `20261021T084710Z_5c8ceff`).

> **Comment lire ce manuel.** Si vous avez 2 minutes : § 1.2 et § 3.2. Si vous êtes au jury : § 4.1. Si vous décidez pour Citiz ou une collectivité : § 4.2. Si vous reprenez le code : § 3 puis § 4.3.

---

## Sommaire

1. [Introduction et vision globale](#1-introduction-et-vision-globale)
2. [Déroulé mission par mission](#2-déroulé-mission-par-mission)
3. [Synthèse de l'architecture et chaîne de valeur](#3-synthèse-de-larchitecture-et-chaîne-de-valeur)
4. [Bilan et guide de lecture par profil](#4-bilan-et-guide-de-lecture-par-profil)
5. [Glossaire](#5-glossaire)

---

## 1. Introduction et vision globale

### 1.1 Contexte et problématique métier

Citiz est le premier réseau coopératif d'autopartage en France : environ 2 800 voitures partagées dans quelque 280 villes. Comme tout opérateur, il doit choisir **où ouvrir ses prochaines stations** : là où elles toucheront le plus d'habitants, compléteront l'offre existante et trouveront leurs usagers.

Depuis la loi d'orientation des mobilités (LOM), beaucoup de données sont ouvertes : arrêts de bus (format **GTFS**), stations de vélos et d'autopartage (format **GBFS**), population fine de l'INSEE, réseau piéton d'OpenStreetMap. Mais **aucune source ne suffit seule** : l'offre ne dit rien de la population servie, la population ne dit rien de l'offre, et une carte sans réseau piéton surestime l'accès réel.

Le défi est donc de **croiser** ces sources pour répondre à une question simple : *qui a vraiment une option de mobilité près de chez lui, et où faut-il en ajouter ?*

Sur notre territoire, la réponse de départ est nette :

| Constat (CA de La Rochelle, 174 016 habitants) | Valeur |
|---|---:|
| Habitants avec au moins une option à 5 min à pied (bus, Citiz ou vélo) | 77,8 % |
| … avec un arrêt de bus | 76,1 % |
| … avec une station vélo en libre-service | 28,5 % |
| … avec une station **Citiz** | **9,8 %** |
| Habitants sans **aucune** option à 5 min | **38 672** |

### 1.2 Objectif majeur et promesse de la solution

**La décision que le projet permet de prendre :**

> Pour un territoire et un budget donnés, **quelles stations financer en priorité** pour maximiser le nombre d'habitants **nouvellement** à 5 minutes à pied d'une station, chacun compté une seule fois, sans doublonner l'offre existante, et en connaissant le prix de l'équité entre communes.

**La réponse produite pour La Rochelle :**

| Scénario de référence | Valeur |
|---|---|
| Budget | 85 000 € sur 3 ans (budget de simulation) |
| Stations financées | 10 |
| Habitants nouvellement couverts | **+18 816** |
| Coût par habitant gagné | **4,52 €** |
| Couverture Citiz | 9,8 % → **20,6 %** (doublée) |
| Variante équité (30 % des gains en communes prioritaires) | 14 446 habitants (−23 %), mais 4 674 dans les communes prioritaires au lieu de 0, et 2 006 habitants sans aucune option atteints au lieu de 168 |

**La promesse :** une recommandation **chiffrée, traçable et rejouable**, qui distingue toujours ce qui est mesuré, ce qui est estimé et ce qui est une hypothèse. L'outil chiffre les arbitrages ; il ne les tranche pas à la place des décideurs.

**Ce que la solution ne promet pas :** une prévision de fréquentation. Aucun historique de locations n'est public ; le projet le dit, et ne fabrique pas de cible.

### 1.3 Vue d'ensemble du parcours (Missions 1 à 15)

```text
 CADRER            OUTILLER              CONSTRUIRE LA DONNÉE              MESURER            DÉCIDER                 RESTITUER ET DÉFENDRE
┌────────┐   ┌──────────────────┐   ┌──────────────────────────────┐   ┌──────────┐   ┌──────────────────┐   ┌─────────────────────────────┐
│ M1     │   │ M3 Dépôt Git     │   │ M6 Bronze : copie fidèle      │   │ M10 KPI  │   │ M11 Candidats    │   │ M13 Restitution (5 pages)   │
│ Cadrage│──▶│ M4 Registre des  │──▶│ M7 Silver : nettoyage,        │──▶│ d'accès  │──▶│     et score     │──▶│ M14 Soutenance              │
│ M2     │   │    sources       │   │    dédoublonnage              │   │ (qui est │   │ M12 Optimisation │   │ M15 Checklist finale        │
│ Terri- │   │ M5 Architecture  │   │ M8 Jointures spatiales        │   │ desservi)│   │     sous budget  │   │                             │
│ toire  │   │    Bronze/Silver │   │ M9 Qualité et couverture      │   │          │   │     + équité     │   │                             │
└────────┘   │    /Gold         │   └──────────────────────────────┘   └──────────┘   └──────────────────┘   └─────────────────────────────┘
             └──────────────────┘
 Question ──▶ Cadre de travail ──▶ Données fiables et traçables ──▶ Diagnostic ──▶ Recommandation chiffrée ──▶ Décision éclairée
```

Chaque mission produit un livrable qui rend la suivante **possible** (on ne peut pas mesurer sans données propres) et **nécessaire** (une mesure appelle une décision). Les transitions sont détaillées au § 2.

---

## 2. Déroulé mission par mission

### 📌 Mission 1 : Cadrage fonctionnel

**1. Pourquoi cette mission ?**
Un hackathon de deux jours et demi échoue rarement faute de code ; il échoue faute de question claire. Il fallait transformer un sujet large (« cartographier l'accès à la mobilité en France et proposer où investir ») en **une décision mesurable**, avec des indicateurs définis avant tout calcul, et dire dès le départ ce que le projet ne ferait pas.

**2. Ce qui a été réalisé et les choix clés**
- Problème reformulé et relié aux 3 objectifs officiels : O1 cartographier l'accès, O2 montrer qui est concerné, O3 proposer où investir (le cœur).
- Parties prenantes et besoins : Citiz, collectivités, autres opérateurs, urbanistes, jury non technique, jury data, habitants.
- Décision finale et 7 décisions secondaires (territoire, type d'équipement, budget, arbitrage efficacité / équité…).
- KPI métier **K1 à K13** et KPI qualité **Q1 à Q8**, avec la règle d'or : **une cellule de population n'est comptée qu'une fois**.
- Hypothèses H1 à H9 ; la plus structurante, **H5 : aucun historique d'usage Citiz**. D'où le choix de parler de **score de potentiel**, jamais de prédiction de fréquentation.
- Périmètre MVP strict, hors périmètre écrit, 18 critères d'acceptation.

**3. Ce que cela apporte**
Un contrat de travail : `docs/cahier_des_charges.md`. Chaque chiffre produit ensuite a une définition écrite d'avance, ce qui protège contre les erreurs classiques (double comptage, confusion couverture / usage, coût sans source).

**4. Transition**
Les KPI sont définis à la cellule de 200 m et le calcul doit tenir sur un ordinateur portable : impossible à l'échelle de la France. Il fallait donc **choisir un territoire**.

---

### 📌 Mission 2 : Choisir le périmètre

**1. Pourquoi cette mission ?**
Un territoire trop grand rend les calculs sur réseau piéton impossibles en local ; un territoire mal choisi (sans flux Citiz, sans GTFS) rend la démonstration vide. Le choix devait être **défendable** devant un jury, pas une préférence.

**2. Ce qui a été réalisé et les choix clés**
- Méthode en deux temps : des **portes éliminatoires** (G1 flux Citiz exploitable, G2 périmètre EPCI ou métropole, G3 GTFS ouvert, G4 carroyage INSEE, G5 taille du graphe, G6 intérêt métier), puis une **note pondérée** S1 à S7 (qualité du flux Citiz, fraîcheur, GTFS, second mode, contraste dense / peu dense, taille, récit pour le jury).
- Sept agglomérations candidates examinées. Lyon (trop peuplée) et le Pays Basque (trop étendu) écartés aux portes. Nantes et Rennes ont la meilleure note (90 / 100), La Rochelle 87,5. **Règle écrite avant la notation : à moins de 5 points du meilleur score, retenir la plus petite superficie.** La Rochelle (327 km²) est donc retenue ; Nantes Métropole (523 km²) reste le territoire de secours.
- Vérifications de verrouillage V-a à V-d (validité du GTFS à la date de démonstration, carreaux dans l'emprise…), faites le 21/10/2026.

**3. Ce que cela apporte**
Un territoire de 28 communes et 174 016 habitants, avec 24 stations Citiz, 136 stations vélo et 534 arrêts de bus : assez riche pour un vrai arbitrage (centre dense, périphérie peu desservie), assez petit pour un calcul exact. `docs/selection_territoire.md`.

**4. Transition**
Le territoire étant connu, le travail pouvait commencer pour de bon : il fallait un **dépôt** organisé pour que tout soit traçable dès le premier fichier.

---

### 📌 Mission 3 : Initialiser le dépôt

**1. Pourquoi cette mission ?**
La rigueur se voit dans le dépôt. Un jury data vérifie qu'on peut rejouer le travail ; un futur développeur doit s'y retrouver. Et surtout, les données (plusieurs centaines de Mo) ne doivent jamais polluer l'historique Git.

**2. Ce qui a été réalisé et les choix clés**
- Arborescence `data/bronze|silver|gold`, `docs`, `notebooks`, `src`, `tests`, `scripts`, `config`, `powerbi`, `reports`.
- `.gitignore` qui exclut toutes les données (`data/**`, `*.parquet`, archives…) mais **garde les manifestes** `_manifest.json`, preuves de traçabilité.
- `requirements.txt` et `requirements-lock.txt` (versions figées), environnement Python 3.11 sur Windows.
- Conventions de nommage (`docs/conventions.md`) : notebooks `NN_couche_objet`, scripts `verbe_objet`, tables `objet_territoire.parquet`.
- Règle de travail : le code est écrit dans le dépôt, les commandes `git` sont exécutées par le porteur.

**3. Ce que cela apporte**
Un socle propre : n'importe qui clone le dépôt, installe l'environnement et sait où chercher. L'historique Git devient lui-même une preuve de méthode.

**4. Transition**
Avant de télécharger quoi que ce soit, il fallait savoir **quoi** télécharger, **d'où**, et **sous quelle licence**.

---

### 📌 Mission 4 : Registre des sources

**1. Pourquoi cette mission ?**
« Les sources doivent être citées et traçables » est une exigence du sujet. Un chiffre sans source est un chiffre que le jury peut contester. Le registre est aussi l'outil qui révèle les manques (pas de données d'usage, pas de coûts).

**2. Ce qui a été réalisé et les choix clés**
- `docs/registre_des_sources.xlsx` : 26 sources, classées **obligatoire / recommandée / optionnelle**, avec producteur, format, usage métier, granularité, fréquence, licence, URL, couche cible, limites connues et contrôles prévus.
- Stratégie de traçabilité : date de récupération, empreinte **SHA-256** (une « signature » du fichier : si un octet change, l'empreinte change), version, chemin local, licence constatée.
- Section « décisions à valider avec Citiz » et liste des champs à demander pour obtenir un jour une **vraie cible d'usage** (réservations, durées, taux d'occupation).
- Règle : rien n'est saisi sans avoir été lu sur la source ; sinon « à vérifier ».

**3. Ce que cela apporte**
La liste de référence des données, livrable exigé par le sujet, et la preuve que chaque chiffre a une origine. Le registre a aussi rendu visibles les deux trous structurels du projet : **pas d'usage**, **pas de coûts** (d'où `docs/registre_couts.md`, plus tard).

**4. Transition**
Avec des sources hétérogènes (zip GTFS, flux JSON GBFS, GeoPackage INSEE, graphe OSM), il fallait une **architecture** qui les range et les transforme sans jamais perdre la trace de l'original.

---

### 📌 Mission 5 : Architecture Bronze / Silver / Gold

**1. Pourquoi cette mission ?**
Mélanger données brutes, données nettoyées et résultats dans un même dossier, c'est perdre la capacité de dire d'où vient un chiffre. L'architecture « médaillon » sépare les états de la donnée pour que chaque transformation soit isolée, contrôlée et rejouable.

**2. Ce qui a été réalisé et les choix clés**

| Couche | Rôle | Règle d'or |
|---|---|---|
| **Bronze** | Copie fidèle de la source, à une date | Jamais modifiée ; empreinte et manifeste |
| **Silver** | Données fiables, sans interprétation métier | Typage, nettoyage, dédoublonnage, jointures, qualité ; pas de KPI |
| **Gold** | Tables de décision | KPI, candidats, score, optimisation, exports |

- Sens unique : Bronze → Silver → Gold.
- Décisions AD1 à AD6 : calculs dans la projection **Lambert-93 (EPSG:2154)**, en mètres, exacte pour la France ; exports en **WGS84 (EPSG:4326)**, le système GPS des cartes web ; formats **Parquet / GeoParquet** (colonnes compressées, types conservés, géométrie incluse) plutôt que CSV ; un seul dossier lu par la restitution (`gold/exports/`) ; les tables de paires (très grandes) n'y vont jamais.
- Dictionnaire des tables (`docs/data_dictionary.md`) : nom, grain, clé, colonnes, source, usage.

> **CRS, en une phrase :** le « système de coordonnées de référence » dit comment lire une position. En Lambert-93, une distance se lit directement en mètres ; en WGS84, en degrés. Mélanger les deux fausse toutes les distances, d'où une règle unique.

**3. Ce que cela apporte**
Une carte du chantier : on sait quelle table existe, d'où elle vient, à quoi elle sert et qui la lit. `docs/architecture_data.md`.

**4. Transition**
L'architecture définissait les cases ; il fallait maintenant **remplir Bronze**, source par source, en prouvant que rien n'a été altéré.

---

### 📌 Mission 6 : Ingestion Bronze

**1. Pourquoi cette mission ?**
C'est la fondation de la preuve. Si le fichier d'origine n'est pas conservé à l'identique et daté, aucun résultat ne peut être rejoué ni défendu.

**2. Ce qui a été réalisé et les choix clés**
- Scripts `scripts/ingest_bronze.py` et `scripts/ingest_osm.py`, modules `src/ingestion/`.
- Dossiers datés et **immuables** : `data/bronze/<famille>/<territoire>/<source>_<AAAA-MM-JJ>/`. Un dossier existant n'est jamais écrasé (suffixe `_2` pour un second passage).
- Un `_manifest.json` par dossier : URL, date, licence constatée, taille, SHA-256 de chaque fichier.
- Ordre par lots : lot 0 (GTFS et Filosofi, pour verrouiller le territoire), lot 1 (communes, réseau OSM, Citiz, vélos). Le lot 2 (autres villes Citiz, pour le modèle H6) n'a pas été ingéré, faute de temps.
- Critères de réussite écrits : fichiers présents et non vides, empreinte vérifiée, contrôles `ok` ou alerte documentée, licence notée.

**3. Ce que cela apporte**
Sept sources réelles déposées (S01 Citiz, S02 GTFS Yélo, S03 et S03d Filosofi, S04 Admin Express, S05 réseau piéton, S08 vélos Yélo), chacune vérifiable octet par octet.

**4. Transition**
Les fichiers bruts sont fidèles mais pas utilisables tels quels : doublons, coordonnées douteuses, formats disparates. Place au **nettoyage**.

---

### 📌 Mission 7 : Nettoyage Silver

**1. Pourquoi cette mission ?**
Des données ouvertes ne sont pas des données propres. Un arrêt compté deux fois, une coordonnée inversée ou une valeur manquante remplacée par zéro faussent silencieusement tous les KPI.

**2. Ce qui a été réalisé et les choix clés**
- Règles de nettoyage par source **RC-01 à RC-16** (identifiant manquant → rejet ; doublon d'identifiant → rejet des deux lignes et alerte, jamais un choix au hasard ; quai jamais desservi → exclu…).
- Règles géographiques **RG-01 à RG-08** (coordonnées dans l'emprise, précision, rattachement au réseau à moins de 400 m).
- **Déduplication des arrêts :** le GTFS de Yélo décrit 981 quais rattachés à 534 arrêts. Une option est un arrêt, pas un quai, sinon un arrêt à deux quais compterait double. La table `dedup_correspondances` garde la provenance de chaque quai.
- Valeurs manquantes conservées et signalées (jamais remplacées par 0 ou une moyenne) ; carreaux imputés par l'INSEE marqués `est_impute`.
- Colonnes d'audit sur chaque ligne : source, identifiant d'origine, fichier, empreinte, date, `run_id`, règles appliquées, statut.
- Contrôles automatiques bloquants **CS-01 à CS-12** (entrée = sortie + rejets, clé unique, CRS, géométries valides, 28 communes…).

**3. Ce que cela apporte**
Une base fiable et auditable (`data/silver/`), avec ses rejets et alertes tracés (`data/silver/quality/`). `docs/methodologie.md`.

**4. Transition**
Les données sont propres mais isolées : un carreau ne « sait » pas à quelle commune il appartient, ni quelle station il atteint. Il fallait les **relier dans l'espace**.

---

### 📌 Mission 8 : Jointures spatiales

**1. Pourquoi cette mission ?**
Toute la valeur du projet tient dans une relation : *ce carreau d'habitants atteint-il cette station en 5 minutes de marche ?* Une jointure inexacte crée des habitants fantômes ou en oublie.

**2. Ce qui a été réalisé et les choix clés**
- Principe : joindre **par attribut** quand la source fournit la clé (codes INSEE), **par géométrie** seulement sinon, et doubler chaque jointure géométrique d'un contrôle.
- Jointures J0 à J8 dans l'ordre : communes → EPCI ; carreau → commune (attribut INSEE, contrôlé géométriquement à 97,69 %) ; option → réseau ; option → commune (99,86 %) ; carreau → réseau ; **carreau × option** ; plus tard candidat × carreau.
- **Accès à 5 minutes = 400 m de marche réelle** (H2, 4,8 km/h) : accès du carreau au réseau + plus court chemin sur le réseau piéton OpenStreetMap + accès à la station.
- Repli « à vol d'oiseau » prévu, mais mesuré : il **surestime** l'accès (2 096 carreaux atteints contre 1 463 sur réseau réel). Le réseau réel a donc été retenu.

> **Isochrone, en une phrase :** la zone que l'on peut atteindre en un temps donné. Ici, au lieu de dessiner des polygones, on calcule directement, pour chaque station, la liste des carreaux à moins de 400 m de marche : c'est plus exact et plus simple à contrôler.

**3. Ce que cela apporte**
La table des paires carreau × option (`gold/accessibility/paires_cellule_offre_larochelle`), source unique de toutes les distances. `docs/strategie_jointures.md`.

**4. Transition**
Avant de publier le moindre KPI, il fallait **prouver la qualité** des données et des jointures, et séparer trois notions que tout le monde confond.

---

### 📌 Mission 9 : Qualité et couverture

**1. Pourquoi cette mission ?**
Un jury data demande toujours « vos données sont-elles fiables ? ». Il fallait y répondre avec des chiffres, et distinguer trois notions :

| Notion | Question |
|---|---|
| Qualité des données | Les données sont-elles complètes, valides, uniques, fraîches ? |
| Couverture des données | Avons-nous la donnée pour tout le territoire ? |
| Couverture de mobilité | Les habitants ont-ils une option à 5 min ? |

**2. Ce qui a été réalisé et les choix clés**
- Six dimensions (complétude, validité, unicité, cohérence, fraîcheur, traçabilité), formules et seuils écrits.
- KPI de jointure (taux de rattachement, connexité du réseau piéton).
- Méthode anti-double-comptage : tout est calculé au carreau, chaque carreau compté une fois.
- Table Gold `qualite_donnees_larochelle` : **52 indicateurs**, dont 40 conformes, 3 alertes, 9 informatifs.
- Les 3 alertes sont expliquées : flux vélo Yélo vieux de 126 jours, capacité des stations vélo absente, 98,3 % des nœuds piétons connectés (seuil 99 %). Aucune ne touche la recommandation Citiz.

**3. Ce que cela apporte**
Une page « confiance » prête pour le jury, et une trame « limites des données » pour la soutenance. `docs/protocole_qualite.md`.

**4. Transition**
Les données étant prouvées, on pouvait enfin **mesurer la situation actuelle** : qui est desservi, qui ne l'est pas.

---

### 📌 Mission 10 : KPI d'accessibilité

**1. Pourquoi cette mission ?**
C'est le diagnostic exigé par les objectifs O1 et O2 du sujet, et la base de toute recommandation : on ne peut pas dire où ajouter sans savoir où il manque.

**2. Ce qui a été réalisé et les choix clés**
- Table principale au carreau : `acces_cellule_larochelle` (nombre d'options par mode, distance minimale, desservi oui / non, quintile de niveau de vie).
- KPI : options accessibles (K1), taux de couverture (K2), population desservie et non desservie (K3, K4), population servie par chaque station (K5, non additive), équité par quintile de revenu (K12).
- Modes comptés sans répétition : un habitant desservi par le bus et le vélo compte une fois en « tous modes ».
- Agrégations par commune et pour l'EPCI.

**3. Ce que cela apporte**
Le diagnostic chiffré : 77,8 % des habitants ont une option, 9,8 % seulement ont Citiz ; **9 communes sur 28** sont sous 60 % de couverture tous modes (de 35 % à 59 %) : ce sont les **communes prioritaires**. Constat contre-intuitif : les ménages les plus modestes sont les mieux desservis (89 %). `docs/kpi_acces.md`.

**4. Transition**
Le diagnostic montre où il manque ; il fallait maintenant identifier **où l'on pourrait ajouter** une station, et comparer ces emplacements.

---

### 📌 Mission 11 : Zones candidates et score de potentiel

**1. Pourquoi cette mission ?**
Le sujet demande d'estimer la valeur d'un emplacement candidat. Sans historique d'usage, un « modèle prédictif » serait une fiction : le projet a choisi un **score multicritère de potentiel**, transparent et décomposable.

**2. Ce qui a été réalisé et les choix clés**
- **Site candidat** = nœud du réseau piéton relié à au moins un carreau peuplé : 2 547 sites, évalués pour Citiz, vélo et bus.
- Exclusions écrites : hors EPCI, pas d'accès voiture (pour Citiz), aucun habitant nouvellement couvert, redondance > 80 %. Il reste **2 200 sites Citiz**.
- **Score K10 sur 100** = somme de 5 contributions : impact (habitants nouvellement couverts, 40 %), besoin (habitants sans option, 20 %), complémentarité bus (15 %), logement collectif (15 %), petits ménages (10 %).
- Normalisation par **rang centile** (« meilleur que 90 % des sites »), robuste aux valeurs extrêmes.
- Sensibilité : chaque poids varié de ±50 % (l'ordre d'ensemble tient, Spearman ≥ 0,978, mais le top 20 change de 10 % à 65 %) ; 500 tirages aléatoires de poids pour mesurer la robustesse de chaque site.
- Garde-fou d'équité : quota de 30 % de communes prioritaires dans un top 20 « équité ».

**3. Ce que cela apporte**
Un classement explicable (on voit **pourquoi** un site est bien noté) et une conclusion méthodologique forte : le haut du classement est serré (scores de 79 à 81), donc **le score départage, il ne décide pas**. `docs/score_potentiel.md`, `docs/model_card.md`.

**4. Transition**
Un classement de sites ne suffit pas : deux sites voisins touchent les mêmes habitants. Pour choisir un **portefeuille** sous budget sans compter deux fois les mêmes personnes, il fallait une **optimisation**.

---

### 📌 Mission 12 : Optimisation budgétaire

**1. Pourquoi cette mission ?**
C'est le cœur du sujet : passer d'un classement à une **décision d'investissement**. Prendre les 10 premiers du classement serait une erreur : ils sont voisins et se partagent les mêmes habitants.

**2. Ce qui a été réalisé et les choix clés**
- Problème classique de **couverture maximale sous budget** (Church et ReVelle, 1974) : choisir des sites (oui / non) pour maximiser les habitants nouvellement couverts, chacun compté une fois, sans dépasser le budget.
- Résolution exacte par **PLNE** avec PuLP et le solveur CBC.

> **Solveur PLNE, en une phrase :** un programme qui explore intelligemment toutes les combinaisons de oui / non et **prouve** qu'aucune n'est meilleure que celle qu'il renvoie. Ici, à 0,1 % près.

- Décisions validées (D-1 à D-5) : objectif = habitants nouvellement couverts par Citiz ; coûts sur 3 ans de 4 000 / 8 500 / 13 000 € (boîtier 4 000 € HT + forfait jusqu'à 250 € TTC par mois, source : convention publique collectivité – Citiz) ; budgets de simulation 42 500 / 85 000 / 170 000 €.
- Deux pièges corrigés : PuLP affichait « Optimal » même quand le solveur s'arrêtait sur sa limite de temps (on lit désormais le vrai statut) ; une contrainte valide (pas plus de ⌊budget / coût minimal⌋ stations) a ramené le cas le plus lent de plus de 120 s à 0,3 s.
- **Variante équité** : au moins 30 % des habitants gagnés dans les communes prioritaires, calculée sur la couverture réelle (un piège de formulation évité et testé).
- Contrôles bloquants O-T1 à O-T8 (budget, absence de double compte, optimum prouvé, part d'équité réelle…) ; une règle simple (glouton) sert de témoin : elle égale l'optimum dans 8 cas sur 9.

**3. Ce que cela apporte**
12 scénarios et une courbe budget → impact. Rendements décroissants (la 1re station couvre 4 040 habitants, la 30e 894). Le coût par station pèse autant que le budget (à 85 000 €, de 12 888 à 30 834 habitants). Le prix de l'équité est mesuré : −27 %, −23 %, −15 % selon le budget. `docs/optimisation.md`, `docs/registre_couts.md`.

**4. Transition**
Les résultats existent, mais dans des tables. Un décideur a besoin de les **voir**, de les manipuler et de comprendre l'arbitrage en quelques secondes.

---

### 📌 Mission 13 : Restitution (rapport conçu pour Power BI, livré en application Streamlit)

**1. Pourquoi cette mission ?**
Le jury attend une démonstration en direct sur données réelles, et un décideur non technique doit comprendre en 30 secondes. La restitution est le pont entre l'analyse et la décision.

**2. Ce qui a été réalisé et les choix clés**
- Conception complète en 5 pages (synthèse, couverture actuelle, candidats et score, optimisation, méthode et limites) : objectif de chaque page, KPI, visuels, filtres, interactions, mesures, messages, erreurs à éviter, modèle de données en étoile (22 tables), couleurs accessibles, maquettes. `powerbi/`.
- **Décision P-1 révisée :** l'application est livrée en **Streamlit** (Python) plutôt que Power BI, sur la même conception. Raisons : cartes des vrais carreaux de 200 m sans service externe, logique en Python testé, fonctionnement hors ligne, pas de licence. Les exports restent lisibles par Power BI.
- Script d'export `scripts/build_exports.py` (contrôles X-01 à X-07) ; mesures Python testées (`src/export/mesures.py`), équivalentes aux mesures DAX ; titres calculés à partir des données.
- Couleurs Okabe-Ito, lisibles par les daltoniens, toujours doublées d'un libellé ; vocabulaire « communes prioritaires ».
- Page 5 : 6 recoupements prouvent que l'application affiche exactement les chiffres du pipeline.

**3. Ce que cela apporte**
Un outil démontrable : changer le budget, le coût ou la variante, et voir la carte et le prix de l'équité se mettre à jour. `docs/application.md`, `app/`.

**4. Transition**
Un bon outil mal présenté ne convainc pas. Il fallait une **stratégie de soutenance** pour un public mixte.

---

### 📌 Mission 14 : Soutenance

**1. Pourquoi cette mission ?**
L'évaluation se fait sur une défense : convaincre à la fois une DG, des élus, un jury académique et des profils data, avec des attentes différentes, en 5 ou 10 minutes.

**2. Ce qui a été réalisé et les choix clés**
- Un **fil rouge** en trois phrases : la question, la réponse (10 stations, couverture doublée), l'arbitrage (le prix de l'équité).
- Pitchs de 5 et 10 minutes, texte mot à mot (`narration.md`), plan des slides avec un titre-réponse par slide.
- Support de 12 slides et 2 annexes, réparti entre 6 personnes avec notes de présentation (`repartition_equipe.md`).
- 33 questions difficiles et leurs réponses (`questions_jury.md`), dont la plus attaquable : « où est le modèle prédictif ? ».
- Démonstration pilotée par la question ; vidéo de secours sous-titrée générée automatiquement (`scripts/enregistrer_demo.py`).
- Limites formulées sans fragiliser le projet : *limite → pourquoi c'est raisonnable → effet sur la décision → suite*.

**3. Ce que cela apporte**
Une soutenance répétable, des réponses sourcées, un plan B. `docs/soutenance/`.

**4. Transition**
Il restait à **tout vérifier** avant de livrer : un oubli (dépôt privé, slides absentes) peut annuler des jours de travail.

---

### 📌 Mission 15 : Checklist finale

**1. Pourquoi cette mission ?**
Le jour J, tout ce qui n'a pas été vérifié peut casser. Une checklist transforme le stress en procédure.

**2. Ce qui a été réalisé et les choix clés**
- 14 sections (dépôt, Bronze, Silver, Gold, qualité, KPI, score, optimisation, application, documentation, slides, démo, soutenance, éthique), avec pour chaque item la preuve attendue, la priorité (bloquant / important / bonus), le responsable et **l'état constaté** dans le dépôt.
- 9 erreurs éliminatoires et leur parade ; plan de secours pour 9 pannes ; les dix dernières minutes minute par minute.
- Les manques trouvés ont été corrigés aussitôt : README à jour, fiche du score, notebook de démonstration (`notebooks/07_hackathon_demo.ipynb`), figures de secours.

**3. Ce que cela apporte**
Une livraison maîtrisée. `docs/soutenance/checklist_finale.md`.

**4. Et après ?**
Les suites naturelles : le modèle H6 validé ville par ville, l'optimisation bus et vélo avec des coûts validés, un devis Citiz pour remplacer l'hypothèse de coût, et un **test terrain de 3 stations pendant un an** pour mesurer enfin l'usage réel.

---

## 3. Synthèse de l'architecture et chaîne de valeur

### 3.1 De la donnée brute à la décision

| Étape | Ce que devient la donnée | Exemple concret | Pourquoi c'est utile à la décision | Où |
|---|---|---|---|---|
| **Sources** | Fichiers publics hétérogènes | Zip GTFS Yélo, flux GBFS Citiz, GeoPackage Filosofi, graphe OSM | Les seules données disponibles, gratuites et réutilisables | `docs/registre_des_sources.xlsx` |
| **Bronze** | Copie fidèle, datée, signée (SHA-256) | `data/bronze/gtfs/larochelle/S02_2026-10-21/` | On peut prouver d'où vient chaque chiffre | `scripts/ingest_*.py` |
| **Silver** | Données nettoyées, dédoublonnées, reliées à l'espace | 981 quais → 534 arrêts ; 2 637 carreaux rattachés à une commune et au réseau | On compte juste : ni doublons, ni habitants fantômes | `scripts/build_silver.py`, `build_spatial.py` |
| **Gold : accessibilité** | Qui atteint quoi en 5 min | Paires carreau × station à ≤ 400 m de marche ; KPI au carreau | Le diagnostic : 77,8 % desservis, 9,8 % pour Citiz | `build_paires.py`, `build_kpi_acces.py` |
| **Gold : candidats** | Où l'on pourrait ajouter, et pourquoi | 2 200 sites Citiz notés sur 100, décomposés en 5 critères | Un classement explicable | `build_candidats.py` |
| **Gold : optimisation** | Quel portefeuille financer | 12 scénarios, courbe budget → impact, prix de l'équité | La recommandation chiffrée | `build_optimisation.py` |
| **Exports** | Tables prêtes à afficher, en WGS84 | 22 tables + 2 GeoJSON, contrôles X-01 à X-07 | Une restitution qui ne recalcule rien | `build_exports.py` |
| **Application** | 5 pages interactives | Changer budget, coût, variante | La décision se prend en voyant l'arbitrage | `app/` (Streamlit ; conception Power BI dans `powerbi/`) |

Trois garanties traversent toute la chaîne :
- **Traçabilité :** chaque table porte un `run_id` (date UTC + commit Git, `-modifie` si le code n'était pas commité) et chaque dossier un manifeste.
- **Contrôles bloquants :** CS (Silver), J (jointures), Q (qualité), O-T (optimisation), X (exports). Si un contrôle échoue, le script s'arrête au lieu de produire un chiffre faux.
- **Une seule définition par chiffre :** l'application et le notebook lisent les mêmes tables et vérifient les mêmes égalités.

### 3.2 Les trois piliers de la solution

#### Pilier 1 — Mesurer la qualité et la couverture réelle

*Savoir avant de recommander.*

- Accès mesuré sur le **réseau piéton réel**, pas à vol d'oiseau (qui surestimerait l'accès de 43 % en nombre de carreaux atteints).
- Population au **carreau de 200 m**, chaque habitant compté une fois.
- 52 indicateurs de qualité ; les alertes sont affichées, pas cachées.
- Trois notions jamais confondues : qualité des données, couverture des données, couverture de mobilité.

**Ce que le pilier rend possible :** dire avec certitude qui est desservi aujourd'hui, et donc qui gagnerait à une nouvelle station.

#### Pilier 2 — Score multicritère de potentiel territorial

*Comparer des emplacements de façon explicable.*

- 5 critères observés, pondérés et affichés ; chaque note se lit par ses contributions.
- Testé en sensibilité : l'ordre d'ensemble est stable, le haut du classement est serré.
- **Pas une prédiction** : sans historique d'usage, le projet refuse d'inventer une cible. Le modèle appris H6 est conçu et documenté, non livré.

**Ce que le pilier rend possible :** expliquer pourquoi un site est intéressant, et départager deux portefeuilles qui couvrent autant d'habitants.

#### Pilier 3 — Optimisation sous contrainte budgétaire

*Décider avec un budget fini.*

- Portefeuille optimal prouvé : chaque habitant compté une fois, budget respecté.
- Scénarios multi-budgets et multi-coûts : la sensibilité au coût unitaire est rendue visible.
- Variante équité : le prix de l'équité est mesuré en habitants, et la décision reste aux élus.

**Ce que le pilier rend possible :** la liste ordonnée des stations à financer, avec son impact et son coût.

### 3.3 Ce qui est certain, estimé, hypothétique

| Nature | Exemples |
|---|---|
| **Certain (mesuré)** | Population par carreau ; positions des stations et arrêts ; distances sur le réseau ; habitants nouvellement couverts par un portefeuille ; optimum prouvé |
| **Estimé** | Coûts bas et haut d'une station (sources publiques) |
| **Hypothèse de travail** | 5 min = 400 m ; coût central de 8 500 € ; budgets de 42 500 à 170 000 € ; seuil de 60 % pour une commune prioritaire ; 30 % pour l'équité ; pondérations du score |
| **Hors de portée** | Fréquentation, chiffre d'affaires, CO₂ évité (faute de données d'usage et de report modal) |

---

## 4. Bilan et guide de lecture par profil

### 4.1 Pour le jury et les évaluateurs

| Ce que vous évaluez | Où le vérifier en priorité |
|---|---|
| Un problème concret et une recommandation claire | § 1.2 ; slides 2, 9, 12 ; page 1 de l'application |
| Démonstration sur données réelles | Application (`streamlit run app/streamlit_app.py`) ; vidéo `reports/demo/demo_application.mp4` |
| Consolidation de sources hétérogènes | `docs/registre_des_sources.xlsx` ; manifestes `data/bronze/**/_manifest.json` |
| Qualité, couverture, limites | `docs/protocole_qualite.md` ; page 5 de l'application ; slide 5 |
| Indicateur justifié, absence de fuite | `docs/model_card.md` ; `docs/score_potentiel.md` |
| Optimisation sous budget | `docs/optimisation.md` ; `tests/test_optimisation.py` ; annexe B des slides |
| Éthique, équité, vie privée | Variante équité (slide 10) ; `docs/suivi_risques.md` ; page 5 |
| Reproductibilité | README « Reproduire » ; `pytest` ; `run_id` dans chaque table |

**Trois points forts à tester :** demandez un chiffre de la slide, retrouvez-le dans l'application ; demandez « comment évitez-vous le double comptage ? » ; changez le coût d'une station en direct.

**Limites assumées :** pas de modèle prédictif d'usage livré ; coûts estimés ; seul Citiz optimisé ; pas d'Omphale ni de bilan carbone.

### 4.2 Pour le décideur (DG Citiz, élus, AOM)

1. **Lire § 1.2** : la recommandation tient en quatre chiffres (10 stations, +18 816 habitants, 4,52 €, couverture doublée).
2. **Ouvrir la page 4 de l'application** et entrer **votre** budget et **votre** coût par station : le portefeuille se recalcule.
3. **Choisir le curseur d'équité** en connaissant son prix (page 4, bouton Équité) : moins d'habitants au total, mais des stations dans les communes peu desservies.
4. **Valider sur le terrain** les sites retenus : foncier, stationnement, accord des communes ne sont pas dans les données.
5. **Lancer un test** de 3 stations pendant un an, avec des indicateurs d'usage, pour transformer le score en modèle appris.

**Trois précautions :** le score n'est pas une prévision de locations ; 85 000 € est un budget de simulation ; 8 500 € par station est une hypothèse, qu'un devis remplace en une ligne de configuration.

### 4.3 Pour l'équipe technique et data

| Besoin | Où regarder |
|---|---|
| Lancer l'application | README « Application de restitution » ; `docs/application.md` |
| Reconstruire tout le pipeline | README « Reproduire » (12 étapes) |
| Comprendre l'architecture | `docs/architecture_data.md` ; `docs/conventions.md` ; `docs/data_dictionary.md` |
| Règles de nettoyage et contrôles | `docs/methodologie.md` (RC, RG, CS) ; `src/cleaning/` |
| Jointures et accessibilité | `docs/strategie_jointures.md` ; `src/geospatial/` |
| Qualité | `docs/protocole_qualite.md` ; `src/evaluation/` ; `config/qualite.yaml` |
| KPI | `docs/kpi_acces.md` ; `src/features/kpi_acces.py` |
| Score | `docs/score_potentiel.md` ; `docs/model_card.md` ; `src/scoring/candidats.py` ; `config/score.yaml` |
| Optimisation | `docs/optimisation.md` ; `src/optimization/couverture.py` ; `config/optimisation.yaml` |
| Exports et mesures | `src/export/exports.py` ; `src/export/mesures.py` ; `config/app.yaml` |
| Démonstration et notebook | `notebooks/07_hackathon_demo.ipynb` ; `scripts/enregistrer_demo.py` |
| Risques ouverts | `docs/suivi_risques.md` (R1 à R29) |

**Règles de contribution :** ne jamais modifier Bronze ; committer avant de lancer un build (sinon `run_id` en `-modifie`) ; toute nouvelle règle a son identifiant et son contrôle ; tout nouveau chiffre a sa définition et sa source ; `pytest` doit rester vert.

**Pistes d'évolution, par ordre de valeur :** ingérer le lot 2 et livrer H6 ; optimisation multi-équipements ; sensibilité des seuils d'équité ; projections Omphale pour un scénario 2030 ; portage vers un lakehouse Fabric (même logique Bronze / Silver / Gold).

---

## 5. Glossaire

| Terme | Définition simple |
|---|---|
| **AOM** | Autorité organisatrice de la mobilité : la collectivité qui organise les transports |
| **Bronze / Silver / Gold** | Les trois états de la donnée : brute, propre, prête pour la décision |
| **Carreau (200 m)** | Petit carré de 200 m de côté où l'INSEE publie la population ; notre unité de calcul |
| **CRS** | Système de coordonnées : Lambert-93 (en mètres) pour calculer, WGS84 (GPS) pour afficher |
| **Commune prioritaire** | Commune dont moins de 60 % des habitants ont une option à 5 min (9 sur 28) |
| **Couverture de mobilité** | Part des habitants qui ont au moins une option à 5 min de marche |
| **EPCI** | Intercommunalité ; ici la CA de La Rochelle (28 communes) |
| **Filosofi** | Données INSEE de population et de revenus au carreau ; certains carreaux sont imputés (secret statistique) |
| **GBFS** | Format ouvert des stations de mobilité partagée (vélos, autopartage) |
| **GeoParquet** | Format de fichier en colonnes, compressé, qui garde les types et la géométrie |
| **Glouton** | Règle simple : prendre à chaque tour le site qui rapporte le plus par euro ; sert de témoin |
| **GTFS** | Format ouvert des transports publics (arrêts, lignes, horaires) |
| **Isochrone** | Zone atteignable en un temps donné ; ici, 5 min de marche |
| **K6** | Habitants nouvellement couverts : passent de « aucune option » à « au moins une », comptés une fois |
| **Manifeste** | Fiche JSON qui décrit un dossier de données : source, date, empreinte, licence |
| **OSM** | OpenStreetMap, carte collaborative dont on extrait le réseau piéton |
| **PLNE / solveur** | Programmation linéaire en nombres entiers : un programme qui trouve et prouve la meilleure combinaison de oui / non sous contraintes |
| **Rang centile** | Position d'un site parmi les autres : « meilleur que 90 % » |
| **`run_id`** | Identifiant d'exécution : date UTC et commit Git du code qui a produit la table |
| **Score de potentiel (K10)** | Note sur 100 qui classe des sites ; ce n'est pas une prédiction |
| **SHA-256** | Empreinte d'un fichier : si un seul octet change, l'empreinte change |
