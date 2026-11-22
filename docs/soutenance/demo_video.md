# Vidéos de démonstration

**Statut :** Mission 14, 21/10/2026. Deux vidéos : une **vidéo de secours automatique** (si la démo en direct échoue) et une **vidéo commentée** (envoi au jury, finale, réseaux). Les chiffres affichés viennent de l'application, pas du montage.

## V1 — Vidéo de secours, sous-titrée (automatique, ≈ 3 min 20)

Produite par `scripts/enregistrer_demo.py` (Playwright) : le script pilote l'application, affiche les sous-titres et enregistre l'écran. Le même parcours est rejoué à l'identique à chaque enregistrement.

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe -m playwright install chromium
# terminal 1
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
# terminal 2 (avec fond de carte ; ajouter --sans-fond pour une version hors ligne)
.\.venv\Scripts\python.exe scripts/enregistrer_demo.py --url http://localhost:8501
```

Sortie : `reports/demo/demo_application.webm`, et `.mp4` si `ffmpeg` est installé (`winget install ffmpeg`). PowerPoint lit le `.mp4`.

| Temps | Page | Action automatique | Sous-titre |
|---|---|---|---|
| 0:00 | 1 | Ouverture | Question : où financer de nouvelles stations Citiz… |
| 0:10 | 1 | — | Moins d'un habitant sur dix a une station Citiz à 5 minutes. |
| 0:20 | 1 | Défilement | 85 000 € sur 3 ans, 10 stations, couverture doublée. Efficacité ou équité. |
| 0:45 | 2 | Mode Citiz, tableau des stations, communes prioritaires | Diagnostic au carreau ; habitants servis par chaque station ; 9 communes < 60 %. |
| 1:30 | 3 | Sélection du site de rang 2 ; sensibilité | Score de potentiel, pas une prédiction ; le score départage, l'optimisation choisit. |
| 2:10 | 4 | Défilement, bouton Équité, retour Efficacité | Optimum prouvé ; rendements décroissants ; prix de l'équité. |
| 2:50 | 5 | Défilement | Contrôles, hypothèses étiquetées, limites ; décision proposée. |

Usage pendant la soutenance : onglet ouvert, en pause. Pitch de 5 min : lire de 0:10 à 0:45 puis de 2:10 à 2:50. Pitch de 10 min : lecture intégrale, en commentant à voix haute.

## V2 — Vidéo commentée (voix, ≈ 2 min)

À enregistrer soi-même, avec la barre de jeu Windows (Win + Alt + R) ou OBS, sur l'application en plein écran, fond de carte activé. Texte : section A de `narration.md`, blocs « Démo » et slides 6-7, lus sur l'écran correspondant.

| Plan | Durée | Écran | Voix |
|---|---|---|---|
| 1 | 15 s | Page 2, mode Tous modes | « Un habitant sur cinq n'a aucune option de mobilité à 5 minutes à pied… » |
| 2 | 15 s | Page 2, mode Citiz | « Pour Citiz, c'est neuf sur dix. L'offre est au centre de La Rochelle. » |
| 3 | 25 s | Page 1 | « Avec 85 000 € sur trois ans, dix stations doublent la couverture… » |
| 4 | 30 s | Page 4, Efficacité puis Équité | « Même budget, contrainte d'équité : 14 446 habitants au lieu de 18 816… » |
| 5 | 20 s | Page 4, courbe et 12 scénarios | « Les premières stations rapportent le plus ; le coût unitaire pèse autant que le budget. » |
| 6 | 15 s | Page 5, recoupements | « Tout est vérifiable : les contrôles sont à zéro. » |
| 7 | 10 s | Page 1 | « Trois décisions : financer, choisir l'équité, tester un an. » |

Règles : souris lente, pas de saisie au clavier, pause d'une seconde avant chaque clic, aucun écran de code. Exporter en MP4 1080p, moins de 50 Mo.

## Versionnement

Ni le `.webm` ni le `.mp4` ne sont versionnés (`.gitignore`). Le `.mp4` (≈ 7 Mo) est publié comme fichier joint de la release v1.0 : https://github.com/soboure69/hackathon-mobility-citiz/releases/download/v1.0/demo_application.mp4
