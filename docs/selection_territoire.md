# Sélection du territoire

**Statut :** méthode et grille proposées. **Aucun territoire n'est retenu.**
**Date du repérage catalogue :** 20 octobre 2026.
**Ce document autorise :** comparer des périmètres sur pièces.
**Ce document n'autorise pas :** télécharger un GTFS, un carroyage ou un graphe piéton, nettoyer des données, modéliser, ou ouvrir Power BI.

Tant que la grille n'est pas remplie et qu'une ligne « Décision » n'est pas écrite en bas de ce fichier, toutes les décisions géospatiales restent provisoires. Lyon 2e reste au plus un essai technique ultérieur, pas un territoire d'étude.

---

## 1. Décision à prendre

Retenir **un seul périmètre d'étude**, assez limité pour un traitement Python local, avec un flux GBFS Citiz exploitable, un réseau de transport public ouvert, une population carroyée et un intérêt métier (Citiz déjà présent, zones encore à couvrir).

Le périmètre d'étude est un **EPCI ou une métropole**, pas la France, pas une région, pas le fichier régional Citiz pris en bloc.

---

## 2. Méthode

Quatre temps, dans cet ordre. On s'arrête au premier échec.

1. **Vivier.** Partir des jeux « Autopartage Citiz » au format GBFS sur le point d'accès national : [catalogue GBFS](https://transport.data.gouv.fr/datasets?format=gbfs&locale=fr&order_by=alpha). Une source publique équivalente est acceptable si l'URL, la date et la licence sont notées. Compléter la liste si le catalogue est paginé : le repérage ci-dessous n'est pas certifié exhaustif.
2. **Périmètre.** Pour chaque jeu, nommer le périmètre que l'on accepterait de traiter. Si le jeu couvre une région ou plusieurs villes éloignées, le territoire candidat est **une** intercommunalité à l'intérieur du jeu, pas le jeu entier.
3. **Portes.** Un candidat qui échoue une porte est écarté. On ne le note pas.
4. **Note.** Les candidats qui passent toutes les portes sont notés. Le meilleur score est proposé. En cas d'écart de 5 points ou moins, retenir le périmètre le plus petit.

La décision n'est valide que lorsque chaque case « Preuve » contient une URL, une date de consultation et le constat (nombre de stations, nom du GTFS, millésime de population). Une case vide vaut un échec.

---

## 3. Portes éliminatoires

Toutes sont obligatoires.

| ID | Porte | Passage | Preuve à coller |
|---|---|---|---|
| G1 | Flux GBFS Citiz exploitable | La fiche existe, la ressource GBFS répond, `station_information` contient au moins une station avec latitude et longitude **dans le périmètre proposé**. La licence autorise la réutilisation. | URL de la fiche, URL du flux, date, nombre de stations dans le périmètre, licence |
| G2 | Périmètre local | Le périmètre est un EPCI ou une métropole. Un jeu régional n'est pas un territoire d'étude. | Nom officiel du périmètre et son contour (source Admin Express ou équivalent, à citer) |
| G3 | Transport public ouvert | Au moins un GTFS du réseau structurant couvre ce périmètre, avec arrêts géolocalisés, sur transport.data.gouv.fr ou une source publique équivalente. | URL, date, nom du réseau |
| G4 | Population | Un carroyage de population à 200 m (Filosofi ou équivalent INSEE) couvre le périmètre. | URL, millésime |
| G5 | Faisabilité Python | Le graphe piéton OSM du périmètre est téléchargeable et calculable en local dans le temps du hackathon. Hypothèse de travail, non mesurée : viser environ 100 000 à 700 000 habitants. En dessous, l'arbitrage budgétaire est faible. Au-dessus, il faut une raison écrite ou un découpage. | Population et superficie sourcées, jugement explicite sur la taille du graphe |
| G6 | Intérêt métier | Des stations Citiz sont dans le périmètre, et le périmètre n'est pas un ilôt trop petit pour discuter d'un budget (Lyon 2e est dans ce cas). | Stations G1 à l'intérieur du contour G2 |

`station_status` et `vehicle_status` décrivent un instantané. Ils ne servent pas à juger l'offre structurelle et ne font pas passer G1.

---

## 4. Grille de note

Appliquée seulement si G1 à G6 sont passées. Chaque critère vaut 0, 1 ou 2. Score = somme (note × poids) / 2, sur 100.

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

## 5. Vivier repéré, non noté

Repérage du catalogue GBFS au 20 octobre 2026. **Une ligne ci-dessous n'est pas un territoire validé.** L'exploitabilité (G1, G3, G4, G5) n'a pas été testée. Les URL ne sont citées que lorsqu'elles ont été lues ; les autres titres renvoient au catalogue.

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

## 6. Grille à remplir

Laisser vide ce qui n'a pas été ouvert. Ne pas deviner un nombre de stations, une population ou un score.

| Critère | Angers Loire Métropole | Grand Poitiers | La Rochelle | Pays Basque AUPA | Nantes Métropole | Métropole de Lyon | Rennes Métropole |
|---|---|---|---|---|---|---|---|
| G1 Flux Citiz | | | | | | | |
| G2 Périmètre local | | | | | | | |
| G3 GTFS | | | | | | | |
| G4 Population 200 m | | | | | | | |
| G5 Taille Python | | | | | | | |
| G6 Intérêt métier | | | | | | | |
| Portes | non vérifié | non vérifié | non vérifié | non vérifié | non vérifié | non vérifié | non vérifié |
| S1 ×20 | | | | | | | |
| S2 ×10 | | | | | | | |
| S3 ×15 | | | | | | | |
| S4 ×10 | | | | | | | |
| S5 ×15 | | | | | | | |
| S6 ×20 | | | | | | | |
| S7 ×10 | | | | | | | |
| Score /100 | | | | | | | |

---

## 7. Décision

| Champ | Valeur |
|---|---|
| Territoire retenu | **non choisi** |
| Date | |
| Score | |
| Deuxième | |
| Raison du choix | |
| Jeux écartés et pourquoi | |
| Décisions géospatiales | provisoires |
