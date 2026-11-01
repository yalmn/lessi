"""Gemeinsame Hilfen für die Skripte."""
import json
import os
import time
from pathlib import Path


def projekt():
    ordner = Path(os.environ.get("LESSI_WORKSPACE") or os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).expanduser().resolve()
    plugin = Path(__file__).resolve().parent.parent
    if ordner.is_relative_to(plugin):
        raise ValueError("Bitte einen eigenen Arbeitsordner außerhalb des installierten Plugins öffnen.")
    if not ordner.is_dir():
        raise ValueError("Der Arbeitsordner existiert nicht.")
    return ordner


def spur(lauf, schritt, ok, hinweis=""):
    """Eine Zeile pro Schritt, damit der Ablauf nachvollziehbar bleibt."""
    zeile = {
        "zeit": time.strftime("%Y-%m-%d %H:%M:%S"),
        "schritt": schritt,
        "ok": ok,
        "hinweis": hinweis,
    }
    with open(lauf / "ablauf.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(zeile, ensure_ascii=False) + "\n")
