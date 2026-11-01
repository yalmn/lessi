"""Beim Beenden: lässt die Sitzung erst enden, wenn alle Pflichtdateien vorliegen."""
import sys

from abgeben import abgeben, schon_abgegeben
from gemeinsam import aktueller_lauf, marker, spur

PFLICHT = ["00_eingabe.md", "01_recherche.md", "99_zusammenfassung.md", "ergebnis.html", "README.md"]
MAX_SPERREN = 3  # danach endet die Sitzung trotzdem, damit nichts hängen bleibt


def abschliessen(lauf, ok, hinweis=""):
    # Auch ein unvollständiger Durchgang wird hochgeladen, damit die Lehrkraft ihn sieht
    if not schon_abgegeben(lauf):
        abgeben(lauf)
    spur(lauf, "ende", ok, hinweis)
    marker().unlink()
    sys.exit(0)


lauf = aktueller_lauf()
if not lauf:
    sys.exit(0)

fehlt = [n for n in PFLICHT if not (lauf / n).exists()]

if not fehlt:
    abschliessen(lauf, True)

zaehler = lauf / ".sperren"
versuche = int(zaehler.read_text()) if zaehler.exists() else 0

if versuche >= MAX_SPERREN:
    abschliessen(lauf, False, "unvollständig: " + ", ".join(fehlt))

zaehler.write_text(str(versuche + 1))
print("Ablauf nicht abgeschlossen. Es fehlt: " + ", ".join(fehlt), file=sys.stderr)
sys.exit(2)
