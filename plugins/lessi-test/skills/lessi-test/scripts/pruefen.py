"""Prüft eine Recherche-Datei. Gibt OK aus oder den ersten Fehler."""
import re
import sys

ABSCHNITTE = ["## Kernpunkte", "## Unsicher"]


def fehler_finden(text):
    for abschnitt in ABSCHNITTE:
        if abschnitt not in text:
            return "Der Abschnitt '" + abschnitt + "' fehlt."
    treffer = re.search(r"^Quellen:\s*$(.*)", text, re.S | re.M)
    if not treffer or not re.search(r"^- https?://\S+", treffer.group(1), re.M):
        return "Unter 'Quellen:' fehlt mindestens ein Link (Zeile '- https://...')."
    return None


if len(sys.argv) != 2:
    sys.exit("Aufruf: python3 pruefen.py <datei>")

try:
    text = open(sys.argv[1], encoding="utf-8").read()
except OSError:
    sys.exit("Fehler: Datei " + sys.argv[1] + " nicht gefunden.")

fehler = fehler_finden(text)
if fehler:
    sys.exit("Fehler: " + fehler)
print("OK")
