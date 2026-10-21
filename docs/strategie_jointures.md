# Stratégie de jointures spatiales

**Statut :** mise en œuvre le 21/10/2026 sur la CA de La Rochelle (EPCI 241700434). Les chiffres sont ceux constatés à l'exécution ; ils sont recalculés et tracés dans les manifestes Silver et Gold.
**Hors périmètre de ce document :** KPI finaux (K1 à K13) et optimisation.

Principe : on joint d'abord **par attribut** quand la source fournit la clé (codes INSEE, SIREN), et **par géométrie** seulement quand aucune clé n'existe. Chaque jointure géométrique est doublée d'un contrôle.

---

## 1. Jointures, dans l'ordre

| # | Jointure | Entrées | Clé ou règle | Méthode | Sortie | Contrôle |
|---|---|---|---|---|---|---|
| J0 | Commune → EPCI | couche `commune` (S04) | SIREN extraits de `codes_siren_des_epci` (motif 9 chiffres) | Attribut | `admin_communes_5epci` | RC-12 / CS-09 : couche commune = couche epci = grille G2 (28) |
| J0b | Commune → département, région | couche `commune` (S04) | `code_insee_du_departement`, `code_insee_de_la_region` | Attribut | `admin_communes_5epci` | Aucune commune sans code |
| J1 | Carreau → commune (RF-01) | Filosofi (S03), communes J0 | `lcog_geo` (codes 2021, virgule) ∩ communes de l'EPCI ; commune = premier code membre | Attribut | `filosofi_carreaux_5epci` | Aucun code 2026 absent des codes 2021 (V-b) ; aucune commune sans carreau (Q6) |
| J2 | Carreau → EPCI, département, région | J1 + J0/J0b | `commune_insee` | Attribut | `cellules_larochelle` | Aucun carreau sans département (arrêt sinon) |
| J2b | Contrôle géométrique de J1 | centroïdes, polygones communes | centroïde **dans** commune | Géométrie (contrôle seulement) | `centroide_dans_commune`, `commune_centroide` | Taux de concordance (constaté 97,69 %) |
| J3 | Option → réseau | offres (S02, S01, S08), nœuds routables (S05) | Nœud routable le plus proche | Géométrie, déterministe | `offre_points_larochelle.node_id`, `dist_snap_m` | Distances médiane / max par mode ; RG-08 |
| J4 | Option → commune, EPCI, département, région | J3, communes J0 | Point **dans** polygone | Géométrie | `offre_points_larochelle` | Taux de jointure (99,86 %) ; une option dans deux communes → arrêt |
| J5 | Option → emprise | J3, contour EPCI + tampon S05 | Point dans emprise | Géométrie | `dans_emprise` (RG-05) | 0 option hors emprise |
| J6 | Carreau → réseau | centroïdes, nœuds routables | Nœud routable le plus proche | Géométrie, déterministe | `cellules_larochelle.node_id`, `dist_snap_m` | RG-08 (7 carreaux, 26 habitants) |
| J7 | Carreau × option | J3, J6, arêtes routables | Accès carreau + plus court chemin + accès option ≤ 400 m | Réseau (Dijkstra borné depuis chaque option) | `gold/accessibility/paires_cellule_offre_larochelle` | J-03 à J-06 (section 7) |
| J8 | Candidat × carreau (E7) | candidats, J6 | Même règle que J7, en partant du nœud du candidat | Réseau | `paires_candidat_cellule_larochelle` | Mêmes contrôles ; à écrire à E7 |

---

## 2. Équipements → unités administratives (J3 à J5)

1. Les trois offres Silver (bus 534, Citiz 24, vélo 136) sont réunies sans fusion entre modes (`offre_id` unique, arrêt sinon).
2. Chaque option est placée dans la commune qui la **contient** (communes de l'EPCI d'étude). Un point sur une limite exacte de deux communes ou un recouvrement de polygones produirait deux lignes : le script s'arrête.
3. Une option du tampon, hors EPCI, garde des codes vides et `hors_epci = vrai`. Elle reste une option : un habitant de bordure peut l'utiliser. Constaté : 1 arrêt de bus sur 694 options.
4. Département et région viennent de la commune, jamais d'une seconde jointure géométrique.

## 3. Carreaux → unités administratives (J1, J2, J2b)

1. La commune d'un carreau est **attributaire** (RF-01) : `lcog_geo` liste les communes du carreau, triées par surface d'intersection décroissante. On retient la première qui appartient à l'EPCI d'étude.
2. Le carreau n'est jamais découpé : sa population compte **une seule fois**, dans une seule commune. `multi_commune` et `partiel_epci` signalent les carreaux de limite.
3. EPCI, département et région suivent la commune (J2).
4. Contrôle géométrique : on vérifie que le centroïde tombe dans la commune attribuée. Constaté : 2 576 / 2 637 (97,69 %). Les écarts sont des carreaux de limite (45 centroïdes hors EPCI). L'attribut reste la référence, puisque l'INSEE le calcule sur la surface et non sur le centroïde.

## 4. Relations carreau × équipement (J7)

- **Règle :** `dist_acces_cellule_m + dist_reseau_m + dist_acces_option_m ≤ 400 m` (H2 : 5 min). Les deux accès sont à vol d'oiseau ; c'est une limite assumée.
- **Réseau :** arêtes non exclues (sans `busway`, RC-15), non orienté (la marche se fait dans les deux sens), longueur `length_m`, plus grande composante.
- **Calcul :** un plus court chemin borné par option (694 calculs), puis lecture des carreaux rattachés aux nœuds atteints. Environ 3 secondes.
- **Table :** une ligne par (carreau, option, méthode, variante), avec les trois distances. Aucune agrégation : les KPI viendront de cette table.
- **Variantes :** `reseau/reference` ; `reseau/sans_trunk` (sensibilité RC-01, option B) ; `vol_oiseau/reference` (repli, section 5).

## 5. Repli MVP sans réseau réel

Si le graphe n'est pas disponible (ou pour les villes d'apprentissage H6, qui n'ont pas de graphe) : paires **à vol d'oiseau**, centroïde du carreau → point de l'option ≤ 400 m, même schéma de table (`methode = vol_oiseau`).

Ce repli **surestime** l'accès. Constaté à La Rochelle, sur les mêmes données :

| Méthode | Paires | Carreaux atteignant au moins une option |
|---|---:|---:|
| Réseau (référence) | 3 016 | 1 463 |
| Vol d'oiseau | 6 918 | 2 096 |

Le détour médian réseau / vol d'oiseau vaut **1,40**. Toutes les paires réseau sont aussi trouvées à vol d'oiseau (contrôle de cohérence). Conséquence : le vol d'oiseau n'est utilisé que pour les variables H6 (calculées de la même façon dans toutes les villes), jamais pour les KPI de La Rochelle.

## 6. Sensibilité RC-01 (option B)

Sans les 184 arêtes `trunk` signalées : **1 paire perdue sur 3 016 (0,03 %)**, **1 carreau** perd toute option. L'écart est négligeable : la limite RC-01 est mesurée, et la réingestion de S05 n'est pas nécessaire. Les KPI utiliseront la variante `reference`.

## 7. Contrôles de cohérence et taux de jointure

| ID | Contrôle | Où | Constaté |
|---|---|---|---|
| J-01 | Options rattachées à une commune de l'EPCI | spatial | 99,86 % (693 / 694) |
| J-02 | Centroïde dans la commune attribuée ; centroïdes hors EPCI | spatial | 97,69 % ; 45 |
| J-03 | Aucune paire au-delà du budget | paires | arrêt sinon |
| J-04 | Aucun identifiant de paire inconnu des tables Silver | paires | arrêt sinon |
| J-05 | Paires, carreaux et options atteints, par méthode et variante | paires | section 5 |
| J-06 | Paires réseau retrouvées à vol d'oiseau ; détour médian | paires | 100 % ; 1,40 |
| CS-03 | Clés uniques (`cell_id`, `offre_id`, quadruplet de paire) | toutes | arrêt sinon |
| CS-04 | EPSG:2154 pour toute table géométrique | toutes | arrêt sinon |
| RG-08 | Rattachement > 400 m | spatial | 7 carreaux (26 habitants) |

## 8. Risques géographiques

| Risque | Mesure en place |
|---|---|
| **CRS** mélangés (WGS84, Lambert-93, LAEA de l'INSEE) | Tout est en EPSG:2154 dès `cleaned/` ; CS-04 bloque ; le rattachement refuse un autre CRS ; distances jamais en degrés |
| **Frontières** (carreaux et options à cheval) | Commune par attribut RF-01, carreau jamais découpé ; tampon de 500 m pour le réseau et les options ; `partiel_epci`, `hors_epci` |
| **Géométries invalides** | RC-11 : réparation signalée, géométrie vide rejetée ; constaté : 0 |
| **Doubles comptes de population** | Population portée par le carreau (une ligne, une commune) ; les paires ne portent pas de population ; K5 (population par option) sera documenté comme non exclusif |
| **Recouvrements de polygones** | Une option dans deux communes arrête le script (J4) |
| **Écart attribut / géométrie** | Mesuré (J-02), attribut gardé comme référence |
| **Réseau incomplet** (tags absents, busway) | RC-01 mesuré (section 6), RC-15 exclut les busway, plus grande composante seulement |
| **Accès à vol d'oiseau** | Inclus dans le budget de 400 m ; limite écrite ; détour mesuré |
