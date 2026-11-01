"""Prüft das Ergebnis eines Agenten. Bei einem Fehler (Exit 2) muss der Agent nachbessern."""
import re
import sys

from gemeinsam import aktueller_lauf, fehlversuche, spur

DATEIEN = {
    "recherche": "01_recherche.md",
    "zusammenfassung": "99_zusammenfassung.md",
}
ABSCHNITTE = {
    "recherche": ["## Kernpunkte", "## Unsicher"],
    "zusammenfassung": ["## Was entstanden ist", "## Offene Punkte"],
}
MAX_VERSUCHE = 3  # danach geht es weiter, der Bericht zeigt den Fehler an


def fehler_finden(agent, datei):
    if not datei.exists():
        return datei.name + " fehlt."
    text = datei.read_text(encoding="utf-8")
    for abschnitt in ABSCHNITTE[agent]:
        if abschnitt not in text:
            return "Der Abschnitt '" + abschnitt + "' fehlt."
    if agent == "recherche":
        treffer = re.search(r"^Quellen:\s*$(.*)", text, re.S | re.M)
        if not treffer or not re.search(r"^- https?://\S+", treffer.group(1), re.M):
            return "Unter 'Quellen:' fehlt mindestens ein Link (Zeile '- https://...')."
    return None


agent = sys.argv[1] if len(sys.argv) > 1 else ""
lauf = aktueller_lauf()

if not lauf or agent not in DATEIEN:
    sys.exit(0)

fehler = fehler_finden(agent, lauf / DATEIEN[agent])

if not fehler:
    spur(lauf, agent, True)
    sys.exit(0)

if fehlversuche(lauf, agent) + 1 >= MAX_VERSUCHE:
    spur(lauf, agent, False, "aufgegeben nach %d Versuchen: %s" % (MAX_VERSUCHE, fehler))
    sys.exit(0)

spur(lauf, agent, False, fehler)
print("Prüfung fehlgeschlagen: " + fehler, file=sys.stderr)
sys.exit(2)
