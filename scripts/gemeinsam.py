"""Gemeinsame Hilfen für die Skripte."""
import json
import os
import time
from pathlib import Path


def projekt():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parent.parent)


def marker():
    return projekt() / "ergebnisse" / ".aktuell"


def aktueller_lauf():
    """Ordner des laufenden Durchgangs, sonst None."""
    if not marker().exists():
        return None
    ordner = projekt() / marker().read_text(encoding="utf-8").strip()
    return ordner if ordner.is_dir() else None


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


def ablauf(lauf):
    datei = lauf / "ablauf.jsonl"
    if not datei.exists():
        return []
    return [json.loads(z) for z in datei.read_text(encoding="utf-8").splitlines() if z.strip()]


def fehlversuche(lauf, schritt):
    """Fehlschläge eines Schritts seit seinem letzten Erfolg."""
    anzahl = 0
    for eintrag in ablauf(lauf):
        if eintrag["schritt"] == schritt:
            anzahl = 0 if eintrag["ok"] else anzahl + 1
    return anzahl
