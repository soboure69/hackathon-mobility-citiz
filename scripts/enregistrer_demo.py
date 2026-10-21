"""Enregistre la vidéo de démonstration de secours de l'application (Playwright, sous-titrée).

Prérequis (une fois) :  pip install playwright  puis  python -m playwright install chromium
Usage :
    1) dans un terminal :  python -m streamlit run app/streamlit_app.py
    2) dans un autre :     python scripts/enregistrer_demo.py --url http://localhost:8501
Sortie : reports/demo/demo_application.webm (et .mp4 si ffmpeg est installé).
Le parcours suit docs/soutenance/demo_video.md. Les chiffres viennent de l'application, pas du script.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "reports" / "demo"
TAILLE = {"width": 1440, "height": 900}

JS_SOUS_TITRE = """(texte) => {
  let b = document.getElementById('sous-titre-demo');
  if (!b) { b = document.createElement('div'); b.id = 'sous-titre-demo';
    Object.assign(b.style, {position: 'fixed', left: '50%', bottom: '24px', transform: 'translateX(-50%)',
      maxWidth: '1100px', padding: '10px 18px', background: 'rgba(26,26,26,0.88)', color: '#fff',
      font: '600 20px/1.35 "Segoe UI", Helvetica, Arial, sans-serif', borderRadius: '8px', zIndex: 99999,
      textAlign: 'center'}); document.body.appendChild(b); }
  b.textContent = texte; b.style.display = texte ? 'block' : 'none'; }"""


def sous_titre(page: Page, texte: str, duree_ms: int = 4500) -> None:
    page.evaluate(JS_SOUS_TITRE, texte)
    page.wait_for_timeout(duree_ms)


def defiler(page: Page, pixels: int, pas: int = 120, pause_ms: int = 140) -> None:
    for _ in range(abs(pixels) // pas):
        page.mouse.wheel(0, pas if pixels > 0 else -pas)
        page.wait_for_timeout(pause_ms)


def aller(page: Page, onglet: str) -> None:
    page.evaluate(JS_SOUS_TITRE, "")          # pas de sous-titre de la page précédente sur la suivante
    page.get_by_role("link", name=onglet).first.click()
    page.wait_for_timeout(6000)
    page.mouse.move(700, 300)


def bouton(page: Page, texte: str) -> None:
    page.get_by_role("radio", name=texte, exact=True).first.click()   # st.segmented_control = boutons radio
    page.wait_for_timeout(4500)


def cocher_ligne(page: Page, indice_tableau: int, ligne: int) -> None:
    """Coche une ligne d'un st.dataframe (grille dessinée en canvas : clic par coordonnées)."""
    grille = page.locator('[data-testid="stDataFrame"]').nth(indice_tableau)
    grille.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    boite = grille.bounding_box()
    x, y = boite["x"] + 20, boite["y"] + 35 * (ligne + 1) + 17
    page.mouse.move(x, y)                     # la grille n'accepte le clic qu'après un survol
    page.wait_for_timeout(400)
    page.mouse.click(x, y)
    page.wait_for_timeout(5000)


def parcours(page: Page, url: str, sans_fond: bool = False) -> None:
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(9000)
    if sans_fond:
        page.get_by_text("Fond de carte (Internet)").click()
        page.wait_for_timeout(4000)
    sous_titre(page, "Question : où financer de nouvelles stations Citiz dans l'agglomération de La Rochelle ?", 5000)
    sous_titre(page, "Aujourd'hui, moins d'un habitant sur dix a une station Citiz à 5 minutes à pied.", 5000)
    sous_titre(page, "Recommandation de référence : 85 000 € sur 3 ans, 10 stations, couverture Citiz doublée.", 5500)
    defiler(page, 700)
    sous_titre(page, "Même budget, deux choix : maximiser les habitants couverts, ou en garantir 30 % aux communes peu desservies.", 6000)
    defiler(page, -700)

    aller(page, "2 · Couverture actuelle")
    sous_titre(page, "Diagnostic : chaque carreau de 200 m, desservi ou non, à 5 minutes de marche réelle (réseau OpenStreetMap).", 6000)
    bouton(page, "Citiz")
    sous_titre(page, "Mode Citiz : l'offre actuelle se concentre au centre de La Rochelle.", 5000)
    defiler(page, 900)
    sous_titre(page, "Pour chaque station ou arrêt : le nombre d'habitants à 5 minutes à pied.", 5000)
    defiler(page, 900)
    sous_titre(page, "Neuf communes sont sous 60 % de couverture tous modes : ce sont les communes prioritaires.", 5500)
    defiler(page, -1800)
    bouton(page, "Tous modes")

    aller(page, "3 · Candidats et score")
    sous_titre(page, "2 200 sites possibles, classés par un score de potentiel. Un classement, pas une prédiction.", 6000)
    cocher_ligne(page, 0, 1)
    defiler(page, 700)
    sous_titre(page, "Chaque score se lit par ses cinq composantes : impact, besoin, bus, logement collectif, petits ménages.", 6000)
    defiler(page, 900)
    sous_titre(page, "L'ordre global résiste aux pondérations ; le haut du classement moins : le score départage, l'optimisation choisit.", 6500)
    defiler(page, -1600)

    aller(page, "4 · Optimisation budgétaire")
    sous_titre(page, "Optimisation exacte sous budget : chaque habitant compté une seule fois, optimum prouvé.", 6000)
    defiler(page, 600)
    sous_titre(page, "Rendements décroissants : la 1re station couvre 4 040 habitants, la 30e moins de 900.", 5500)
    defiler(page, -600)
    bouton(page, "Équité (≥ 30 % prioritaires)")
    sous_titre(page, "Variante équité : le prix de l'équité est mesuré, en habitants, à budget égal.", 6000)
    defiler(page, 900)
    sous_titre(page, "Plus le budget est grand, moins l'équité coûte en proportion.", 5000)
    defiler(page, -900)
    bouton(page, "Efficacité")

    aller(page, "5 · Méthode, qualité, limites")
    sous_titre(page, "Confiance : contrôles de qualité, alertes connues, recoupements application / pipeline à zéro.", 6000)
    defiler(page, 1200)
    sous_titre(page, "Hypothèses étiquetées (certain, estimé, hypothèse), sources, risques ouverts et limites.", 6000)
    defiler(page, 1200)
    sous_titre(page, "Décision proposée : financer le portefeuille, puis choisir le curseur d'équité.", 6000)
    sous_titre(page, "", 500)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enregistre la vidéo de démonstration de secours.")
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--sans-fond", action="store_true", help="désactive le fond de carte (démonstration hors ligne)")
    args = parser.parse_args(argv)
    SORTIE.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        navigateur = p.chromium.launch(args=["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        contexte = navigateur.new_context(viewport=TAILLE, record_video_dir=str(SORTIE), record_video_size=TAILLE,
                                          locale="fr-FR")
        page = contexte.new_page()
        parcours(page, args.url, args.sans_fond)
        video = page.video.path()
        contexte.close()
        navigateur.close()
    webm = SORTIE / "demo_application.webm"
    Path(video).replace(webm)
    print(f"Vidéo : {webm}")
    if shutil.which("ffmpeg"):
        mp4 = webm.with_suffix(".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "23", str(mp4)], check=True)
        print(f"Vidéo : {mp4}")
    else:
        print("ffmpeg absent : la vidéo reste en .webm (lisible par Chrome, Edge, VLC).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
