# Registre des coûts (étiquetés)

**Statut :** recherche du 21/10/2026, selon `strategie_couts.md`. Aucun coût fourni par Citiz.
**Règle :** chaque montant porte **une** étiquette.

- **Coût documenté** : montant publié, repris tel quel.
- **Estimation publique** : montant documenté **appliqué à La Rochelle** ou combiné par un calcul écrit.
- **Hypothèse de simulation** : paramètre choisi faute de source.

Un montant documenté ailleurs devient une estimation publique dès qu'on l'applique à La Rochelle.

**Base de coût retenue :** coût pour la **collectivité** sur un **horizon de 3 ans** (hypothèse de simulation), investissement compris. Les montants sont en euros HT, aux prix de l'année de la source, **sans actualisation** (limite).

## 1. Montants trouvés (sources primaires)

| # | Montant | Ce qu'il couvre | Source | Année |
|---|---|---|---|---|
| C1 | **4 000 € HT** par boîtier télématique et par véhicule (achat) | Équipement d'un véhicule Citiz, financé par la collectivité | Convention de déploiement de l'autopartage, Pôle métropolitain du Genevois français et SCIC Alpes Autopartage (Citiz), annexe 1, art. 2.2 et 5.3 — [PDF](https://genevoisfrancais.org/wp-content/uploads/CS2023_03.2-MAJ-CONVENTION-DEPLOIMENT-AUTOPARTAGE_annexe-1.pdf) | 2023 (convention jusqu'au 31/10/2024) |
| C2 | **250 € TTC par mois et par voiture au maximum** (forfait de la collectivité), réduit selon l'usage (intéressement) | Garantie de fonctionnement versée à Citiz | Même convention, art. 6.2 et 6.4 | 2023 |
| C3 | Coûts d'aménagement d'une station « minimes », sans montant | Station (marquage, signalétique) | Livre blanc Citiz 2026, p. 11 — [PDF](https://www.citiz.coop/uploads/2026/02/2026-CITIZ-livre_blanc.pdf) | 2026 |
| C4 | **110 000 € HT** pour 2 stations de 10 vélos à assistance électrique (vélos compris) ; fonctionnement estimé à 6 000 € par an et maintenance à 3 000 € par an | Vélo en libre-service PériVélo | Grand Périgueux, délibération DD2022-135 du 8/12/2022 — [PDF](https://www.grandperigueux.fr/fileadmin/medias/Publications/Deliberations/2022/Conseil_du_8_d%C3%A9cembre_2022/DD2022-135_PERIMOUV_MISE_EN_PLACE_VELOS_LIBRE-SERVICE.pdf) | 2022 |
| C5 | Quai de bus accessible : **10 700 € HT** en moyenne (CAPI) ; **18 000 à 23 000 €** pour un quai traditionnel ; de 5 600 à 22 400 € HT selon les cas | Aménagement de l'arrêt seulement (pas l'exploitation de la ligne) | CEREMA, rapport sur les quais modulaires, 2018 — [PDF](https://www.cerema.fr/fr/system/files/documents/2018/02/CEREMA-rapport-quais-modulaires-art1642.pdf) | 2011–2018 |
| C6 | 1 voiture en autopartage = 8 voitures en moins ; libère 1 à 3 places de stationnement | Pour K13 (CO₂), pas pour les coûts | Livre blanc Citiz 2026, p. 8 | 2026 |

## 2. Paramètres de coût par station (horizon 3 ans)

| Type | Bas | Central | Haut | Calcul | Étiquette |
|---|---:|---:|---:|---|---|
| **Citiz** (1 véhicule) | 4 000 € | 8 500 € | 13 000 € | C1 + forfait C2 × 36 mois × {0 ; 50 % ; 100 %} ; station C3 comptée à 0 | Bas et haut : **estimation publique** (bornes C1, C2). Central (50 % du forfait) : **hypothèse de simulation** |
| **Vélo** (station de 10 VAE) | 55 000 € | 68 500 € | 82 000 € | C4 / 2 stations = 55 000 € ; + (6 000 + 3 000) / 2 × 3 ans = 13 500 € | Central : **estimation publique**. Bas (investissement seul) : estimation publique. Haut (+ 20 %) : **hypothèse de simulation** |
| **Bus** (quai d'arrêt) | 10 700 € | 18 000 € | 23 000 € | C5, quai seul | **Estimation publique**. Ne comprend **pas** le coût de desserte (passage d'une ligne), d'où l'usage indicatif |

**Limites à dire telles quelles :**

- **Citiz :** le prix du véhicule n'est pas compté, car il est supposé porté par la coopérative. C'est une hypothèse à valider avec Citiz.
- **Bus :** un arrêt n'a de valeur que si une ligne y passe. Le coût réel inclut l'exploitation, que nous ne connaissons pas.
- Les montants ne sont pas actualisés. Ils viennent d'autres territoires, à des années différentes.
- Le forfait C2 est en TTC et le boîtier C1 en HT. On les additionne sans conversion : l'écart de TVA n'est pas connu.
