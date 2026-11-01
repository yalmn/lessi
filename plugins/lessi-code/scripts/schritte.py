"""Schritte dieses Plugins. Der Ablauf selbst steht in ablauf.py."""

# Die Reihenfolge ist zugleich die Abhängigkeit: Änderungen machen Folgeschritte ungültig.
SCHRITTE = {
    "auftragsklaerung": ("01_auftrag.md", ["Rahmen", "Lerngruppe", "Materialien", "Annahmen"]),
    "lehrplanrecherche": ("02_lehrplan.md", ["Kompetenzen", "Fundstellen", "Offene Punkte"]),
    "fachrecherche": ("03_fachrecherche.md", ["Kernpunkte", "Belege", "Unsicher"]),
    "unterrichtsplanung": ("04_unterrichtsplan.md", ["Lernziele", "Stundenverlauf", "Lernkontrolle"]),
    "aufgabenentwicklung": ("05_aufgaben.md", ["Aufgaben", "Differenzierung", "Materialbedarf"]),
    "loesungsentwicklung": ("06_loesungen.md", ["Loesungen", "Erwartungshorizont"]),
    "fachreview": ("07_fachreview.json", []),
    "didaktikreview": ("08_didaktikreview.json", []),
    "canva-praesentation": ("09_praesentation.json", []),
    "canva-arbeitsblatt": ("10_arbeitsblatt.json", []),
    "materialreview": ("11_materialreview.json", []),
    "uebergabe": ("99_uebergabe.md", ["Materialien", "Pruefergebnisse", "Offene Punkte", "Freigabe"]),
}
ZIELE = {
    "fachreview": ["lehrplanrecherche", "fachrecherche", "unterrichtsplanung", "aufgabenentwicklung", "loesungsentwicklung"],
    "didaktikreview": ["auftragsklaerung", "unterrichtsplanung", "aufgabenentwicklung", "loesungsentwicklung"],
    "materialreview": ["canva-praesentation", "canva-arbeitsblatt"],
}
CANVA = ("canva-praesentation", "canva-arbeitsblatt")
# Schritte, deren Ergebnis Quellenlinks enthalten muss
QUELLEN = ("lehrplanrecherche", "fachrecherche")
