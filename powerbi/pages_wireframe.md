# Maquettes textuelles des pages

**Statut :** conception, Mission 13 (21/10/2026). Canevas 1280 × 720. Les identifiants V*x.y* renvoient à `conception_rapport.md`. Chaque page a la même barre du haut.

```text
BARRE COMMUNE (hauteur 48 px)
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [1 Synthèse] [2 Couverture] [3 Candidats] [4 Budget] [5 Méthode]      Données au 21/10/2026 │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

## Page 1 — Executive overview

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ BARRE COMMUNE                                                                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ TITRE : « 10 stations Citiz doublent la couverture de l'agglomération pour 85 000 € »    │
├─────────────────────┬─────────────────────┬─────────────────────┬────────────────────────┤
│ V1.1 Couverture     │ V1.2 Sans aucune    │ V1.3 Nouvellement   │ V1.4 Coût par habitant │
│ Citiz aujourd'hui   │ option à 5 min      │ couverts            │ gagné                  │
│      9,8 %          │     38 672 hab.     │  +18 816 hab.       │     4,52 €             │
│                     │                     │  9,8 % → 20,6 %     │  hypothèse de simul.   │
├─────────────────────┴─────────────────────────────────────────┬────────────────────────┤
│ V1.5 CARTE                                                    │ V1.6 TOP STATIONS      │
│  ● bleu  stations Citiz existantes                           │ # Commune  +hab cumul  │
│  ● vert  stations proposées (taille = habitants gagnés)      │ 1 …        4 040  …    │
│  ┅ violet contour des communes prioritaires                  │ 2 …                    │
│                                                               │ … (10 lignes)          │
│                                                               ├────────────────────────┤
│                                                               │ V1.7 EFFICACITÉ /      │
│                                                               │ ÉQUITÉ (même budget)   │
│                                                               │ 18 816  vs  14 446 hab │
│                                                               │ prioritaires 0 → 4 674 │
├───────────────────────────────────────────────────────────────┴────────────────────────┤
│ V1.8 « Moins d'un habitant sur dix a Citiz à 5 min. 10 stations doublent ce chiffre.     │
│        Imposer 30 % des gains aux communes peu desservies coûte un quart de l'impact. »  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

## Page 2 — Couverture actuelle

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ BARRE COMMUNE                                                                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ TITRE : « 22 % des habitants n'ont aucune option de mobilité à 5 minutes à pied »        │
│ Segment mode : [Tous modes] [Bus] [Citiz] [Vélo]          Segment commune : [▼ Toutes]   │
├─────────────────────┬─────────────────────┬─────────────────────┬────────────────────────┤
│ V2.1 Taux couverture│ V2.2 Desservis      │ V2.3 Non desservis  │ V2.4 Options / hab.    │
├─────────────────────┴───────────────────────────┬─────────────┴────────────────────────┤
│ V2.5 CARTE DES CARREAUX                         │ V2.8 COUVERTURE PAR COMMUNE (triée)   │
│  ● bleu desservi   ● vermillon non desservi     │ ████████████████ 98 %                  │
│  (taille = population du carreau)               │ ██████████       61 %                  │
│                                                 │ ┊ seuil 60 %                           │
│                                                 │ ███████          35 %  prioritaire     │
├────────────────────────┬────────────────────────┼────────────────────────────────────────┤
│ V2.7 HABITANTS PAR     │ V2.9 COUVERTURE PAR    │ V2.10 COMMUNES SOUS-DESSERVIES         │
│ NOMBRE D'OPTIONS       │ QUINTILE DE NIVEAU DE  │ Commune  Pop  Non desservis  Taux      │
│ 0 | 1-2 | 3-5 | 6+     │ VIE (1 = modeste)      │ (9 lignes)                              │
└────────────────────────┴────────────────────────┴────────────────────────────────────────┘
```

## Page 3 — Zones candidates et score de potentiel

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ BARRE COMMUNE                                                                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ TITRE : « 2 200 sites possibles, classés par un score de potentiel (pas une prédiction) »│
│ Segments : [▼ Commune]  [Prioritaire ☐]  Score [====|-------] 0–100                      │
├───────────────────────┬───────────────────────┬──────────────────────────────────────────┤
│ V3.1 Candidats retenus│ V3.2 Score du site    │ V3.3 Habitants gagnés (site seul)       │
├───────────────────────┴───────────────────────┼──────────────────────────────────────────┤
│ V3.4 CARTE DES CANDIDATS                      │ V3.5 TOP 20 : POURQUOI CE SCORE ?        │
│  bleus clair → foncé = classe de score        │ ███▓▓▒▒░░ impact|besoin|bus|logt|ménages│
│  (taille = habitants gagnés, site seul)       │ ███▓▓▒░░                                 │
│  info-bulle : page « Candidat »               │ …                                        │
├───────────────────────────────────────────────┼──────────────────────────────────────────┤
│ V3.6 IMPACT / REDONDANCE                      │ V3.7 TABLEAU DES SITES  │ V3.8 SENSIBILITÉ│
│ Y habitants gagnés ↑   X redondance →         │ rang commune score …    │ variable ×0,5   │
│ (en haut à gauche = meilleurs sites)          │                          │ Spearman, top N │
└───────────────────────────────────────────────┴──────────────────────────┴─────────────────┘
```

## Page 4 — Optimisation budgétaire

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ BARRE COMMUNE                                                                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ V4.0 TITRE DYNAMIQUE : « Central, coût central, efficacité : 10 stations, 18 816 hab. »  │
│ Budget [42 500] [85 000] [170 000]   Coût/station [4 000] [8 500] [13 000]               │
│ Variante [Efficacité] [Équité]   (message si combinaison absente)                        │
├─────────────────────┬─────────────────────┬─────────────────────┬────────────────────────┤
│ V4.1 Stations       │ V4.2 Nouvellement   │ V4.3 Coût par hab.  │ V4.4 Part des gains en │
│                     │ couverts            │ + étiquette         │ communes prioritaires  │
├─────────────────────┴───────────────────────────┬─────────────┴────────────────────────┤
│ V4.5 CARTE DU PORTEFEUILLE                      │ V4.9 PORTEFEUILLE (ordre d'ajout)      │
│                                                 │ # Commune Score Coût cumul +hab cumul  │
│                                                 ├────────────────────────────────────────┤
│                                                 │ V4.10 ESCALIER : habitants cumulés     │
├────────────────────────┬────────────────────────┼────────────────────────────────────────┤
│ V4.6 BUDGET → IMPACT   │ V4.7 12 SCÉNARIOS      │ V4.8 PRIX DE L'ÉQUITÉ (coût central)   │
│ (1 à 30 stations,      │ coût ↔ habitants       │ ▇▅ prudent  ▇▅ central  ▇▅ ambitieux    │
│ rendements décroiss.)  │ ● efficacité ● équité  │ bleu efficacité / rose équité          │
└────────────────────────┴────────────────────────┴────────────────────────────────────────┘
```

## Page 5 — Méthodologie, qualité, limites et risques

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ BARRE COMMUNE                                                                            │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ TITRE : « Des chiffres traçables : 40 contrôles conformes, 3 alertes connues »            │
├─────────────────────┬─────────────────────┬─────────────────────┬────────────────────────┤
│ V5.1 Conformes      │ V5.2 En alerte      │ V5.3 Dernière exéc. │ V5.10 Contrôles = 0 ✓  │
├─────────────────────┴─────────────────────┴─────────────────────┴────────────────────────┤
│ V5.4 PIPELINE : Sources → Bronze → Silver → Gold → Power BI (image)                      │
├──────────────────────────────────────────┬───────────────────────────────────────────────┤
│ V5.5 QUALITÉ PAR DIMENSION × STATUT      │ V5.6 ALERTES (3) : indicateur, valeur, seuil  │
│ Segment famille : [qualité][données][mob]│                                               │
├──────────────────────────────────────────┼───────────────────────────────────────────────┤
│ V5.7 SOURCES : id, producteur, licence,  │ V5.8 HYPOTHÈSES ● certain ◐ estimé ○ hypothèse│
│ date                                     ├───────────────────────────────────────────────┤
│                                          │ V5.9 RISQUES OUVERTS ET LIMITES               │
└──────────────────────────────────────────┴───────────────────────────────────────────────┘
```

## Page info-bulle « Candidat » (masquée, 320 × 240)

```text
┌──────────────────────────────┐
│ Site C_… · Commune …         │
│ Score …/100 · rang …         │
│ impact      ████████         │
│ besoin      █████            │
│ bus         ███              │
│ logement    ██               │
│ ménages     ██               │
│ Habitants gagnés (seul) …    │
└──────────────────────────────┘
```
