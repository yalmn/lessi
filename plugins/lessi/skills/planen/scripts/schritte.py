"""Schritte im Chat. Gleiche Namen und Dateien wie in lessi-code, ohne Canva und Übergabe."""

# Die Reihenfolge ist zugleich die Abhängigkeit: Änderungen machen Folgeschritte ungültig.
SCHRITTE = {
    "auftragsklaerung": ("01_auftrag.md", ["Rahmen", "Lerngruppe", "Annahmen"]),
    "lehrplanrecherche": ("02_lehrplan.md", ["Kompetenzen", "Fundstellen", "Offene Punkte"]),
    "fachrecherche": ("03_fachrecherche.md", ["Kernpunkte", "Belege", "Unsicher"]),
    "unterrichtsplanung": ("04_unterrichtsplan.md", ["Lernziele", "Stundenverlauf", "Lernkontrolle"]),
    "aufgabenentwicklung": ("05_aufgaben.md", ["Aufgaben", "Differenzierung"]),
    "loesungsentwicklung": ("06_loesungen.md", ["Loesungen", "Erwartungshorizont"]),
    "fachreview": ("07_fachreview.json", []),
    "didaktikreview": ("08_didaktikreview.json", []),
}
ZIELE = {
    "fachreview": ["lehrplanrecherche", "fachrecherche", "unterrichtsplanung", "aufgabenentwicklung", "loesungsentwicklung"],
    "didaktikreview": ["auftragsklaerung", "unterrichtsplanung", "aufgabenentwicklung", "loesungsentwicklung"],
}
CANVA = ()
# Schritte, deren Ergebnis Quellenlinks enthalten muss
QUELLEN = ("lehrplanrecherche", "fachrecherche")
