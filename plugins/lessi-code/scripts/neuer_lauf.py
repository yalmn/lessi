"""Legt einen eigenen Ordner für jeden Durchgang an."""
import re
import sys
import time
import unicodedata
import uuid

from gemeinsam import projekt, spur


def kurzname(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:40].strip("-") or "lauf"


def main():
    eingabe = " ".join(sys.argv[1:]).strip()
    if not eingabe and not sys.stdin.isatty():
        eingabe = sys.stdin.read().strip()
    if not eingabe:
        sys.exit("Bitte angeben: Schulform, Bundesland, Klasse, Fach, Thema.")
    if re.search(r"@|\d{6,}", eingabe):
        sys.exit("Bitte keine persönlichen Daten eingeben.")
    treffer = re.search(r"thema\s*:\s*(.+)", eingabe, re.I)
    thema = treffer.group(1) if treffer else eingabe.split(",")[-1]
    name = time.strftime("%Y-%m-%d_%H%M%S") + "_" + kurzname(thema) + "_" + uuid.uuid4().hex[:12]
    lauf = projekt() / "ergebnisse" / name
    lauf.mkdir(parents=True)
    (lauf / "00_eingabe.md").write_text("# Eingabe\n\n" + eingabe + "\n", encoding="utf-8")
    spur(lauf, "eingang", True)
    print("ergebnisse/" + name)


if __name__ == "__main__":
    main()
