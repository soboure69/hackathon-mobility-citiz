"""Journal d'exécution au format JSON Lines : un événement par ligne."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class Journal:
    """Écrit dans logs/<prefixe>_<run_id>.jsonl et affiche un résumé à l'écran."""

    def __init__(self, dossier_logs: Path | str, run_id: str, prefixe: str = "bronze") -> None:
        self.run_id = run_id
        self.chemin = Path(dossier_logs) / f"{prefixe}_{run_id}.jsonl"
        self.chemin.parent.mkdir(parents=True, exist_ok=True)

    def evenement(self, source_id: str, etape: str, statut: str, message: str, **details: object) -> None:
        ligne = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": self.run_id,
            "source_id": source_id,
            "etape": etape,
            "statut": statut,
            "message": message,
            "details": details,
        }
        with self.chemin.open("a", encoding="utf-8", newline="\n") as fichier:
            fichier.write(json.dumps(ligne, ensure_ascii=False, default=str) + "\n")
        print(f"[{statut:>6}] {source_id} {etape} : {message}")
