# Sélection du territoire

**Statut :** grille remplie le 20 octobre 2026. Territoire retenu : **CA de La Rochelle**.
**Date du repérage catalogue :** 20 octobre 2026. **Date de la vérification :** 20 octobre 2026.
**Ce document autorise :** comparer des périmètres sur pièces. Consulter un flux dans le navigateur et garder des captures d'écran dans `docs/annexes/selection_territoire/`. Aucun fichier de données dans `data/`.
**Ce document n'autorise pas :** déposer un GTFS, un carroyage, un graphe piéton ou un export GBFS dans `data/`, nettoyer des données, modéliser, ou ouvrir Power BI.

Tant que la grille n'est pas remplie et qu'une ligne « Décision » n'est pas écrite en bas de ce fichier, toutes les décisions géospatiales restent provisoires. Lyon 2e reste au plus un essai technique ultérieur, pas un territoire d'étude.

---

## 1. Décision à prendre

Retenir **un seul périmètre d'étude**, assez limité pour un traitement Python local, avec un flux GBFS Citiz exploitable, un réseau de transport public ouvert, une population carroyée et un intérêt métier (Citiz déjà présent, zones encore à couvrir).

Le périmètre d'étude est un **EPCI ou une métropole**, pas la France, pas une région, pas le fichier régional Citiz pris en bloc.

---

## 2. Méthode

Quatre temps, dans cet ordre. Pour un candidat, on s'arrête à la première porte échouée. L'ordre de vérification est **G1 → G2 → G5 → G6 → G3 → G4** : G1 d'abord pour les sept candidats, parce que c'est la porte la plus éliminatoire et la plus rapide.

1. **Vivier.** Partir des jeux « Autopartage Citiz » au format GBFS sur le point d'accès national : [catalogue GBFS](https://transport.data.gouv.fr/datasets?format=gbfs&locale=fr&order_by=alpha). Une source publique équivalente est acceptable si l'URL, la date et la licence sont notées. Compléter la liste si le catalogue est paginé : le repérage ci-dessous n'est pas certifié exhaustif.
2. **Périmètre.** Pour chaque jeu, nommer le périmètre que l'on accepterait de traiter. Si le jeu couvre une région ou plusieurs villes éloignées, le territoire candidat est **une** intercommunalité à l'intérieur du jeu, pas le jeu entier.
3. **Portes.** Un candidat qui échoue une porte est écarté. On ne le note pas. On n'ouvre pas les portes suivantes pour ce candidat.
4. **Note.** Les candidats qui passent toutes les portes sont notés. Le meilleur score est proposé. **Si l'écart avec le meilleur score est ≤ 5 points, retenir la plus petite superficie.** La superficie est le quotient population / densité du comparateur INSEE (RP2023), en km². Ce n'est ni la population, ni le nombre de stations, ni le nombre de communes.

La décision n'est valide que lorsque chaque case « Preuve » contient une URL, une date de consultation et le constat (nombre de stations, nom du GTFS, millésime de population). Une case vide vaut un échec.

---

## 3. Portes éliminatoires

Toutes sont obligatoires.

| ID | Porte | Passage | Preuve à coller |
|---|---|---|---|
| G1 | Flux GBFS Citiz exploitable | La fiche existe, la ressource GBFS répond, `station_information` contient au moins une station avec latitude et longitude. La licence autorise la réutilisation. Le rattachement au périmètre est **provisoire** : il compare les noms ou adresses des stations à la liste des communes de l'EPCI (G2). | URL de la fiche, URL du flux, date, nombre de stations, licence, capture dans `docs/annexes/selection_territoire/` |
| G2 | Périmètre local | Le périmètre est un EPCI ou une métropole. Un jeu régional n'est pas un territoire d'étude. | Nom officiel de l'EPCI et liste de ses communes (fiche INSEE ou BANATIC, URL citée). Le contour Admin Express est reporté à E3. |
| G3 | Transport public ouvert | Au moins un GTFS du réseau structurant couvre ce périmètre, avec arrêts géolocalisés, sur transport.data.gouv.fr ou une source publique équivalente. | URL, date, nom du réseau |
| G4 | Population carroyée | Un carroyage Filosofi (ou équivalent INSEE) à 200 m couvre le périmètre. La porte sert à écarter un millésime absent ou un territoire non couvert (par exemple un DROM hors fichier), pas à départager deux métropoles. | URL, **millésime**, constat « carreaux présents sur le périmètre » |
| G5 | Faisabilité Python | Le graphe piéton OSM du périmètre est téléchargeable et calculable en local dans le temps du hackathon. Hypothèse de travail, non mesurée : viser environ 100 000 à 700 000 habitants. En dessous, l'arbitrage budgétaire est faible. Au-dessus, il faut une raison écrite ou un découpage. | Population et superficie sourcées, jugement explicite sur la taille du graphe |
| G6 | Intérêt métier | Des stations Citiz sont dans les communes de l'EPCI, et le périmètre n'est pas un ilôt trop petit pour discuter d'un budget (Lyon 2e est dans ce cas). Passage provisoire par noms de communes. | Nombre de stations G1 dont la commune est dans la liste G2 |

**Passage provisoire G1 / G6.** Le contour Admin Express n'est pas téléchargé avant E3. Jusque-là, une station est comptée dans l'EPCI si son nom ou son adresse cite une commune de la liste officielle. Confirmation géométrique à E3 : si moins de 80 % des stations du flux tombent dans le contour, la décision est rouverte. Le seuil de 80 % est une hypothèse à valider.

`station_status` et `vehicle_status` décrivent un instantané. Ils ne servent pas à juger l'offre structurelle et ne font pas passer G1.

---

## 4. Grille de note

Appliquée seulement si G1 à G6 sont passées. Chaque critère vaut 0, 1 ou 2. Score = somme (note × poids) / 2, sur 100.

S5 couvre aussi la diversité des besoins de mobilité : le contraste dense / peu dense rend un scénario d'équité lisible. S7 couvre la facilité de démonstration devant le jury.

| ID | Critère | Poids | 0 | 1 | 2 |
|---|---|---|---|---|---|
| S1 | Flux Citiz utilisable | 20 | fiche sans stations exploitables dans le périmètre | stations géolocalisées, champs incomplets | nom, latitude, longitude et capacité renseignés |
| S2 | Fraîcheur affichée par le producteur | 10 | date inconnue ou supérieure à 12 mois | 3 à 12 mois | moins de 3 mois, ou flux temps réel valide sur les stations |
| S3 | GTFS du réseau structurant | 15 | absent ou arrêts sans coordonnées | un réseau, couverture partielle | réseau principal couvrant le périmètre |
| S4 | Second mode ouvert (vélo partagé) | 10 | aucun GBFS vélo | jeu présent, incomplet | GBFS vélo exploitable sur le même périmètre |
| S5 | Contraste dense / peu dense | 15 | tissu homogène, scénario d'équité sans objet | deux types de communes | gradient lisible centre / périphérie |
| S6 | Taille pour Python local | 20 | région, ou métropole dont le graphe est jugé hors de portée | à la limite, à justifier | EPCI ou métropole confortable pour OSMnx en local |
| S7 | Récit pour le jury | 10 | cas difficile à expliquer | cas correct | Citiz déjà là, question d'implantation évidente |

---

## 5. Vivier constitué avant la notation

Liste du 20 octobre 2026, avant les portes. Ce n'est pas un classement, et une ligne de ce tableau n'est pas le territoire retenu. Les portes, les notes et la décision sont dans les sections 6 et 7. Les jeux régionaux restent hors périmètre d'étude en bloc.

| Jeu publié | Échelle déclarée | Conséquence pour la grille | Fiche |
|---|---|---|---|
| Citiz Angers Loire Métropole | CU | Candidat à ouvrir en priorité | catalogue |
| Citiz Grand Poitiers | CU | Candidat à ouvrir en priorité | catalogue |
| Citiz La Rochelle | CA de La Rochelle | Candidat à ouvrir en priorité | [fiche](https://transport.data.gouv.fr/datasets/citiz-autopartage-la-rochelle) |
| Citiz Pays Basque AUPA | à confirmer sur la fiche | Candidat à ouvrir en priorité | catalogue |
| Citiz Nantes Métropole | Nantes Métropole | Candidat, vérifier G5 (taille du graphe) | [fiche](https://transport.data.gouv.fr/datasets/citiz-autopartage-nantes) |
| Citiz Métropole de Lyon | Métropole de Lyon | Candidat, vérifier G5. Distinct du jeu régional AURA | catalogue |
| Citiz Rennes Métropole | Rennes Métropole | Candidat, vérifier G5 | catalogue |
| Citiz Gironde | plusieurs communes, dont Bordeaux | Ne pas prendre le jeu en bloc. Extraire un EPCI, puis appliquer les portes | catalogue |
| Citiz Haut de France | surtout la métropole lilloise et quelques villes | Idem : un sous-périmètre, pas le jeu entier | catalogue |
| Citiz Provence | Avignon, Marseille | Idem | [ressource](https://transport.data.gouv.fr/resources/83165) |
| Citiz Bourgogne Franche-Comté | plusieurs villes éloignées | Idem | [fiche](https://transport.data.gouv.fr/datasets/citiz-autopartage-bourgogne-franche-comte) |
| Citiz Auvergne Rhône Alpes | région | Hors périmètre d'étude. Des erreurs de validation étaient signalées sur la fiche au moment du repérage : à relire, pas à trancher ici | [fiche](https://transport.data.gouv.fr/datasets/citiz-autopartage-auvergne-rhone-alpes) |
| Citiz Grand Est | région | Hors périmètre d'étude en bloc | [fiche](https://transport.data.gouv.fr/datasets/citiz-autopartage-grand-est) |
| Citiz Occitanie | région, nombreuses communes | Hors périmètre d'étude en bloc | catalogue |
| Citiz Développement | France | Hors périmètre d'étude | [fiche](https://transport.data.gouv.fr/datasets/citiz-autopartage-developpement) |

Licence Ouverte 2.0 lue sur les fiches AURA, Nantes, Grand Est, La Rochelle et Développement. Elle reste à confirmer pour chaque candidat au moment de G1.

Ordre de vérification, qui n'est pas un classement : d'abord les communautés urbaines et d'agglomération (Angers, Grand Poitiers, La Rochelle, Pays Basque), ensuite les métropoles (Nantes, Lyon, Rennes) en surveillant G5.

---

## 6. Grille remplie le 20 octobre 2026

Les communes des stations viennent de [geo.api.gouv.fr](https://geo.api.gouv.fr/) à partir des coordonnées du flux : beaucoup de stations n'ont pas d'adresse. Ce n'est pas encore le contour Admin Express. La population et la densité viennent du comparateur INSEE, RP2023, géographie au 01/01/2026, pages consultées le 20 octobre 2026. La superficie indiquée est le quotient population / densité, arrondi au km².

Les captures des fiches sont dans `docs/annexes/selection_territoire/`. Aucun fichier n'a été déposé dans `data/`.

| Critère | Angers | Grand Poitiers | La Rochelle | Pays Basque | Nantes | Lyon | Rennes |
|---|---|---|---|---|---|---|---|
| G1 | passe | passe | passe | passe | passe | passe | passe |
| G2 | passe | passe | passe | passe | passe | passe | passe |
| G5 | passe | passe | passe | **échoue** | passe | **échoue** | passe |
| G6 | passe | passe | passe | non ouverte | passe | non ouverte | passe |
| G3 | passe | passe | passe | non ouverte | passe | non ouverte | passe |
| G4 | passe | passe | passe | non ouverte | passe | non ouverte | passe |
| S1 (20) | 2 | 2 | 2 | — | 2 | — | 2 |
| S2 (10) | 2 | 2 | 2 | — | 2 | — | 2 |
| S3 (15) | 2 | 2 | 1 | — | 2 | — | 2 |
| S4 (10) | 1 | 1 | 1 | — | 2 | — | 2 |
| S5 (15) | 2 | 2 | 2 | — | 2 | — | 2 |
| S6 (20) | 1 | 1 | 2 | — | 1 | — | 1 |
| S7 (10) | 2 | 2 | 2 | — | 2 | — | 2 |
| Score /100 | 85 | 85 | **87,5** | — | 90 | — | 90 |

### Preuves

**Angers Loire Métropole — portes passées, score 85.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-angers), licence Ouverte 2.0, mise à jour affichée le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/7/gbfs/3.0/gbfs.json`, `station_information` : 28 stations, 28 avec latitude et longitude, 28 avec `capacity`. Communes : Angers 25, Les Ponts-de-Cé 1, Avrillé 1, Beaucouzé 1. Capture `G1_angers_2026-10-20.png`.
- G2. Passe. CU Angers Loire Métropole, SIREN 244900015, 29 communes ([geo.api.gouv.fr/epcis/244900015/communes](https://geo.api.gouv.fr/epcis/244900015/communes)). [Comparateur INSEE](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-244900015).
- G5. Passe. 312 612 habitants en 2023, densité 468,9 hab/km², soit environ 667 km². Dans la fourchette de population. Superficie assez grande : la note de taille sera 1, pas un échec de porte.
- G6. Passe, provisoire. 28/28 stations dans l'EPCI.
- G3. Passe. Réseau Irigo, [GTFS](https://www.data.gouv.fr/datasets/angers-loire-metropole-reseau-irigo-gtfs-gtfs-rt-siri), ressource `irigo-angers-gtfs` au format GTFS, licence ODbL, fiche mise à jour le 2025-11-26. Archive non ouverte.
- G4. Passe sur le champ publié. Filosofi carroyé 200 m, millésime 2021, paru le 12/02/2026, France métropolitaine : [page INSEE](https://www.insee.fr/fr/statistiques/8735162?sommaire=8735243). Fichier non téléchargé.
- Notes. S1 = 2 (nom, coordonnées, capacité). S2 = 2 (fiche du jour). S3 = 2. S4 = 1 : GBFS Pony vélos et trottinettes, [fiche](https://www.data.gouv.fr/datasets/angers-trottinettes-velos-et-vae-en-libre-service), le `gbfs.json` répond mais ne publie pas de `station_information`, licence non précisée. S5 = 2 (ville-centre et communes de couronne). S6 = 1. S7 = 2. Score = (40+20+30+10+30+20+20) / 2 = 85.

**CU du Grand Poitiers — portes passées, score 85.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-grand-poitiers), licence Ouverte 2.0, mise à jour le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/9/gbfs/3.0/gbfs.json` : 21 stations, toutes avec coordonnées et capacité. Communes : Poitiers 18, Buxerolles 1, Chasseneuil-du-Poitou 1, Chauvigny 1. Capture `G1_poitiers_2026-10-20.png`.
- G2. Passe. CU du Grand Poitiers, 200069854, 40 communes. [Comparateur](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200069854).
- G5. Passe. 197 408 habitants, densité 185,4, soit environ 1 065 km². Population dans la fourchette. L'étendue baisse la note de taille, elle ne ferme pas la porte.
- G6. Passe, provisoire. 21/21.
- G3. Passe. [Offre de transport Grand Poitiers](https://www.data.gouv.fr/datasets/arrets-horaires-et-parcours-theoriques-des-reseaux-naq-vit-nva-m-1), GTFS agrégé `grand_poitiers-aggregated-gtfs.zip`, licence ODbL, fiche mise à jour le 2026-10-19. Archive non ouverte.
- G4. Même constat Filosofi 2021 que pour Angers.
- Notes. S4 = 1 : [Pony Poitiers](https://www.data.gouv.fr/datasets/velos-et-trottinettes-pony-poitiers), GBFS sans `station_information`, licence non précisée, fiche mise à jour le 2026-05-18. S6 = 1. Les autres notes sont 2. Score = 85.

**CA de La Rochelle — portes passées, score 87,5.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-la-rochelle), licence Ouverte 2.0, mise à jour le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/18/gbfs/v3.0/gbfs.json` : 24 stations, toutes avec coordonnées et capacité. Communes : La Rochelle 19, Lagord 2, Aytré 1, Puilboreau 1, Périgny 1. Capture `G1_larochelle_2026-10-20.png`.
- G2. Passe. CA de La Rochelle, 241700434, 28 communes. [Comparateur](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-241700434).
- G5. Passe. 182 435 habitants, densité 558,0, soit environ 327 km². C'est le périmètre le plus compact des sept.
- G6. Passe, provisoire. 24/24.
- G3. Passe, avec réserve de note. Les fichiers Yélo sont publiés séparément (stops, trips, routes, calendrier, stop_times), licence Ouverte, fiches mises à jour le 2026-10-19. Exemple : [GTFS stop](https://www.data.gouv.fr/datasets/transport-yelo-gtfs-stop-des-bus), qui contient `gtfs_stop.csv` et un `gtfs.zip`. Archive non ouverte : la couverture complète n'est pas constatée, d'où S3 = 1.
- G4. Même constat Filosofi 2021.
- Notes. S3 = 1, voir G3. S4 = 1 : [Yélo vélos](https://www.data.gouv.fr/datasets/yelo-disponibilite-des-velos-en-libre-service). Le champ `last_updated` vaut `2026-06-17T11:12:55+02:00` à la racine de `gbfs.json`, et la même valeur à la racine du seul flux lié, `system_information`. `gbfs.json` embarque en plus 137 stations et des disponibilités figées. Ce n'est pas un index GBFS vivant. S5 = 2 : les 28 communes ne sont pas au même niveau dans la [grille communale de densité INSEE](https://www.insee.fr/fr/information/8571524) (grille de densité 2025, fichier `fichier_diffusion_2026.xlsx`, mise en ligne le 15/05/2026, géographie au 01/01/2026). Degré à 3 postes : 2 communes en urbain dense, 15 en urbain intermédiaire, 11 en rural. L'EPCI est classé urbain intermédiaire. S6 = 2 : 182 435 habitants et environ 327 km², le périmètre le plus compact, tenable pour un graphe piéton local. S7 = 2 : Citiz est déjà sur l'agglomération, avec 24 stations, et la question d'implantation est directe. Score = (40+20+15+10+30+40+20) / 2 = 87,5.

**CA du Pays Basque — écartée à G5.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-pays-basque-aupa), licence Ouverte 2.0, mise à jour le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/20/gbfs/3.0/gbfs.json` : 8 stations, toutes avec coordonnées et capacité. Sept dans la CA (Bayonne 3, Anglet 2, Biarritz 2). Une à Tarnos, hors CA (EPCI 244000659). Capture `G1_paysbasque_2026-10-20.png`.
- G2. Passe. CA du Pays Basque, 200067106. [Comparateur](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200067106).
- G5. Échoue. 329 856 habitants, dans la fourchette, mais densité 111,1 hab/km², soit environ 2 969 km². Jugement : le graphe piéton de toute la CA n'est pas tenable en local dans le temps du hackathon. Ce jugement n'est pas une mesure du graphe. G6, G3 et G4 ne sont pas ouvertes. Pas de score.

**Nantes Métropole — portes passées, score 90.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-nantes), licence Ouverte 2.0, mise à jour le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/15/gbfs/v3.0/gbfs.json` : 23 stations, toutes avec coordonnées et capacité. Communes : Nantes 20, Orvault 2, Rezé 1. Capture `G1_nantes_2026-10-20.png`.
- G2. Passe. Nantes Métropole, 244400404, 24 communes. [Comparateur](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-244400404).
- G5. Passe. 689 456 habitants, sous le plafond de 700 000. Densité 1 317,4, soit environ 523 km². Proche du plafond : S6 = 1.
- G6. Passe, provisoire. 23/23.
- G3. Passe. [GTFS Naolib](https://www.data.gouv.fr/datasets/arrets-horaires-et-circuits-des-transports-en-commun-naolib-de-nantes-metropole-au-format-gtfs), licence ODbL, fiche mise à jour le 2026-10-16. L'enregistrement consulté pointe vers `gtfs_lumidata_id.zip`, validité affichée du 2026-10-19 au 2027-01-19. Archive non ouverte.
- G4. Même constat Filosofi 2021.
- Notes. S4 = 2 : [vélos Naolib](https://www.data.gouv.fr/datasets/offre-et-temps-reel-du-service-velos-en-libre-service-naolib-de-nantes-metropole-au-format-gbfs), `https://api.cyclocity.fr/contracts/nantes/gbfs/v3/gbfs.json`, `station_information` présent, `last_updated` le 2026-10-20. Score = (40+20+30+20+30+20+20) / 2 = 90.

**Métropole de Lyon — écartée à G5.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-metropole-de-lyon), licence Ouverte 2.0, mise à jour le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/3/gbfs/3.0/gbfs.json` : 200 stations, toutes avec coordonnées et capacité. Le repérage communal les place dans la métropole, dont 148 à Lyon et 22 à Villeurbanne. Capture `G1_lyon_2026-10-20.png`.
- G2. Passe. Métropole de Lyon, 200046977. [Comparateur](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200046977).
- G5. Échoue. 1 436 354 habitants en 2023, au-dessus de 700 000. Densité 2 691,4, soit environ 534 km². Aucun découpage n'est proposé. G6, G3 et G4 ne sont pas ouvertes. Pas de score.

**Rennes Métropole — portes passées, score 90.**

- G1. Passe. [Fiche](https://www.data.gouv.fr/datasets/citiz-autopartage-rennes-metropole), licence Ouverte 2.0, mise à jour le 2026-10-20. Flux `https://backend.citiz.fr/public/provider/19/gbfs/v3.0/gbfs.json` : 66 stations, toutes avec coordonnées et capacité. Communes : Rennes 58, Saint-Jacques-de-la-Lande 3, Cesson-Sévigné 2, Chantepie 1, Saint-Grégoire 1, Saint-Erblon 1. Capture `G1_rennes_2026-10-20.png`.
- G2. Passe. Rennes Métropole, 243500139, 43 communes. [Comparateur](https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-243500139).
- G5. Passe. 480 178 habitants, densité 681,1, soit environ 705 km². S6 = 1.
- G6. Passe, provisoire. 66/66.
- G3. Passe. [GTFS STAR bus et métro](https://www.data.gouv.fr/datasets/versions-des-horaires-theoriques-des-lignes-de-bus-et-de-metro-du-reseau-star-dans-les-formats-gtfs-et-netex-ainsi-que-les-urls-dacces-au-gtfs-rt), ressource « GTFS (Version en cours) », licence ODbL. La date de la fiche catalogue est ancienne (2014-12-03) ; l'archive n'a pas été ouverte.
- G4. Même constat Filosofi 2021.
- Notes. S4 = 2 : [Vélo STAR GBFS](https://www.data.gouv.fr/datasets/velo-en-libre-service-du-star-au-standard-gbfs), `station_information` présent, flux répondu le 2026-10-20. La fiche catalogue date de 2019. Score = 90.

---

## 7. Décision

| Champ | Valeur |
|---|---|
| Territoire retenu | **CA de La Rochelle** (241700434) |
| Date | 20 octobre 2026 |
| Score | 87,5 / 100 |
| Deuxième | Nantes Métropole et Rennes Métropole, 90 / 100, meilleur score de la grille. Nantes est la plus petite des deux (environ 523 km² contre 705). |
| Raison du choix | Le meilleur score est 90. La Rochelle est à 87,5, donc dans la bande des 5 points, avec la plus petite superficie (environ 327 km²). Angers et Grand Poitiers sont à 85, eux aussi dans la bande, mais plus étendus. |
| Jeux écartés et pourquoi | Lyon : 1 436 354 habitants, porte G5. Pays Basque : environ 2 969 km², porte G5. Angers (environ 667 km²) et Grand Poitiers (environ 1 065 km²) : portes passées, écart de 5 points avec le meilleur score, écartés par la superficie. |
| Décisions géospatiales | Le territoire est décidé. Le rattachement des stations au contour reste provisoire jusqu'à E3 : si moins de 80 % des stations tombent dans le contour Admin Express, la décision est rouverte. La structure `data/` est créée vide ; aucun fichier de données n'y est déposé. |

---

## 8. Périmètre de secours

Secours : Nantes Métropole (90/100, environ 523 km²), désigné par la même règle (bande de 5 points, plus petite superficie après La Rochelle).

| Déclencheur de bascule | Vérifié à |
|---|---|
| Moins de 80 % des stations Citiz dans le contour Admin Express | E3 |
| Archive GTFS Yélo inexploitable (arrêts sans coordonnées, réseau incomplet) : S3 = 0, score 80, écart de 10 avec Nantes | E2 |
| Carroyage Filosofi absent ou lacunaire sur le périmètre | E2 |
| Graphe piéton non calculable en local | E3 |

Date limite de bascule : fin de E3. Après E3, on ne change plus de territoire, on documente la limite.

Point de vigilance sur le secours : Nantes est proche du plafond G5 (689 456 habitants).

---

## 9. Verrouillage

Statut : verrouillé le 21/10/2026. Preuve : [`verrouillage_2026-10-21.json`](annexes/selection_territoire/verrouillage_2026-10-21.json), run `20261021T035827Z_aabf711`.

| # | Vérification | Constat attendu | Résultat au 21/10/2026 | Étape |
|---|---|---|---|---|
| V-a | Ouvrir l'archive GTFS Yélo | stops.txt avec coordonnées, routes et trips présents, calendrier valide à la date de démo | Passée si la démonstration a lieu au plus tard le 03/01/2027. Archive complète : fichiers obligatoires, `shapes`, `feed_info`, 1 515 arrêts avec coordonnées, validité du 08/10/2026 au 03/01/2027. | E2 |
| V-b | Filosofi 200 m | carreaux présents sur les 28 communes, part des carreaux sous secret statistique notée | Passée. Les 28 codes 2026 sont dans `lcog_geo` 2021, aucun carreau hors contour. 2 637 carreaux, `idcar_200m` unique. Population Filosofi 2021 : 174 016, rapport 0,954 à la population légale 2023 (182 435). | E2 |
| V-c | Contour Admin Express de l'EPCI 241700434 | ≥ 80 % des 24 stations Citiz dedans | Passée. 24/24 stations dans le contour (100 %, seuil 80 %). | E3 |
| V-d | Graphe piéton OSM de l'EPCI | téléchargé et calculé en local, nombre de nœuds noté | Passée. 29 865 nœuds, 84 010 arêtes, 136 composantes. 98,29 % des nœuds sont dans la composante principale. Une distance réseau de 400 m a été calculée. | E3 |

Constat V-a du 21/10 : S3 passerait à 2 (95/100). Décision du 20/10 inchangée.

Limite Q8, à présenter au jury. Sur l'EPCI, 41,9 % des carreaux ont une valeur imputée (`i_est_200 = 1`), mais ils ne portent que 6,3 % de la population. C'est une limite de la diffusion Filosofi, pas un défaut du rattachement. Le constat départemental du même jour était plus haut : 78 % des carreaux de la Charente-Maritime. Une population imputée non entière ne s'affiche pas avec ses décimales comme un nombre d'habitants.

Le déclencheur « archive GTFS inexploitable » du §8 ne s'applique pas. Le seul cas encore ouvert sur ce flux est une finale nationale après le 03/01/2027 (R23) : il faudrait alors retélécharger S02 dans un nouveau dossier daté.

---

## 10. Risques liés au territoire

Résumé ; le détail est dans [`suivi_risques.md`](suivi_risques.md).

- R16 : périmètre trop grand pour le graphe piéton → La Rochelle, la plus compacte des 7
- R17 : 24 stations Citiz seulement → H6 option A (multi-territoires)
- R18 : vélo Yélo figé au 17/06/2026 → positions seulement, date affichée
- R19 : clos le 21/10/2026, V-a passée
- R23 : validité GTFS Yélo jusqu'au 03/01/2027 → nouveau téléchargement de S02 si une finale nationale a lieu après cette date
- R20 : territoire de taille moyenne, donc un impact en valeur absolue plus faible qu'une grande métropole → présenter aussi des ratios (coût par habitant, % de couverture), pas seulement des volumes
