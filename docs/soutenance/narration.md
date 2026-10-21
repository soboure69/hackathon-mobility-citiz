# Narration de la soutenance

**Statut :** Mission 14, 21/10/2026. Texte à dire, pas à lire : apprendre les phrases en gras (ouverture, transitions, conclusion), garder le reste en idées. Débit visé : 130 mots par minute. [Crochets] = geste ou action. Chiffres vérifiés dans l'application.

---

## A. Pitch de 5 minutes (≈ 640 mots)

### [Slide 1] — 0:00

**« Un habitant de l'agglomération de La Rochelle sur cinq n'a aucune solution de mobilité à moins de cinq minutes à pied de chez lui. Pour l'autopartage Citiz, c'est neuf sur dix. »**

### [Slide 2] — 0:15

Le bus couvre 76 % des habitants. Le vélo en libre-service, 29 %. Citiz, 9,8 %. Au total, 38 672 personnes n'ont ni bus, ni vélo, ni voiture partagée à cinq minutes de marche.

### [Slide 3] — 0:30

La question que nous a posée Citiz est simple : **où ouvrir les prochaines stations ?** Nous y avons répondu sur un territoire réel : la communauté d'agglomération de La Rochelle, 28 communes, 174 000 habitants, 24 stations Citiz aujourd'hui. Uniquement des données ouvertes, uniquement des données réelles.

### [Slide 4] — 1:00

Pour savoir qui est vraiment desservi, aucune source ne suffit. Nous en avons croisé cinq : les arrêts de bus, les stations Citiz et vélo, la population de l'INSEE par carreaux de 200 mètres, les limites des communes, et surtout le réseau piéton réel d'OpenStreetMap. Cinq minutes, ce n'est pas un cercle sur une carte : c'est 400 mètres de trottoir. Et chaque habitant est compté une seule fois, même s'il est proche de plusieurs stations.

**Plutôt que de vous le décrire, je vous le montre.**

### [Démo] — 1:45

[Page 1] Voici la recommandation. Aujourd'hui 9,8 %. Avec 85 000 euros sur trois ans, dix stations, 18 816 habitants de plus, 4,52 euros par habitant gagné.
[Survoler deux points verts] Les points verts sont les stations proposées, dans l'ordre de leur apport.
[Page 4, cliquer Équité] Maintenant, même budget, mais j'impose que 30 % des gains aillent aux communes les moins bien desservies. 14 446 habitants au lieu de 18 816. Mais 4 674 dans ces communes, au lieu de zéro.
[Cliquer Efficacité] **Le choix vous appartient. L'outil le chiffre.**

### [Slide 6] — 2:45

Notre recommandation : dix stations, 85 000 euros sur trois ans. La couverture Citiz passe de 9,8 % à 20,6 %. Elle double. Ce portefeuille n'est pas une liste triée à la main : c'est la meilleure combinaison possible pour ce budget, prouvée par le solveur. Et il y a des rendements décroissants : la première station couvre 4 040 habitants, la trentième moins de 900. **Les premières stations rapportent le plus : c'est par elles qu'il faut commencer.**

### [Slide 7] — 3:30

Mais le choix le plus efficace a un angle mort : les dix stations sont toutes à La Rochelle même. Les neuf communes sous 60 % de couverture ne reçoivent rien. Leur garantir 30 % des gains coûte 23 % de l'impact. En échange, on atteint douze fois plus d'habitants qui n'avaient aucune option : 2 006 au lieu de 168. **L'équité a un prix, et ce prix est mesurable.**

### [Slide 8] — 4:15

Soyons clairs sur ce que l'outil ne dit pas. Il ne prédit pas combien de locations fera une station : il n'existe aucun historique d'usage public. Nous avons donc mesuré ce qui est certain, la proximité, et classé les sites avec un score transparent. Les coûts sont des estimations, affichées comme telles.

### [Slide 9] — 4:40

**Trois décisions. Financer les dix stations. Choisir le curseur d'équité. Et tester trois stations pendant un an, pour mesurer enfin l'usage réel. Nous ne vous demandons pas de croire une prédiction : nous vous montrons des habitants comptés un par un. Merci.**

---

## B. Pitch de 10 minutes (≈ 1 250 mots)

### [Slide 1] — 0:00

**« Un habitant de l'agglomération de La Rochelle sur cinq n'a aucune solution de mobilité à moins de cinq minutes à pied de chez lui. Pour l'autopartage Citiz, c'est neuf sur dix. »**

### [Slide 2] — 0:15

Le bus couvre 76 % des habitants, le vélo en libre-service 29 %, Citiz 9,8 %. 38 672 personnes n'ont aucune de ces options à cinq minutes de marche. Ce sont les chiffres que nous allons faire bouger.

### [Slide 3] — 0:30

Citiz doit choisir où ouvrir ses prochaines stations. Nous avons pris un territoire réel, choisi avec une grille : sept agglomérations candidates, des critères éliminatoires — un flux Citiz ouvert, des arrêts de bus publiés, une population carroyée, un intérêt métier — puis une note. La Rochelle est sortie première, Nantes deuxième. 28 communes, 174 000 habitants, 24 stations Citiz.

### [Slide 4] — 0:45

Notre chaîne de données a trois étages. **Bronze** : les fichiers bruts, jamais modifiés, chacun avec son empreinte et sa date. **Silver** : nettoyés, dédoublonnés, rattachés au réseau piéton. Par exemple, un même arrêt de bus apparaît plusieurs fois dans les fichiers, une fois par quai : nous les regroupons, sinon nous compterions trois options là où il n'y en a qu'une. **Gold** : les tables de décision. Tout est rejouable par un script, et chaque table porte l'identifiant du code qui l'a produite.

Le cœur de la mesure, c'est la marche réelle. Pour chaque carreau de 200 mètres, nous calculons le trajet sur le réseau piéton OpenStreetMap jusqu'à chaque station. Moins de 400 mètres : le carreau est desservi.

### [Slide 5] — 1:45

Des données ouvertes ne sont pas des données propres. Nous avons posé 52 indicateurs de qualité : complétude, unicité, jointure, fraîcheur. 40 sont conformes, 3 sont en alerte. Nous les affichons : le flux des vélos Yélo date de 126 jours, la capacité de ces stations vélo n'est pas renseignée, et 98,3 % du réseau piéton est connecté au lieu des 99 % visés. **Aucune de ces trois alertes ne touche la recommandation Citiz.**

### [Démo, page 2] — 2:15

[Page 2] Voici le diagnostic. Chaque carré est un carreau de 200 mètres : bleu s'il est desservi, orange sinon.
[Cliquer Citiz] En mode Citiz, l'offre est concentrée au centre de La Rochelle.
[Faire défiler jusqu'au tableau] Et pour chaque station ou arrêt, le nombre d'habitants à cinq minutes : c'est le deuxième objectif du sujet.
[Faire défiler jusqu'aux communes] Neuf communes sont sous 60 % de couverture tous modes : nous les appelons communes prioritaires, pas « mal desservies ». Et un résultat contre-intuitif : les ménages les plus modestes sont les mieux couverts, à 89 %.

### [Démo, page 3] — 3:15

[Page 3] Où ajouter ? Nous avons retenu 2 200 sites possibles pour Citiz : sur le réseau, accessibles en voiture, et qui gagnent des habitants par rapport à l'existant.
[Cliquer la ligne 2] Chaque site reçoit un score sur 100, et ce score se décompose : combien d'habitants il gagne, combien n'ont aucune option, la complémentarité avec le bus, le logement collectif, les petits ménages.
[Tableau de sensibilité] Nous avons testé ce score en changeant les pondérations : l'ordre d'ensemble tient, mais le haut du classement est serré, les meilleurs scores sont entre 79 et 81. **C'est pour cela que le score ne décide pas : il départage. C'est l'optimisation qui choisit.**

### [Slide 6 + démo page 4] — 4:15

[Page 4] Le problème est classique en recherche opérationnelle : couvrir le plus d'habitants possible avec un budget donné, chaque habitant ne comptant qu'une fois. Nous le résolvons de façon exacte, et le solveur prouve que la solution est optimale à 0,1 % près.
[Budget 85 000 €] Au budget central, dix stations, 18 816 habitants, 4,52 euros par habitant.
[Budget 170 000 €] Doubler le budget ne double pas l'impact : vingt stations, 29 834 habitants.
[Coût 4 000 € puis 13 000 €] Le coût unitaire pèse autant que le budget : à 85 000 euros, on couvre entre 12 888 et 30 834 habitants selon le coût réel d'une station. **Un devis Citiz est la donnée qui vaut le plus.**
[Courbe] La première station couvre 4 040 habitants, la trentième 894.
Pour contrôler le solveur, nous le comparons à une règle simple — prendre à chaque fois le site qui rapporte le plus par euro. Elle trouve le même résultat dans 8 cas sur 9 ; dans le dernier, l'optimisation fait mieux.

### [Slide 7 + démo Équité] — 6:00

[Cliquer Équité] Le portefeuille efficace a un angle mort : aucune station dans les communes prioritaires. Si on impose qu'au moins 30 % des habitants gagnés y vivent, on perd 27 % de l'impact au petit budget, 23 % au budget central, 15 % au grand budget. Plus le budget est grand, moins l'équité coûte. Et un effet que nous n'attendions pas : la variante équité atteint 2 006 habitants qui n'avaient aucune option, contre 168 pour la variante efficace. **Ce n'est pas à l'outil de choisir. C'est à vous ; mais vous choisissez en connaissant le prix.**

### [Slide 8 + démo page 5] — 7:00

[Page 5] Pourquoi nous faire confiance ? Parce que tout est vérifiable. L'application ne recalcule rien : six recoupements prouvent qu'elle affiche exactement les chiffres du pipeline. Chaque hypothèse est étiquetée : certaine, estimée, ou hypothèse de travail.

### [Slide 8] — 8:00

Nos limites, maintenant. Un : nous ne prédisons pas l'usage. Sans historique de locations, ce serait inventer une cible. Nous avons conçu un modèle qui apprend où Citiz est déjà implanté dans cinq villes et se valide ville par ville ; il n'est pas livré. Deux : les coûts sont des estimations. Trois : le sujet parle aussi de bus et de vélo ; nos candidats bus et vélo sont scorés, mais nous n'avons optimisé que Citiz, faute de coûts fiables. Quatre : nous n'affichons pas de bilan carbone, car il faudrait inventer un taux de report modal. Et pour la vie privée : nous ne manipulons aucune donnée personnelle, et 42 % des carreaux, 6 % des habitants, ont des valeurs imputées par l'INSEE au titre du secret statistique.

### [Slide 9] — 9:00

**Trois décisions. Un : financer les dix stations du portefeuille, 85 000 euros sur trois ans, pour doubler la couverture Citiz. Deux : choisir le curseur d'équité, en connaissant son prix. Trois : tester trois de ces stations pendant un an, avec des indicateurs d'usage, pour remplacer notre score par un modèle appris. Et demain, la même méthode s'applique à n'importe quelle agglomération française : il suffit de changer le code du territoire. Nous ne vous demandons pas de croire une prédiction ; nous vous montrons des habitants comptés un par un. Merci.**

---

## C. Phrases de secours

| Situation | Phrase |
|---|---|
| L'application ne répond pas | « Je vous montre la même chose en vidéo, enregistrée sur les mêmes données. » [onglet vidéo] |
| Question hors sujet pendant le pitch | « Excellente question, j'y reviens juste après, elle touche la partie limites. » |
| Trou de mémoire sur un chiffre | « Le chiffre exact est sur cette page » [pointer l'application] — ne jamais arrondir au hasard. |
| Dépassement de temps | Sauter la slide 5 (qualité) et la renvoyer en question. |
