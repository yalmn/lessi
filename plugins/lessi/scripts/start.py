"""Prüft Voraussetzungen im gewählten Arbeitsordner."""
import sys
from gemeinsam import projekt

if sys.version_info < (3, 9):
    sys.exit("Bitte Python 3.9 oder neuer verwenden.")
try:
    (projekt() / "ergebnisse").mkdir(exist_ok=True)
except (OSError, ValueError) as e:
    sys.exit(str(e))
print("Lessi ist bereit. Start mit /lessi:planen; Fortsetzen mit /lessi:review.")
