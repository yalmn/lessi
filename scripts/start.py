"""Beim Sitzungsstart: Ordner anlegen, Voraussetzungen prüfen."""
import json
import sys

from gemeinsam import marker, projekt

if sys.version_info < (3, 8):
    print("Python ist zu alt. Bitte Python 3.8 oder neuer verwenden.", file=sys.stderr)
    sys.exit(1)

(projekt() / "ergebnisse").mkdir(exist_ok=True)

try:
    quelle = "" if sys.stdin.isatty() else json.load(sys.stdin).get("source", "")
except (ValueError, AttributeError):
    quelle = ""

# Ein Durchgang aus einer abgebrochenen Sitzung würde sonst das Beenden blockieren
if quelle in ("startup", "clear") and marker().exists():
    marker().unlink()

print("Lessi ist bereit. Start mit: /lessi Schulform, Bundesland, Klasse, Fach, Thema")
