# Registre des sources

**Statut :** inventaire écrit le 21 octobre 2026. Lot 0 déposé le même jour : S02 et S03, empreintes dans `recuperations`. Les autres sources ne sont pas téléchargées.

Le fichier lu par le pipeline et par le jury est `docs/registre_des_sources.xlsx`. Ce document fixe les règles et le sens des colonnes.

Aucune valeur n'est saisie sans avoir été lue sur la source. Ce qui n'a pas été lu est `à vérifier` ou `à rechercher`. Les URL, dates et licences déjà notées viennent de `selection_territoire.md` (consultation du 20 octobre 2026). Les coûts ne sont pas ici : ils sont dans `strategie_couts.md`, à E2 pour la méthode et à E7 pour les montants.

## Priorité

| Valeur | Sens |
|---|---|
| `obligatoire` | Nécessaire au MVP sur La Rochelle, ou à l'apprentissage H6 |
| `recommandee` | Utile, ne bloque pas le MVP |
| `optionnelle` | Seulement s'il reste du temps, ou secours d'une source obligatoire |

S07 est la source proposée pour la densité d'arrêts de H6 : un seul fichier, le même traitement dans les cinq villes. S18a à S18d restent le secours, non écartées. S05 est un graphe OSMnx (GraphML) : pas d'URL, la requête est tracée par ses paramètres, et la reproductibilité vient du graphe sauvegardé. S07 n'est pas encore une fiche vérifiée.

## Onglet `sources`

Une ligne par source. S06 et S18 sont découpés par ville (`S06a`, `S18a`…) pour que chaque `source_id` ait son dossier bronze. Cela fait 24 lignes, pas une ligne par famille.

| # | Colonne | Contenu |
|---|---|---|
| 1 | `source_id` | Identifiant stable (`S01`, `S06a`) |
| 2 | `priorite` | `obligatoire`, `recommandee` ou `optionnelle` |
| 3 | `famille` | Dossier bronze : `gtfs`, `gbfs`, `insee_filosofi`, `insee_omphale`, `admin_express`, `osm`, `external` |
| 4 | `nom` | Nom du jeu tel que publié |
| 5 | `producteur` | Qui produit la donnée |
| 6 | `diffuseur` | Où elle est publiée |
| 7 | `territoire` | `larochelle`, `angers`, `poitiers`, `nantes`, `rennes` ou `national` |
| 8 | `role` | `decision`, `apprentissage_h6` ou `reference` |
| 9 | `usage_metier` | À quoi elle sert |
| 10 | `kpi_lies` | Indicateurs alimentés |
| 11 | `granularite` | Unité spatiale ou temporelle |
| 12 | `format` | Format d'origine |
| 13 | `frequence_maj` | Fréquence déclarée par le producteur, sinon `à vérifier` |
| 14 | `millesime_ou_version` | Millésime ou version connue |
| 15 | `licence` | Licence lue sur la fiche |
| 16 | `attribution_requise` | `oui` ou `non`, avec le texte si il a été recopié |
| 17 | `url_fiche` | Page de présentation |
| 18 | `url_ressource` | Lien direct du fichier ou du flux |
| 19 | `statut_url` | `verifiee` ou `a_rechercher` |
| 20 | `date_consultation` | `AAAA-MM-JJ`, vide si la page n'a pas été ouverte |
| 21 | `chemin_bronze` | `data/bronze/<famille>/<territoire>/<source_id>_<AAAA-MM-JJ>/` |
| 22 | `limites_connues` | Défauts connus à l'avance |
| 23 | `controles_qualite` | KPI qualité prévus |
| 24 | `statut` | `identifiee`, `verifiee`, `telechargee` ou `ecartee` |
| 25 | `commentaire` | Libre |

`verifiee` = URL et licence lues à la date indiquée. Cela ne veut pas dire que le fichier est dans `data/`. `telechargee` est le statut après dépôt. S02 et S03 le sont depuis le lot 0. La licence de S03 reste `à vérifier`.

## Onglet `recuperations`

Une ligne par téléchargement. Vide tant qu'aucun fichier n'est déposé.

`recup_id` · `source_id` · `date_heure_recuperation` (ISO, avec fuseau) · `url_effective` · `version_producteur` · `fichier_local` (chemin relatif) · `taille_octets` · `sha256` · `licence_constatee` · `methode` (`navigateur`, `script` ou `manuel`) · `commentaire`

## Onglet `decisions_citiz`

`id` · `question` · `pourquoi` · `hypothese_par_defaut` · `reponse` · `date` · `source_reponse`

Pas de canal vers Citiz au 21 octobre 2026. `reponse`, `date` et `source_reponse` restent vides.

Les hypothèses par défaut DC1–DC8 s'appliquent tant que la colonne réponse est vide.

| ID | Hypothèse par défaut |
|---|---|
| DC1 | Le flux est considéré comme exhaustif, et c'est écrit dans les limites |
| DC2 | Cible = présence seulement |
| DC3 | 5 min (sujet officiel), avec 10 min en sensibilité si le temps le permet |
| DC4 | Hypothèse de simulation étiquetée |
| DC5 | Deux scénarios montrés, sans trancher |
| DC6 | Aucune exclusion, et c'est écrit dans les limites |
| DC7 | Nom seulement, sans logo |
| DC8 | Non (H5 confirmée) |

## Onglet `cible_usage`

`champ` · `definition` · `niveau_agregation` · `pourquoi` · `contrainte_vie_privee`

Demande non envoyée. Si ces agrégats arrivaient, H6 pourrait devenir une prédiction de fréquentation : il faudrait rouvrir le cahier (H5, H6, A17). Ce n'est pas le cas.

Règles de la demande : uniquement des agrégats, aucun trajet individuel, aucun identifiant d'abonné ; masquage des petits effectifs selon un seuil fixé par Citiz ; usage limité au hackathon.

## Traçabilité

À chaque téléchargement, sans exception.

| Étape | Action |
|---|---|
| 1 | Créer `data/bronze/<famille>/<territoire>/<source_id>_<AAAA-MM-JJ>/` |
| 2 | Y déposer le fichier tel quel, jamais renommé ni modifié |
| 3 | Empreinte SHA-256 (`Get-FileHash -Algorithm SHA256` ou `sha256sum`) |
| 4 | Noter la version du producteur : `feed_info.txt` ou `calendar` pour un GTFS ; `last_updated` et `version` pour un GBFS ; millésime INSEE ; édition IGN ; date d'extraction OSM |
| 5 | Écrire `_manifest.json` : `source_id`, `url`, `date_heure`, `fichier`, `taille_octets`, `sha256`, `licence`, `version_producteur` |
| 6 | Ajouter une ligne dans `recuperations` |
| 7 | Passer `statut` à `telechargee` |

La couche bronze est immuable : un nouveau téléchargement crée un nouveau dossier daté. Pour un GBFS, on garde `gbfs.json`, `system_information` et `station_information`. `station_status` ne décrit pas l'offre. La licence est notée au moment du téléchargement.

Mission 4 = ce registre, sans téléchargement. V-a (archive GTFS Yélo) et V-b (Filosofi) sont la première action après validation du registre, toujours dans E2, avec empreinte. Les autres empreintes sont à E3.
