"""Macht aus einer Markdown-Datei ein Word-Dokument, nur mit der Standardbibliothek."""
import sys
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

DOKUMENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>{}<w:sectPr/></w:body>
</w:document>"""


def absatz(text, fett=False, groesse=24):
    # groesse in halben Punkt, 24 entspricht 12 pt
    stil = "<w:rPr>%s<w:sz w:val=\"%d\"/></w:rPr>" % ("<w:b/>" if fett else "", groesse)
    return "<w:p><w:r>%s<w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % (stil, escape(text))


def umwandeln(zeilen):
    teile = []
    for zeile in zeilen:
        s = zeile.rstrip()
        if s.startswith("```"):
            continue
        if s.startswith("# "):
            teile.append(absatz(s[2:], True, 36))
        elif s.startswith("## "):
            teile.append(absatz(s[3:], True, 28))
        elif s.startswith("- "):
            teile.append(absatz("• " + s[2:]))
        elif s:
            teile.append(absatz(s))
    return "".join(teile)


if len(sys.argv) != 3:
    sys.exit("Aufruf: python3 arbeitsblatt.py <eingabe.md> <ausgabe.docx>")

try:
    zeilen = open(sys.argv[1], encoding="utf-8").read().splitlines()
except OSError:
    sys.exit("Fehler: Datei " + sys.argv[1] + " nicht gefunden.")

with zipfile.ZipFile(sys.argv[2], "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", INHALTSTYPEN)
    z.writestr("_rels/.rels", BEZIEHUNGEN)
    z.writestr("word/document.xml", DOKUMENT.format(umwandeln(zeilen)))
print(sys.argv[2])
