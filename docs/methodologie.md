# Méthodologie

**Statut :** à compléter à E5–E9.

Plan : accessibilité 5 min, KPI, candidats, K6, H6, optimisation.

## Règles de nettoyage

### RC-01 — Arêtes non piétonnes

Règle : retirer les arêtes `motorroad=yes` sans tag `foot` explicite.

Origine : test sur Lyon 2e (hors périmètre du projet).

À constater sur La Rochelle à E3 : nombre d'arêtes retirées, nombre de composantes avant / après (Q7).

## Indicateurs de qualité

### Q8 — Carreaux imputés (secret statistique)

Définition : part des carreaux de l'EPCI avec `i_est_200 = 1` (valeurs imputées en dessous de 11 ménages fiscaux, selon S03d).

Mesure aussi : part de la population de l'EPCI dans ces carreaux.

Usage : afficher en page 5 ; ne jamais présenter un carreau imputé comme une observation individuelle (vie privée, R10).
