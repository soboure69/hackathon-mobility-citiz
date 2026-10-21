"""Tests du bloc Silver S-4 (réseau piéton), sur un petit graphe construit par le test."""
import networkx as nx

from src.cleaning import osm
from src.cleaning.audit import Suivi

AUDIT = {"source_id": "S99", "fichier_origine": "f", "sha256_origine": "h", "date_donnee": "d", "run_id": "RUN"}


def graphe(avec_motorroad=False):
    g = nx.MultiDiGraph(crs="epsg:4326")
    for n, (x, y) in {1: (-1.150, 46.160), 2: (-1.149, 46.160), 3: (-1.148, 46.160),
                      4: (-1.147, 46.160), 9: (-1.100, 46.200), 10: (-1.099, 46.200)}.items():
        g.add_node(n, x=x, y=y, street_count=1)
    aretes = [
        (1, 2, {"highway": "footway", "length": 77.0}),
        (2, 3, {"highway": "trunk", "length": 77.0}),
        (3, 4, {"highway": "busway", "access": "no", "length": 77.0}),
        (1, 3, {"highway": "service", "access": "no", "length": 150.0}),
        (9, 10, {"highway": ["residential", "footway"], "length": 77.0}),   # 2e composante, attribut liste
    ]
    for u, v, d in aretes:
        d = {**d, "osmid": 1, "oneway": False, "reversed": False}
        if avec_motorroad and d["highway"] == "trunk":
            d["motorroad"] = "yes"
        g.add_edge(u, v, **d)
    return g


def test_standardisation_lambert93_et_composantes():
    noeuds, aretes = osm.standardiser_reseau(graphe(), **AUDIT)
    assert noeuds.crs.to_epsg() == 2154 and aretes.crs.to_epsg() == 2154
    principale = noeuds.set_index("node_id")["composante_principale"]
    assert bool(principale[1]) and not bool(principale[9])
    assert aretes.set_index(["u", "v"]).loc[(9, 10), "highway"] == "residential;footway"


def test_rc01_non_applicable_signale_les_trunk():
    noeuds, aretes = osm.standardiser_reseau(graphe(), **AUDIT)
    suivi = Suivi("RUN")
    _, propres, statut = osm.nettoyer_reseau(noeuds, aretes, suivi)
    journal = suivi.table()
    assert statut.startswith("non applicable")
    assert list(journal.loc[journal["regle_id"] == "RC-01", "niveau"]) == ["alerte"]
    assert len(propres) == len(aretes)                       # rien n'est retiré


def test_rc01_appliquee_si_tag_present():
    noeuds, aretes = osm.standardiser_reseau(graphe(avec_motorroad=True), **AUDIT)
    suivi = Suivi("RUN")
    _, propres, statut = osm.nettoyer_reseau(noeuds, aretes, suivi)
    assert statut == "appliquée"
    assert len(propres) == len(aretes) - 1                   # l'arête motorroad est rejetée


def test_busway_exclu_access_no_signale():
    noeuds, aretes = osm.standardiser_reseau(graphe(), **AUDIT)
    suivi = Suivi("RUN")
    _, propres, _ = osm.nettoyer_reseau(noeuds, aretes, suivi)
    journal = suivi.table().set_index("regle_id")
    assert journal.loc["RC-15", "niveau"] == "exclusion"     # busway, même avec access=no : une seule règle
    assert journal.loc["RC-16", "id_origine"] == "1-3-0"     # service access=no
    exclues = propres.loc[propres["statut_transformation"] == "exclu", "highway"]
    assert list(exclues) == ["busway"]
