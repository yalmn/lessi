"""Baut Unterrichtsplan, Arbeitsblatt und Lösungen, aber nur aus geprüften Ergebnissen."""
import argparse
import re
import sys
import time

from ablauf import status
from canva import FERTIG, aktuelle
from gemeinsam import projekt, spur
import word


def abschnitt(lauf, datei, titel):
    text = (lauf / datei).read_text(encoding="utf-8")
    treffer = re.search(r"^## " + re.escape(titel) + r"\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    inhalt = treffer.group(1).strip() if treffer else ""
    # "nichts" ist für die Prüfung nötig, im Dokument aber überflüssig
    return "" if inhalt.lower().strip("-*. ") in ("nichts", "keine") else inhalt


def kopf(titel, eingabe):
    return word.absatz(titel, True, 36, abstand=60) + word.absatz(eingabe, groesse=20, abstand=240, farbe="555555")


def teil(titel, text):
    return word.absatz(titel, True, 26, abstand=120) + word.umwandeln(text) if text.strip() else ""


def bauen(lauf):
    stand = status(lauf)
    if stand["status"] not in FERTIG:
        raise ValueError("Noch nicht alle Prüfungen bestanden. Nächster Schritt: " + str(stand["agent"]))

    eingabe = (lauf / "00_eingabe.md").read_text(encoding="utf-8").replace("# Eingabe", "").strip()
    vermerk = "Fachlich und didaktisch geprüft am %s, Stand %s." % (time.strftime("%d.%m.%Y"), stand["version"][:8])
    if stand["status"] != "freigegeben":
        vermerk += " Entwurf: Bitte vor dem Einsatz selbst durchsehen."
    folien = aktuelle(lauf)
    fuss = word.absatz("", abstand=240) + word.absatz(vermerk, groesse=16, farbe="777777")

    plan = "".join([
        kopf("Unterrichtsplan", eingabe),
        teil("Präsentation", "- Folien in Canva: " + folien) if folien else "",
        teil("Rahmen", abschnitt(lauf, "01_auftrag.md", "Rahmen")),
        teil("Lerngruppe", abschnitt(lauf, "01_auftrag.md", "Lerngruppe")),
        teil("Lernziele", abschnitt(lauf, "04_unterrichtsplan.md", "Lernziele")),
        teil("Stundenverlauf", abschnitt(lauf, "04_unterrichtsplan.md", "Stundenverlauf")),
        teil("Lernkontrolle", abschnitt(lauf, "04_unterrichtsplan.md", "Lernkontrolle")),
        teil("Differenzierung", abschnitt(lauf, "05_aufgaben.md", "Differenzierung")),
        teil("Lehrplanbezug", abschnitt(lauf, "02_lehrplan.md", "Kompetenzen")),
        teil("Fachlicher Hintergrund", abschnitt(lauf, "03_fachrecherche.md", "Kernpunkte")),
        teil("Quellen", abschnitt(lauf, "02_lehrplan.md", "Fundstellen") + "\n" + abschnitt(lauf, "03_fachrecherche.md", "Belege")),
        teil("Annahmen", abschnitt(lauf, "01_auftrag.md", "Annahmen")),
        teil("Bitte prüfen", abschnitt(lauf, "02_lehrplan.md", "Offene Punkte") + "\n" + abschnitt(lauf, "03_fachrecherche.md", "Unsicher")),
        fuss,
    ])
    blatt = "".join([
        kopf("Arbeitsblatt", eingabe),
        word.absatz("Name: ______________________    Datum: ____________", abstand=240),
        word.umwandeln(abschnitt(lauf, "05_aufgaben.md", "Aufgaben"), linien_nach_aufgabe=4),
        fuss,
    ])
    loesungen = "".join([
        kopf("Lösungen", eingabe),
        word.umwandeln(abschnitt(lauf, "06_loesungen.md", "Loesungen")),
        teil("Erwartungshorizont", abschnitt(lauf, "06_loesungen.md", "Erwartungshorizont")),
        fuss,
    ])

    dateien = []
    for name, inhalt in (("Unterrichtsplan.docx", plan), ("Arbeitsblatt.docx", blatt), ("Loesungen.docx", loesungen)):
        word.speichern(lauf / name, inhalt)
        dateien.append(lauf / name)
    spur(lauf, "dokumente", True, stand["status"])
    return dateien


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lauf", required=True)
    args = parser.parse_args()
    lauf = (projekt() / args.lauf).resolve()
    if not lauf.is_relative_to((projekt() / "ergebnisse").resolve()) or not (lauf / "00_eingabe.md").is_file():
        raise ValueError("Kein gültiger Laufordner.")
    for pfad in bauen(lauf):
        print(pfad)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
