"""Mesures de l'application (équivalent Python des mesures DAX de powerbi/measures_dax.md).

Mêmes règles : une mesure de couverture porte sur un seul mode ; une valeur non additive
(habitants gagnés par un site seul, population à 5 min d'une offre) n'est jamais sommée ;
les mesures de scénario lisent les KPI calculés en Gold, sans les recalculer autrement.
"""
from __future__ import annotations

import pandas as pd

MODES_VALIDES = {"tous", "bus", "citiz", "velo"}


def _communes(table: pd.DataFrame, communes: list[str] | None, colonne: str = "commune_insee") -> pd.DataFrame:
    return table if not communes else table[table[colonne].isin(communes)]


def couverture(acces_mode: pd.DataFrame, cellules: pd.DataFrame, mode: str,
               communes: list[str] | None = None) -> dict[str, float]:
    """Population desservie / non desservie, taux et options par habitant, pour UN mode (K1 à K4)."""
    if mode not in MODES_VALIDES:
        raise ValueError(f"mode inconnu : {mode}")
    ids = _communes(cellules, communes)["cell_id"]
    f = acces_mode[(acces_mode["mode"] == mode) & acces_mode["cell_id"].isin(ids)]
    desservie = float(f.loc[f["desservi"], "pop"].sum())
    non = float(f.loc[~f["desservi"], "pop"].sum())
    total = desservie + non
    return {"pop_desservie": desservie, "pop_non_desservie": non, "pop_totale": total,
            "taux": desservie / total if total else float("nan"),
            "options_par_habitant": float((f["pop"] * f["n_options"]).sum() / total) if total else float("nan")}


def pop_sans_option(cellules: pd.DataFrame, communes: list[str] | None = None) -> float:
    c = _communes(cellules, communes)
    return float(c.loc[~c["desservi_tous"], "pop"].sum())


def taux_quintiles(equite: pd.DataFrame, mode: str) -> pd.DataFrame:
    e = equite[equite["mode"] == mode]
    g = e.groupby("quintile", as_index=False)[["pop", "pop_desservie"]].sum()
    g["taux"] = g["pop_desservie"] / g["pop"]
    return g


def ecart_q1_q5(equite: pd.DataFrame, mode: str) -> float:
    """Écart de couverture, en points, entre le quintile 1 (modeste) et le quintile 5."""
    t = taux_quintiles(equite, mode).set_index("quintile")["taux"]
    return 100 * (float(t["1"]) - float(t["5"]))


def scenario(scenarios: pd.DataFrame, budget: str, hypothese_cout: str, variante: str) -> pd.Series | None:
    """Ligne du scénario choisi, ou None si la combinaison n'existe pas (équité hors coût central)."""
    s = scenarios[(scenarios["scenario"] == budget) & (scenarios["hypothese_cout"] == hypothese_cout)
                  & (scenarios["variante"] == variante)]
    if len(s) > 1:
        raise ValueError("plusieurs scénarios pour une même combinaison")
    return None if s.empty else s.iloc[0]


def reference(scenarios: pd.DataFrame) -> pd.Series:
    r = scenarios[scenarios["est_reference"]]
    if len(r) != 1:
        raise ValueError("il faut exactement un scénario de référence")
    return r.iloc[0]


def variante_equite(scenarios: pd.DataFrame, sc: pd.Series) -> pd.Series | None:
    """Variante équité du même budget et du même coût, si elle existe."""
    e = scenarios[scenarios["scenario_reference"] == sc["scenario_id"]]
    return None if e.empty else e.iloc[0]


def gain_points(avant: float, apres: float) -> float:
    return 100 * (float(apres) - float(avant))


def part_conformes(qualite: pd.DataFrame) -> float:
    """Part des indicateurs « ok » parmi ceux qui ont un seuil (ok + alerte) ; les « info » sont exclus."""
    ok = int((qualite["statut"] == "ok").sum())
    alerte = int((qualite["statut"] == "alerte").sum())
    return ok / (ok + alerte) if ok + alerte else float("nan")


def controles(acces_mode: pd.DataFrame, cellules: pd.DataFrame, kpi_territoire: pd.DataFrame,
              scenarios: pd.DataFrame, cellules_gagnees: pd.DataFrame, selection: pd.DataFrame) -> pd.DataFrame:
    """Recoupements application / Python : chaque écart doit valoir 0."""
    lignes = []
    for mode in sorted(MODES_VALIDES):
        app = couverture(acces_mode, cellules, mode)["taux"]
        gold = float(kpi_territoire.loc[kpi_territoire["mode"] == mode, "taux_couverture"].iloc[0])
        lignes.append({"controle": f"Taux de couverture {mode} : application − Gold", "ecart": app - gold})
    k6 = scenarios.set_index("scenario_id")["k6"]
    gagne = cellules_gagnees.groupby("scenario_id")["pop"].sum().reindex(k6.index).fillna(0)
    marginal = selection.groupby("scenario_id")["pop_nouvelle_marginale"].sum().reindex(k6.index).fillna(0)
    lignes.append({"controle": "Σ carreaux gagnés − K6 (pire scénario)", "ecart": float((gagne - k6).abs().max())})
    lignes.append({"controle": "Σ gains marginaux − K6 (pire scénario)", "ecart": float((marginal - k6).abs().max())})
    d = pd.DataFrame(lignes)
    d["ok"] = d["ecart"].abs() < 1e-6
    return d
