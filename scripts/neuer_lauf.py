"""Legt den Ordner für einen neuen Durchgang an."""
import re
import sys
import time
import unicodedata

from gemeinsam import marker, projekt, spur


def kurzname(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:40].strip("-") or "lauf"


def thema(text):
    treffer = re.search(r"thema\s*:\s*(.+)", text, re.I)
    return treffer.group(1) if treffer else text.split(",")[-1]


# Eingabe kommt über stdin, damit Anführungszeichen im Thema die Shell nicht stören
eingabe = " ".join(sys.argv[1:]).strip()
if not eingabe and not sys.stdin.isatty():
    eingabe = sys.stdin.read().strip()

if not eingabe:
    sys.exit("Bitte angeben: Schulform, Bundesland, Klasse, Fach, Thema.")

# Grobe Sperre gegen versehentliche persönliche Daten
if re.search(r"@|\d{6,}", eingabe):
    sys.exit("Bitte keine E-Mail-Adressen, Telefonnummern oder Namen von Schülern eingeben.")

name = time.strftime("%Y-%m-%d_%H%M") + "_" + kurzname(thema(eingabe))
lauf = projekt() / "ergebnisse" / name
lauf.mkdir(parents=True, exist_ok=True)
(lauf / "00_eingabe.md").write_text("# Eingabe\n\n" + eingabe + "\n", encoding="utf-8")
marker().write_text("ergebnisse/" + name + "\n", encoding="utf-8")
spur(lauf, "eingang", True)

print("ergebnisse/" + name)
