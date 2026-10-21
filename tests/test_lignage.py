"""Tests de l'écriture des tables Silver (CS-03, CS-04, CS-11) et de leur manifeste."""
import json

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

from src.utils.lignage import ecrire_table, mettre_a_jour_manifeste


def table_geo(crs=2154):
    return gpd.GeoDataFrame({"offre_id": ["b", "a"], "n": [2, 1]},
                            geometry=[Point(380000, 6570000), Point(380100, 6570100)], crs=crs)


def test_ecriture_reproductible(tmp_path):
    """CS-11 : même contenu → même empreinte, quel que soit l'ordre des lignes en entrée."""
    a = ecrire_table(table_geo(), tmp_path / "a.parquet", ["offre_id"])
    b = ecrire_table(table_geo().iloc[::-1], tmp_path / "b.parquet", ["offre_id"])
    assert a["sha256"] == b["sha256"]


def test_cle_non_unique_refusee(tmp_path):
    with pytest.raises(RuntimeError, match="CS-03"):
        ecrire_table(pd.DataFrame({"k": [1, 1]}), tmp_path / "t.parquet", ["k"])


def test_crs_autre_que_2154_refuse(tmp_path):
    with pytest.raises(RuntimeError, match="CS-04"):
        ecrire_table(table_geo(crs=4326), tmp_path / "t.parquet", ["offre_id"])


def test_manifeste_garde_les_autres_tables(tmp_path):
    mettre_a_jour_manifeste(tmp_path, "t1.parquet", {"run_id": "R1"})
    mettre_a_jour_manifeste(tmp_path, "t2.parquet", {"run_id": "R2"})
    mettre_a_jour_manifeste(tmp_path, "t1.parquet", {"run_id": "R3"})
    tables = json.loads((tmp_path / "_manifest.json").read_text(encoding="utf-8"))["tables"]
    assert tables == {"t1.parquet": {"run_id": "R3"}, "t2.parquet": {"run_id": "R2"}}
