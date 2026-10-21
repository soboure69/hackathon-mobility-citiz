# Optimisation budgétaire — formulation (à valider avant code)

**Statut :** formulation proposée le 21/10/2026. **Aucun code tant qu'elle n'est pas validée.** Les 5 décisions à trancher sont en section 13.
**Outil :** PuLP (déjà dans `requirements-lock.txt`, avec le solveur CBC). OR-Tools n'est pas nécessaire à cette taille.
**Entrées :** `gold/candidates/candidats_larochelle`, `gold/candidates/paires_candidat_cellule_larochelle`, `gold/accessibility/acces_cellule_larochelle`, `docs/registre_couts.md`.

## 1. Formulation métier

> Avec un budget donné, quelles stations Citiz ouvrir pour que **le plus grand nombre d'habitants gagnent un accès Citiz à moins de 5 minutes à pied**, sans compter deux fois le même habitant ?

La part minimale de gains dans les communes les moins desservies n'est pas dans le MVP (D-5). Elle vient en version enrichie, pour montrer le prix de l'équité.

- **Ce qu'on maximise :** des habitants **nouvellement couverts** (K6), pas un nombre de stations ni un score.
- **Pourquoi pas le score K10 :** il note un site **seul** ; deux sites voisins ont le même bon score, mais le second n'apporte presque rien. L'optimisation compte ce que chaque station **ajoute** (gain marginal).
- **Le score K10** sert seulement à départager deux solutions de même impact.

## 2. Formulation mathématique : couverture maximale sous budget

C'est un problème classique de localisation (« maximal covering location problem », Church et ReVelle, 1974), ici avec un budget au lieu d'un nombre fixe de stations.

**Ensembles et données**

| Symbole | Signification | Source |
|---|---|---|
| I | sites candidats retenus pour le type (Citiz : 2 200) | `candidats` (`retenu`) |
| J | carreaux **non desservis par Citiz aujourd'hui** | `acces_cellule` (`desservi_citiz` = faux) |
| N(j) ⊂ I | sites qui atteignent le carreau j à ≤ 400 m | `paires_candidat_cellule` |
| p_j | population du carreau j | `acces_cellule.pop` |
| c_i | coût du site i (type Citiz, hypothèse basse, centrale ou haute) | `registre_couts.md` |
| s_i | score K10 du site i, ramené dans [0, 1] | `candidats.score / 100` |
| B | budget du scénario | section 11 |
| P ⊂ J | carreaux des communes prioritaires (couverture < 60 %) | `kpi_couverture` |

## 3. Variables de décision

| Variable | Domaine | Sens |
|---|---|---|
| x_i | {0, 1} | 1 si l'on ouvre une station au site i |
| y_j | [0, 1] | 1 si le carreau j devient couvert (vaut 0 ou 1 à l'optimum) |

## 4. Fonction objectif

```text
max   Σ_{j ∈ J} p_j · y_j   +   ε · Σ_{i ∈ I} s_i · x_i
```

- Le premier terme est **K6 du portefeuille** : chaque carreau compte **une seule fois**, quel que soit le nombre de stations qui l'atteignent.
- Le second terme ne sert qu'à **départager** des solutions d'impact égal. ε est assez petit pour ne jamais échanger le plus petit carreau peuplé contre du score : ε < min(p_j > 0) / Σ s_i. La population Filosofi n'est pas entière, donc la borne n'est pas 1.

## 5. Contrainte de budget

```text
Σ_{i ∈ I} c_i · x_i  ≤  B
```

## 6. Contraintes possibles

| # | Contrainte | Écriture | MVP | Remarque |
|---|---|---|---|---|
| C-1 | **Couverture** (lien station → carreau) | y_j ≤ Σ_{i ∈ N(j)} x_i, pour tout j | ✅ | Le cœur du modèle : un carreau n'est couvert que si une station l'atteint |
| C-2 | **Budget** | Σ c_i x_i ≤ B | ✅ | — |
| C-3 | **Non-redondance** | Assurée par C-1 et par l'objectif (un carreau ne rapporte qu'une fois) ; plus l'exclusion à 80 % de redondance | ✅ (implicite) | Pas besoin de contrainte supplémentaire |
| C-4 | **Nombre maximum de stations** | Σ x_i ≤ N_max | ✅ (optionnelle) | Capacité de déploiement de Citiz (véhicules, équipes) |
| C-5 | **Équité** | Σ_{j ∈ P} p_j y_j ≥ α · Σ_{j ∈ J} p_j y_j | Version enrichie | Au moins α (par exemple 30 %) des habitants gagnés dans les communes prioritaires |
| C-6 | **Couverture territoriale** | Σ_{i ∈ I(c)} x_i ≥ 1, pour chaque commune prioritaire c retenue | Version enrichie | Au moins une station par commune prioritaire choisie |
| C-7 | **Distance minimale entre stations** | x_i + x_k ≤ 1 si d(i, k) < D_min | Version enrichie | Évite la concurrence entre deux stations ; C-1 évite déjà le double comptage. D_min à fixer (par exemple 400 m sur le réseau) |

## 7. Version MVP (rapide)

- **Type :** Citiz seul, le cœur du sujet.
- **Modèle :** C-1 + C-2 (+ C-4 si N_max est donné). Programme linéaire en nombres entiers PuLP / CBC. Environ 2 200 variables binaires, 2 400 variables continues et 10 000 liens : quelques secondes.
- **Courbe budget → impact :** même modèle résolu pour une grille de budgets (de 1 à 30 stations au coût central). On voit les **rendements décroissants**.
- **Contrôle croisé :** un **algorithme glouton** (on ajoute à chaque tour la station qui apporte le plus d'habitants nouveaux par euro). Il donne l'**ordre d'ajout**, facile à expliquer. L'optimum PuLP doit être ≥ au glouton (test).
- **Sorties :** tables de la section 10.

## 8. Version enrichie (si le temps le permet)

1. Contraintes C-5 (équité), C-6 (une station par commune prioritaire) et C-7 (distance minimale), avec un scénario « efficacité » contre un scénario « équité » : **le prix de l'équité** en habitants.
2. **Plusieurs types** (Citiz, vélo, bus) dans un même budget, avec des coûts par type. Objectif : habitants **sans aucune option** aujourd'hui qui en gagnent une, chaque carreau comptant une fois tous types confondus. Le bus reste indicatif (le coût de desserte n'est pas connu).
3. **Robustesse aux coûts :** solution évaluée sous les coûts bas et hauts ; ou contrainte de budget écrite sur le coût haut.
4. Bonus d'objectif pour le score H6 (E8) à la place de K10, s'il est validé.

## 9. Données nécessaires et hypothèses

| Donnée | Disponible | Remarque |
|---|---|---|
| Sites, exclusions, score | ✅ `candidats_larochelle` | 2 200 sites Citiz retenus |
| Zones atteintes | ✅ `paires_candidat_cellule_larochelle` | 10 435 liens site → carreau |
| Population et desserte actuelle | ✅ `acces_cellule_larochelle` | 156 932 habitants non desservis par Citiz |
| Communes prioritaires | ✅ `kpi_couverture_larochelle` | Couverture < 60 % |
| **Coûts** | ✅ `registre_couts.md` | Citiz 4 000 / 8 500 / 13 000 € sur 3 ans (étiquetés) |
| Budgets | ❌ **À décider** | Proposition en section 11 |
| Foncier, stationnement, accord municipal | ❌ Hors données | Validation après optimisation |

## 10. Sorties Gold attendues (`data/gold/optimization/`)

| Table | Clé | Contenu |
|---|---|---|
| `scenarios` | `scenario_id` | Budget, hypothèse de coût, contraintes actives, solveur, statut, valeur de l'objectif, écart d'optimalité, durée |
| `selection_scenario` | `scenario_id`, `candidat_id` | Stations retenues, coût et étiquette, **ordre d'ajout** (glouton), population nouvellement couverte **marginale**, cumuls |
| `kpi_scenario` | `scenario_id` | K6, K7 (coût total), **K8** (coût par habitant nouvellement couvert), nombre de stations, couverture Citiz avant / après, couverture tous modes avant / après, part des gains en communes prioritaires (K12) |
| `courbe_budget_impact` | `budget` | Budget → K6 optimal et K8, pour la courbe de rendements décroissants |
| `cellules_couvertes_scenario` | `scenario_id`, `cell_id` | Carreaux nouvellement couverts (carte « avant / après ») |

Contrôles prévus :

- budget respecté ;
- Σ des gains marginaux = K6 ;
- K6 ≤ population non desservie ;
- aucun carreau compté deux fois ;
- optimum ≥ glouton ;
- même entrée → même solution (CBC déterministe, graine fixée).

## 11. Trois scénarios

Les budgets sont des **hypothèses de simulation**, exprimées en stations « au coût central » pour rester lisibles.

| Scénario | Budget (3 ans) | Équivalent au coût central | Esprit |
|---|---:|---:|---|
| **Prudent** | 42 500 € | 5 stations | Premier test, quartiers les plus évidents |
| **Central** | 85 000 € | 10 stations | Plan de déploiement réaliste |
| **Ambitieux** | 170 000 € | 20 stations | Maillage de l'agglomération |

Chaque scénario est résolu avec les coûts **bas, central et haut**, soit 9 solutions. Cela montre combien l'incertitude sur les coûts change le résultat. En version enrichie, chaque scénario a une variante « équité » (C-5).

## 12. Expliquer le résultat au jury

> « Avec 85 000 € sur 3 ans, soit environ dix stations, notre outil choisit les emplacements qui donnent accès à Citiz au plus grand nombre de nouveaux habitants. Chaque habitant n'est compté qu'une fois : deux stations voisines ne rapportent pas deux fois. Le résultat : **N stations, X habitants gagnés, Y € par habitant**. La courbe montre qu'au-delà d'un certain budget, chaque station rapporte moins. Si l'on impose qu'une part des gains aille aux communes les moins desservies, on perd **Z habitants** : c'est le prix de l'équité, et c'est au décideur de le choisir. »

**Visuels :** carte avant / après, courbe budget → habitants gagnés, barres des stations dans l'ordre d'ajout (gain marginal décroissant), tableau des 3 scénarios avec K6, K7 et K8.

Les valeurs X, Y, Z et N seront **calculées**, jamais écrites à l'avance.

## 13. Décisions à valider avant de coder

| # | Décision | Proposition |
|---|---|---|
| D-1 | Objectif du MVP | Habitants nouvellement couverts **par Citiz** (A). Variante B, en version enrichie : habitants sans **aucune** option |
| D-2 | Base de coût | Coût pour la collectivité sur 3 ans, Citiz à 4 000 / 8 500 / 13 000 € |
| D-3 | Budgets | 42 500 / 85 000 / 170 000 € |
| D-4 | N_max | Aucun dans le MVP (le budget suffit) |
| D-5 | Équité dans le MVP | Non : montrée par une variante en version enrichie (C-5 avec α = 30 %) |
