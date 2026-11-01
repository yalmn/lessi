"""Baut aus den Ergebnisdateien eine Seite, die sich auf jedem Gerät öffnen lässt.

README.md zeigt GitHub beim Öffnen des Ordners direkt an, ergebnis.html ist für den Rechner.
"""
import html
import re
import sys

from gemeinsam import ablauf, aktueller_lauf, spur

SEITE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lessi</title>
<style>
body { font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 42rem;
       margin: 2rem auto; padding: 0 1rem; line-height: 1.5; color: #222; }
h2 { margin-top: 2.5rem; border-bottom: 1px solid #ddd; padding-bottom: .3rem; }
a { color: #0a58ca; word-break: break-all; }
.warnung { background: #fff3cd; border: 1px solid #e0c060; padding: .5rem 1rem; }
</style>
</head>
<body>
{{INHALT}}
</body>
</html>
"""


def zeile(text):
    text = html.escape(text)
    return re.sub(r"(https?://[^\s<]+)", r'<a href="\1">\1</a>', text)


def markdown(text):
    ausgabe, liste = [], False
    for roh in text.splitlines():
        s = roh.rstrip()
        if s.startswith("- "):
            if not liste:
                ausgabe.append("<ul>")
                liste = True
            ausgabe.append("<li>" + zeile(s[2:]) + "</li>")
            continue
        if liste:
            ausgabe.append("</ul>")
            liste = False
        treffer = re.match(r"(#{1,3}) (.*)", s)
        if treffer:
            stufe = len(treffer.group(1)) + 1
            ausgabe.append("<h%d>%s</h%d>" % (stufe, zeile(treffer.group(2)), stufe))
        elif s:
            ausgabe.append("<p>" + zeile(s) + "</p>")
    if liste:
        ausgabe.append("</ul>")
    return "\n".join(ausgabe)


lauf = aktueller_lauf()
if not lauf:
    sys.exit("Kein laufender Durchgang gefunden.")

letzter = {e["schritt"]: e for e in ablauf(lauf)}
warnungen = [
    "Achtung, Schritt \"%s\" ist nicht sauber durchgelaufen: %s" % (s, e["hinweis"])
    for s, e in letzter.items() if not e["ok"]
]
texte = [d.read_text(encoding="utf-8").strip() for d in sorted(lauf.glob("[0-9][0-9]_*.md"))]

kasten = ['<div class="warnung">' + "".join("<p>%s</p>" % html.escape(w) for w in warnungen) + "</div>"] if warnungen else []
seite = SEITE.replace("{{INHALT}}", "\n".join(kasten + [markdown(t) for t in texte]))
(lauf / "ergebnis.html").write_text(seite, encoding="utf-8")

kasten = ["\n\n".join("> **%s**" % w for w in warnungen)] if warnungen else []
(lauf / "README.md").write_text("\n\n---\n\n".join(kasten + texte) + "\n", encoding="utf-8")

spur(lauf, "bericht", True)
print(lauf / "ergebnis.html")
