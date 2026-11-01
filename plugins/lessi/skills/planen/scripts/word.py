"""Schreibt einfache Word-Dateien aus Markdown, nur mit der Standardbibliothek."""
import re
import zipfile
from xml.sax.saxutils import escape

INHALTSTYPEN = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

BEZIEHUNGEN = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

# A4 mit 2 cm Rand, Maße in Twip
DOKUMENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>{}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="709" w:footer="709" w:gutter="0"/></w:sectPr></w:body>
</w:document>"""

SCHRIFT = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>'
RAHMEN = "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="999999"/>' % s
                 for s in ("top", "left", "bottom", "right", "insideH", "insideV"))


def text_laeufe(text, fett=False, groesse=22, farbe=None):
    # groesse in halben Punkt, 22 entspricht 11 pt
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1 (\2)", text)
    laeufe = []
    for teil in re.split(r"(\*\*.+?\*\*|\*[^*\s][^*]*\*)", text):
        if not teil:
            continue
        stil = SCHRIFT
        if fett or teil.startswith("**"):
            stil += "<w:b/>"
        elif teil.startswith("*") and teil.endswith("*") and len(teil) > 2:
            stil += "<w:i/>"
        if farbe:
            stil += '<w:color w:val="%s"/>' % farbe
        laeufe.append('<w:r><w:rPr>%s<w:sz w:val="%d"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'
                      % (stil, groesse, escape(teil.strip("*") if teil.startswith("*") and len(teil) > 2 else teil)))
    return "".join(laeufe)


def absatz(text, fett=False, groesse=22, einzug=0, abstand=80, farbe=None):
    eigenschaften = '<w:pPr><w:spacing w:after="%d"/>%s</w:pPr>' % (
        abstand, '<w:ind w:left="%d" w:hanging="240"/>' % einzug if einzug else "")
    return "<w:p>%s%s</w:p>" % (eigenschaften, text_laeufe(text, fett, groesse, farbe))


def schreiblinien(anzahl):
    # Unterstriche statt Rahmen: Die Systemvorschau auf iPad und Mac zeigt Rahmen leerer Zellen nicht an
    linie = absatz("_" * 74, abstand=160, farbe="999999")
    return linie * anzahl + absatz("", abstand=120)


def tabelle(zeilen):
    xml = []
    for nummer, zellen in enumerate(zeilen):
        xml.append("<w:tr>" + "".join(
            '<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/></w:tcPr>%s</w:tc>' % absatz(z, fett=nummer == 0, groesse=20, abstand=0)
            for z in zellen) + "</w:tr>")
    return ('<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblBorders>%s</w:tblBorders></w:tblPr>%s</w:tbl>'
            % (RAHMEN, "".join(xml))) + absatz("", abstand=0)


def umwandeln(text, linien_nach_aufgabe=0):
    """Markdown in Word-Absätze. Optional Schreiblinien nach jedem ### Abschnitt."""
    teile, tabellenzeilen, offene_aufgabe = [], [], False

    def aufgabe_schliessen():
        if offene_aufgabe and linien_nach_aufgabe:
            teile.append(schreiblinien(linien_nach_aufgabe))

    for zeile in text.splitlines() + [""]:
        s = zeile.strip()
        if s.startswith("|"):
            zellen = [z.strip() for z in s.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", z) for z in zellen):
                tabellenzeilen.append(zellen)
            continue
        if tabellenzeilen:
            breite = max(len(z) for z in tabellenzeilen)
            teile.append(tabelle([z + [""] * (breite - len(z)) for z in tabellenzeilen]))
            tabellenzeilen = []
        if not s or s.startswith("```"):
            continue
        treffer = re.match(r"(#{1,4}) (.*)", s)
        if treffer:
            stufe = len(treffer.group(1))
            if stufe >= 3:
                aufgabe_schliessen()
                offene_aufgabe = True
            teile.append(absatz(treffer.group(2), True, {1: 32, 2: 26}.get(stufe, 23), abstand=120))
        elif re.match(r"[-*] ", s):
            teile.append(absatz("• " + s[2:], einzug=360))
        else:
            teile.append(absatz(s))
    aufgabe_schliessen()
    return "".join(teile)


def speichern(pfad, inhalt_xml):
    with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", INHALTSTYPEN)
        z.writestr("_rels/.rels", BEZIEHUNGEN)
        z.writestr("word/document.xml", DOKUMENT.format(inhalt_xml))
