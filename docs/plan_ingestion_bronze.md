# Plan d'ingestion Bronze

**Statut :** plan validé pour l'écriture le 21 octobre 2026. Le script n'existe pas encore. Le lot 0 (S02, S03) est fait à la main. Aucune table Silver.

Le script futur lit les URL dans `docs/registre_des_sources.xlsx`. Il refuse une source dont `url_ressource` est vide ou vaut `à rechercher`. On ne télécharge pas « à peu près ».

La date de démonstration du hackathon n'est pas dans le dépôt. Le contrôle « le calendrier GTFS couvre la date de démonstration » reste ouvert tant que cette date n'est pas écrite dans `config/bronze.yaml`.

## Disponibilité

| Groupe | Sources | Situation |
|---|---|---|
| A. Prêtes | S01, S06a–d, S10 | URL directe déjà vérifiée |
| B. Lien direct noté le 21/10/2026 | S02, S03, S08 | Copié depuis la fiche ou la page INSEE |
| B. Encore sans lien direct | S18a–d | Secours de S07, hors ingestion pour l'instant |
| C. À rechercher | S04, S07, S09, S11 | Fiche ou lien direct non ouvert |
| D. Sans URL | S05 | Requête OSMnx, tracée par ses paramètres |
| Hors ingestion | S12, S13–S17 | S12 est une page de référence. S13–S17 sont optionnelles |

## Ordre

| Lot | Sources | Pourquoi |
|---|---|---|
| 0 | S02, S03 | V-a et V-b. Elles verrouillent La Rochelle. Fait à la main, comme répétition du plan |
| 1 | S04, puis S05, puis S01, S08 | Le graphe S05 a besoin du contour S04 |
| 2 | S06a–d, S07 | Apprentissage H6, hors chemin critique |
| 3 | S10, S09, S11 | Référence, hors chemin critique |

Dossier : `data/bronze/<famille>/<territoire>/<source_id>_<AAAA-MM-JJ>/`. La date est celle de la récupération. Si le dossier du jour existe, on ne l'écrase pas. Un second passage le même jour utilise le suffixe `_2`.

## Plan par source

| Source | À récupérer | Dossier | Nom de fichier | Métadonnées propres | Contrôles juste après | Licence |
|---|---|---|---|---|---|---|
| S01 | `gbfs.json`, puis les flux qu'il liste : `system_information`, `station_information`. `station_status` facultatif, jamais utilisé pour l'offre | `gbfs/larochelle/S01_…` | Nom du flux tel que listé, avec `.json` | `version` et `last_updated` de chaque flux, `ttl`, `system_id` | JSON lisible ; `version` présent ; nombre de stations ; coordonnées et `capacity` présentes ; écart avec les 24 stations du 20/10 signalé, pas bloquant | LO 2.0 : citer la source et la date de mise à jour |
| S06a–d | Comme S01 | `gbfs/<ville>/S06x_…` | Comme S01 | Comme S01 | Comme S01, face à 28, 21, 23 et 66 stations | LO 2.0 |
| S08 | `gbfs.json` | `gbfs/larochelle/S08_…` | `gbfs.json` | `last_updated` (attendu : 17/06/2026), nombre de stations embarquées | JSON lisible ; date constatée ; « export figé » dans le manifeste | Licence Ouverte (`fr-lo` sur la fiche). Version 2.0 non indiquée |
| S02 | `gtfs.zip` | `gtfs/larochelle/S02_…` | `gtfs.zip` | `feed_info.txt` s'il existe, sinon la plage de `calendar` et `calendar_dates` | Zip lisible ; `agency`, `stops`, `routes`, `trips`, `stop_times`, et `calendar` ou `calendar_dates` ; nombre de lignes ; arrêts avec coordonnées ; validité face à la date de démonstration (V-a) | Licence Ouverte (`fr-lo`) : citer la source |
| S03 | Archive nationale GeoPackage. La page publie aussi un shapefile et un CSV : une seule archive est déposée, sans conversion | `insee_filosofi/national/S03_…` | `Filosofi2021_carreaux_200m_gpkg.zip` | Millésime 2021, date de parution 12/02/2026, couches et CRS lus dans le fichier | Fichier lisible ; nombre de carreaux ; CRS lu ; carreaux dans l'emprise de l'EPCI (V-b). Sans contour S04, ce dernier contrôle attend le premier script | Licence non affichée sur la page consultée |
| S04 | Archive de l'édition en cours | `admin_express/national/S04_…` | Nom d'origine | Édition, date, CRS | Archive lisible ; couches communes et EPCI ; EPCI 241700434 avec 28 communes | À vérifier |
| S05 | Graphe OSMnx `network_type="walk"` sur le contour S04 élargi d'un tampon | `osm/larochelle/S05_…` | `walk_graph.graphml` | Version d'OSMnx, `network_type`, `retain_all`, `simplify`, tampon en mètres, dossier S04 utilisé, emprise | Graphe relisible ; nombre de nœuds et d'arêtes ; composantes (Q7, constat, pas de correction) | ODbL : « © les contributeurs d'OpenStreetMap » sur toute carte. Partage à l'identique si une base dérivée est diffusée |
| S07 | Fichier national | `gtfs/national/S07_…` | Nom d'origine | Date de mise à jour de la fiche | Lisible ; nombre d'arrêts ; arrêts dans les 5 EPCI | À vérifier |
| S10 | `fichier_diffusion_2026.xlsx` | `external/national/S10_…` | Nom d'origine | Millésime du fichier | Lisible ; 28 communes de l'EPCI présentes | À vérifier |
| S09, S11 | Fichiers publiés | selon le registre | Noms d'origine | Millésime ou date | Lisible ; nombre de lignes | À vérifier |

Le tampon de S05 est un paramètre de `config/` : au moins 400 m, l'hypothèse H2 pour 5 minutes de marche. Il est écrit dans le manifeste. Sans ce tampon, un arrêt juste hors de l'EPCI serait invisible pour un habitant en bordure.

S05 est reproductible par le graphe sauvegardé, pas par une nouvelle requête Overpass. OSM change. On ne réinterroge pas Overpass pour refaire un Bronze déjà déposé.

## Manifeste

Un `_manifest.json` par dossier.

| Champ | Contenu |
|---|---|
| `source_id`, `nom` | Repris du registre |
| `run_id` | `AAAAMMJJTHHMMSSZ_<hash court du commit>[-modifie]`. Heure UTC. Suffixe `-modifie` si le code (`src`, `scripts`, `config`, `pytest.ini`, `requirements-lock.txt`) diffère du commit, fichiers non suivis compris. `data/` et `logs/` ne comptent pas. Les manifestes manuels du lot 0 gardent leur `run_id` d'origine. |
| `date_heure` | ISO 8601 avec fuseau |
| `url_demandee`, `url_effective` | Avant et après redirection |
| `http_status` | Code par fichier |
| `fichiers` | `nom`, `taille_octets`, `sha256`, `content_type` |
| `version_producteur` | Champs propres à la source |
| `licence_registre`, `licence_constatee` | Registre, puis fiche du jour |
| `outil` | `manuel` ou nom du script, commit Git, versions de `requests` et d'`osmnx` si elles servent |
| `parametres` | S05, et la date de démonstration quand elle est connue |
| `controles` | `id`, `resultat` (`ok`, `alerte`, `echec`), `valeur` |
| `statut_ingestion` | `reussie`, `reussie_avec_alertes` ou `echouee` |

## Fichiers à créer à la mission suivante

| Fichier | Rôle |
|---|---|
| `src/utils/manifest.py` | SHA-256, écriture et relecture du manifeste |
| `src/utils/logging_setup.py` | Log au format ci-dessous |
| `src/ingestion/http_download.py` | Délai, 3 essais, en-tête qui identifie le projet, jamais d'écrasement |
| `src/ingestion/gbfs.py` | Lit `gbfs.json` et récupère les flux. Structures v2 et v3 |
| `src/ingestion/gtfs.py` | Contrôles du zip |
| `src/ingestion/osm.py` | Requête OSMnx et sauvegarde du graphe |
| `scripts/ingest_bronze.py` | `--source`, `--lot` ou `--all` |
| `scripts/sync_registre.py` | Recopie les manifestes dans `recuperations`. Excel fermé |
| `notebooks/01_bronze_ingestion.ipynb` | Raconte et affiche les contrôles. Il ne télécharge pas |
| `tests/test_manifest.py` | Empreinte et refus d'écrasement, sur un fichier créé par le test |
| `config/bronze.yaml` | Délai, essais, tampon S05, date de démonstration |

## Log

`logs/bronze_<run_id>.jsonl`, un événement par ligne. Le dossier `logs/` n'est pas versionné. La preuve versionnée est le manifeste.

```text
{"ts": "<ISO 8601>", "run_id": "...", "source_id": "S01", "etape": "download|hash|controle|manifest", "statut": "ok|alerte|echec", "message": "...", "details": {}}
```

## Réussite

Une source est réussie si les fichiers attendus sont là, aucun n'est vide, le SHA-256 recalculé est celui du manifeste, les contrôles sont `ok` ou en `alerte` documentée, et la licence constatée est notée.

Un lot est réussi si toutes ses sources le sont, si `git status` ne montre que des `_manifest.json` sous `data/`, si `recuperations` est à jour, et si le statut du registre passe à `telechargee`.

Pour le lot 0 : V-a exige que la validité du GTFS couvre la date de démonstration. V-b exige des carreaux dans l'emprise de l'EPCI. Si l'un des deux est en `echec`, le déclencheur de bascule vers Nantes (`selection_territoire.md`, §8) s'applique. Un contrôle reporté au premier script, parce que le contour ou la date manque, est une alerte, pas un échec.

## Constat du lot 0 (21/10/2026)

Les deux dépôts sont manuels. Les archives ne sont pas versionnées. La preuve est le manifeste.

| Contrôle | Résultat |
|---|---|
| V-a, structure GTFS | `ok`. Neuf fichiers, dont les obligatoires. 1 515 arrêts, aucun sans coordonnées. `feed_info` du 20261008 au 20270103, identique à `calendar`. |
| V-a, date de démonstration | `alerte`. Cette date n'est pas dans le dépôt. Le 2026-10-21 est dans la plage du flux. Pas de bascule vers Nantes. |
| V-b, fichier Filosofi | `ok`. Zip lisible, trois GeoPackage. Métropole : 2 298 582 carreaux, EPSG:2154. Martinique : 11 222, EPSG:5490. La Réunion : 14 773, EPSG:2975. |
| V-b, carreaux dans l'emprise | `alerte`. À faire au premier script : le contour S04 n'existe pas encore. Aucune table Silver. |
| Licence S03 | Non affichée sur la page. Reste `à vérifier`. |
| Documentation | Déposée ensuite en S03d, dans un autre dossier. `S03_2026-10-21/` n'est pas rouvert. |
