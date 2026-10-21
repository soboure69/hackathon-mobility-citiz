# Application de restitution (Streamlit)

**Statut :** Mission 13, 21/10/2026. Décisions P-1 à P-6 validées ; **P-1 révisée : Streamlit remplace Power BI**, avec les mêmes pages, les mêmes tables et les mêmes règles (`powerbi/conception_rapport.md`).

## Lancer

```powershell
.\.venv\Scripts\python.exe scripts/build_exports.py --territoire larochelle   # contrôles X-01 à X-07
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py              # http://localhost:8501
```

## Fichiers

| Fichier | Rôle |
|---|---|
| `config/app.yaml` | Type affiché (Citiz, P-4), scénario de référence (P-3), hypothèses de la page 5 |
| `src/export/exports.py` | Construction des 22 tables d'export à partir de Gold (fonctions pures) |
| `src/export/mesures.py` | Mesures de l'application : équivalent Python des mesures DAX, testées |
| `scripts/build_exports.py` | Écrit `data/gold/exports/` + manifeste, contrôles X-01 à X-07 |
| `app/streamlit_app.py` | Entrée : navigation en haut, barre latérale (date des données, fond de carte) |
| `app/commun.py` | Chargement en cache, couleurs, formats français, cartes pydeck |
| `app/vues/p1_synthese.py` … `p5_methode.py` | Les cinq pages |
| `.streamlit/config.toml` | Thème accessible (couleur principale `#0072B2`) |
| `tests/test_exports.py`, `tests/test_app.py` | Exports et mesures ; chaque page s'exécute sans erreur sur les exports réels |

## Équivalences Power BI → Streamlit

| Power BI (conception) | Streamlit |
|---|---|
| Mesure DAX | Fonction de `src/export/mesures.py` (ex. `Taux de couverture` → `couverture()`, `Écart K6` → `controles()`) |
| `HASONEVALUE(dim_mode)` | Segment mode à sélection unique obligatoire (`st.segmented_control`, `required=True`) |
| Mesure non additive (vide si plusieurs sites) | Valeur affichée pour **un** site sélectionné ; jamais de somme |
| Carte Azure Maps (bulles + référence) | `pydeck` : vrais carrés de 200 m (page 2), points (pages 1, 3, 4), contours des communes. Fond de carte optionnel |
| Interaction croisée (clic sur un tableau) | Sélection de ligne `st.dataframe(on_select="rerun")` → mise en évidence sur la carte et décomposition du score |
| Segment commune synchronisé | Même clé de session `communes` sur les pages 2 et 3 |
| Signets Efficacité / Équité | Segment « Variante » de la page 4 |
| Message si combinaison absente | Avertissement + arrêt de la page (équité hors coût central) |
| Titres dynamiques | Titres calculés à partir des exports : aucun chiffre écrit en dur |
| Page 5, contrôles = 0 | `mesures.controles()` : taux application = Gold par mode, Σ carreaux gagnés = K6, Σ gains marginaux = K6 |

## Règles tenues

- L'application ne lit que `data/gold/exports/` (AD3) et ne recalcule aucun KPI autrement que le pipeline.
- Chaque chiffre de coût ou de budget porte son étiquette (« hypothèse de simulation », « estimation publique »).
- Le score est présenté comme un classement, jamais comme une prédiction (bandeau page 3).
- Couleurs Okabe-Ito, toujours doublées d'un libellé ; texte au contraste ≥ 4,5:1.
- Note technique : dans `pydeck`, une chaîne est lue comme une expression ; les paramètres `*_units` ne sont donc pas utilisés (rayons et traits en mètres, avec un minimum en pixels).
