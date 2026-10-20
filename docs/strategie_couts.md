# Stratégie de recherche des coûts

**Statut :** méthode. Aucun montant n'est retenu dans ce fichier.
**Constat :** Citiz n'a fourni aucun ordre de grandeur pour une station Citiz, un arrêt de transport ou une station vélo.

Chaque montant utilisé plus tard porte **une seule** étiquette. Un chiffre sans étiquette n'entre pas dans un scénario.

| Étiquette | Définition | Ce qui doit être écrit à côté du chiffre |
|---|---|---|
| **Coût documenté** | Montant publié par une source primaire, repris tel quel | URL, date, auteur, année du montant, ce que le montant inclut et exclut |
| **Estimation publique** | Calcul explicite à partir d'un ou plusieurs montants documentés | Formule, sources, et ce que le calcul ajoute comme hypothèse |
| **Hypothèse de simulation** | Paramètre choisi pour faire tourner le scénario, faute de source assez fiable | Valeur basse, centrale, haute, unité, et la phrase « hypothèse de simulation » |

Un coût documenté dans une autre ville ou une autre année devient une estimation publique dès qu'on l'applique au territoire d'étude. Il ne reste pas un coût documenté.

---

## Où chercher, dans cet ordre

1. Délibérations et rapports de la collectivité ou de l'AOM du territoire retenu (station, arrêt, vélo).
2. Rapports d'activité publics des coopératives Citiz du territoire, s'ils chiffrent un équipement.
3. Marchés publics (BOAMP, données essentielles de la commande publique) dont l'objet est un arrêt, une station vélo ou une station d'autopartage.
4. Publications CEREMA, ADEME ou équivalent, pour un coût unitaire national servant de base d'estimation.
5. Presse, seulement si elle cite le document primaire. La presse seule ne produit pas un coût documenté.

Si l'étape 1 à 4 ne donne rien de fiable pour un type d'équipement, ce type entre dans le scénario comme hypothèse de simulation. On ne comble pas le trou par un chiffre vraisemblable non sourcé.

---

## Règles d'usage dans le scénario

- Trois paramètres distincts : `cout_citiz`, `cout_arret_tc`, `cout_station_velo`. Chacun a une étiquette et, pour une hypothèse, une fourchette.
- Le coût du scénario (K7) est la somme de ces paramètres. K8 reprend la même étiquette : si un seul poste est une hypothèse, K8 est une hypothèse de simulation.
- L'optimisation est relancée au moins sur la valeur basse et la valeur haute lorsque le poste est une hypothèse. L'écart de population nouvellement couverte est montré.
- Power BI affiche l'étiquette à côté du montant, pas seulement dans une annexe.
- Aucun montant n'est inventé dans les documents de cadrage. Les valeurs n'apparaissent qu'au moment où la source ou la fourchette est écrite dans le registre des coûts.
