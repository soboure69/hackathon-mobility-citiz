# Mesures DAX

**Statut :** conception, Mission 13 (21/10/2026). Mesures à créer dans une table vide `_Mesures`, rangées par dossier d'affichage. Noms de tables = `pbi_*` sans préfixe (voir `dataset_schema/modele_donnees.md`).

Trois règles :
1. **Une mesure, une définition.** Les KPI viennent de Python ; DAX les sélectionne ou les agrège seulement quand l'agrégation est exacte (population d'une partition de carreaux).
2. **Jamais de somme non additive.** `pop_5min` d'une offre et `pop_nouvelle_isolee` d'un candidat ne s'additionnent pas (chevauchements). Les mesures correspondantes renvoient BLANK si plusieurs lignes sont en contexte.
3. **Un mode à la fois.** Les mesures de couverture renvoient BLANK si le segment « mode » n'a pas exactement une valeur.

Priorité : **P1** = indispensable à la soutenance ; **P2** = utile ; **P3** = contrôle (page 5, masqué ailleurs).

## 1. Couverture actuelle (dossier `Couverture`)

```dax
-- P1. Population Filosofi du périmètre filtré (communes, carreaux).
Population totale = SUM ( dim_cellule[pop] )

-- P1. Population à 5 min d'au moins une option du mode choisi.
Population desservie =
IF (
    HASONEVALUE ( dim_mode[mode] ),
    CALCULATE ( SUM ( fact_acces_mode[pop] ), fact_acces_mode[desservi] = TRUE () )
)

-- P1.
Population non desservie =
IF (
    HASONEVALUE ( dim_mode[mode] ),
    CALCULATE ( SUM ( fact_acces_mode[pop] ), fact_acces_mode[desservi] = FALSE () )
)

-- P1. Taux de couverture à 5 min (K2).
Taux de couverture =
DIVIDE ( [Population desservie], [Population desservie] + [Population non desservie] )

-- P1. Indépendant du segment mode : habitants sans aucune option (bus, Citiz, vélo).
Population sans aucune option =
CALCULATE ( SUM ( dim_cellule[pop] ), dim_cellule[desservi_tous] = FALSE () )

-- P2. Nombre moyen d'options accessibles par habitant (K4), pondéré par la population.
Options par habitant =
IF (
    HASONEVALUE ( dim_mode[mode] ),
    DIVIDE (
        SUMX ( fact_acces_mode, fact_acces_mode[pop] * fact_acces_mode[n_options] ),
        SUM ( fact_acces_mode[pop] )
    )
)

-- P2. Couverture Citiz, quel que soit le segment mode (cartes KPI page 1).
Taux de couverture Citiz =
CALCULATE ( [Taux de couverture], dim_mode[mode] = "citiz" )

Taux de couverture tous modes =
CALCULATE ( [Taux de couverture], dim_mode[mode] = "tous" )

-- P2. Communes prioritaires (couverture tous modes < 60 %).
Communes prioritaires =
CALCULATE ( COUNTROWS ( dim_commune ), dim_commune[prioritaire] = TRUE () )

-- P2. Équité de revenu : écart de couverture entre le 1er et le 5e quintile de niveau de vie.
Taux quintile =
DIVIDE ( SUM ( fact_equite_quintile[pop_desservie] ), SUM ( fact_equite_quintile[pop] ) )

Écart Q1 - Q5 (points) =
IF (
    HASONEVALUE ( dim_mode[mode] ),
    100 * (
        CALCULATE ( [Taux quintile], fact_equite_quintile[quintile] = "1" )
        - CALCULATE ( [Taux quintile], fact_equite_quintile[quintile] = "5" )
    )
)

-- P2. Population exclusive d'une offre : ne s'additionne pas sur plusieurs offres.
Population à 5 min (offre) =
IF ( HASONEVALUE ( dim_offre[offre_id] ), SELECTEDVALUE ( dim_offre[pop_5min] ) )
```

## 2. Candidats et score (dossier `Candidats`)

```dax
-- P1.
Candidats retenus =
CALCULATE ( COUNTROWS ( dim_candidat ), dim_candidat[retenu] = TRUE () )

-- P1. Score de potentiel (K10, sur 100) d'un seul candidat.
Score =
IF ( HASONEVALUE ( dim_candidat[candidat_id] ), SELECTEDVALUE ( dim_candidat[score] ) )

-- P1. Habitants nouvellement couverts si ce site était le seul ajouté. Non additif.
Habitants gagnés (site seul) =
IF ( HASONEVALUE ( dim_candidat[candidat_id] ), SELECTEDVALUE ( dim_candidat[pop_nouvelle_isolee] ) )

-- P2. Coût par habitant si ce site était seul, au coût central.
Coût par habitant (site seul) =
DIVIDE ( 8500, [Habitants gagnés (site seul)] )

-- P2. Redondance moyenne, pondérée par la population du rayon (K9).
Redondance moyenne =
DIVIDE (
    SUMX ( dim_candidat, dim_candidat[taux_redondance] * dim_candidat[pop_rayon] ),
    SUM ( dim_candidat[pop_rayon] )
)

-- P2. Stabilité du rang face aux pondérations (part des tirages où le site reste dans le top N).
Stabilité top N = AVERAGE ( dim_candidat[frequence_top_n] )

-- P1. Contribution d'un critère au score (barres empilées).
Contribution = SUM ( fact_contribution[contribution] )
```

`Coût par habitant (site seul)` écrit 8 500 en dur : c'est le coût central (D-2). Si la décision change, remplacer par `SELECTEDVALUE ( dim_scenario[cout_station] )` avec un segment de coût.

## 3. Scénarios (dossier `Scénario`)

```dax
-- P1. Libellé du scénario filtré (titres dynamiques).
Scénario choisi =
SELECTEDVALUE ( dim_scenario[libelle], "Choisir un budget, un coût et une variante" )

-- P1. K6 : habitants nouvellement couverts par Citiz, sans double compte.
Habitants nouvellement couverts = SELECTEDVALUE ( dim_scenario[k6] )

-- P1. K7 et K8.
Coût total = SELECTEDVALUE ( dim_scenario[k7] )
Coût par habitant = DIVIDE ( [Coût total], [Habitants nouvellement couverts] )

-- P1.
Stations financées = SELECTEDVALUE ( dim_scenario[n_stations] )
Budget = SELECTEDVALUE ( dim_scenario[budget] )
Budget non utilisé = [Budget] - [Coût total]

-- P1. Couverture avant / après et gain en points.
Couverture Citiz avant = SELECTEDVALUE ( dim_scenario[couverture_citiz_avant] )
Couverture Citiz après = SELECTEDVALUE ( dim_scenario[couverture_citiz_apres] )
Gain Citiz (points) = 100 * ( [Couverture Citiz après] - [Couverture Citiz avant] )
Couverture tous modes après = SELECTEDVALUE ( dim_scenario[couverture_tous_apres] )
Gain tous modes (points) =
100 * ( [Couverture tous modes après] - SELECTEDVALUE ( dim_scenario[couverture_tous_avant] ) )

-- P1. Équité (K12) et prix de l'équité.
Part des gains en communes prioritaires = SELECTEDVALUE ( dim_scenario[k12_part_prioritaire] )
Habitants gagnés en communes prioritaires = SELECTEDVALUE ( dim_scenario[pop_gagnee_prioritaire] )
Prix de l'équité (habitants) = SELECTEDVALUE ( dim_scenario[prix_equite_habitants] )
Prix de l'équité (%) = SELECTEDVALUE ( dim_scenario[prix_equite_part] )

-- P1. Scénario de référence (page 1), quel que soit le filtre.
Habitants nouvellement couverts (référence) =
CALCULATE ( MAX ( dim_scenario[k6] ), dim_scenario[est_reference] = TRUE (), REMOVEFILTERS ( dim_scenario ) )

Coût par habitant (référence) =
CALCULATE ( [Coût par habitant], dim_scenario[est_reference] = TRUE (), REMOVEFILTERS ( dim_scenario ) )

-- P2. Message si la combinaison choisie n'existe pas (équité calculée au coût central seulement).
Message scénario =
IF (
    ISBLANK ( [Habitants nouvellement couverts] ),
    "La variante équité n'est calculée qu'au coût central (8 500 €).",
    BLANK ()
)

-- P2. Titre dynamique de la page 4.
Titre page 4 =
[Scénario choisi] & " : " & FORMAT ( [Stations financées], "0" ) & " stations, "
    & FORMAT ( [Habitants nouvellement couverts], "#,##0" ) & " habitants nouvellement couverts"
```

## 4. Qualité et contrôles (dossier `Qualité`)

```dax
-- P1.
Indicateurs conformes = CALCULATE ( COUNTROWS ( fact_qualite ), fact_qualite[statut] = "ok" )
Indicateurs en alerte = CALCULATE ( COUNTROWS ( fact_qualite ), fact_qualite[statut] = "alerte" )
Part des indicateurs conformes =
DIVIDE ( [Indicateurs conformes], [Indicateurs conformes] + [Indicateurs en alerte] )

-- P2. Date de la dernière exécution du pipeline.
Dernière exécution = MAX ( meta_execution[date_execution_utc] )

-- P3. Recoupement Power BI / Python : doit valoir 0 au périmètre EPCI.
Écart couverture PBI - Python =
IF (
    HASONEVALUE ( dim_mode[mode] ) && NOT ISFILTERED ( dim_commune ),
    [Taux de couverture] - SELECTEDVALUE ( fact_kpi_territoire[taux_couverture] )
)

-- P3. Σ des carreaux gagnés = K6 : doit valoir 0 pour chaque scénario.
Écart K6 =
SUM ( fact_cellules_gagnees[pop] ) - [Habitants nouvellement couverts]

-- P3. Σ des gains marginaux = K6.
Écart gains marginaux =
SUM ( fact_selection[pop_nouvelle_marginale] ) - [Habitants nouvellement couverts]
```

## 5. Format

| Mesure | Format |
|---|---|
| Populations, habitants | `#,##0` (la virgule est le séparateur de milliers du format ; en culture fr-FR, il s'affiche comme une espace) |
| Taux, parts | Pourcentage, 1 décimale |
| Gains en points | `0,0" pt"` |
| Coûts | `#,##0 €` |
| Coût par habitant | `0,00 €` |
| Score | `0` (sur 100) |

Paramètre régional du fichier : français (France), pour la virgule décimale.
