"""Erstellt eine Übersicht mit aktuellem Status und allen Materiallinks."""
import argparse
import html
import sys

from urllib.parse import quote, urlparse

from ablauf import CANVA, SCHRITTE, dateien, designs, lesen, status
from gemeinsam import projekt


def bauen(lauf):
    stand = status(lauf)
    titel = {
        "in_arbeit": "In Arbeit – noch nicht freigegeben",
        "wartet_auf_lehrkraft": "Entwurf – wartet auf das Review der Lehrkraft",
        "freigegeben": "Von der Lehrkraft freigegeben",
        "zurueckgestellt": "Von der Lehrkraft zurückgestellt",
    }[stand["status"]]
    materialien = []
    for agent in CANVA:
        pfad = lauf / SCHRITTE[agent][0]
        if not pfad.exists():
            continue
        try:
            exporte = dateien(lauf, agent)[1:]
            for design in designs(lesen(pfad), agent):
                url = design.get("bearbeitungslink", "")
                if urlparse(url).scheme == "https" and urlparse(url).hostname in ("canva.com", "www.canva.com"):
                    materialien.append((agent, url))
            materialien.extend((p.name, quote(p.relative_to(lauf).as_posix(), safe="/")) for p in exporte)
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    teile = ["# Unterrichtspaket", "**" + titel + "**", "Version: " + stand["version"]]
    if stand["agent"]:
        teile.append("Nächster Schritt: " + stand["agent"])
    if materialien:
        teile.append("## Materiallinks\n\n" + "\n".join("- [" + name + "](" + url + ")" for name, url in materialien))
    for name in ["00_eingabe.md"] + [s[0] for s in SCHRITTE.values()]:
        pfad = lauf / name
        if pfad.is_file():
            text = pfad.read_text(encoding="utf-8").strip()
            teile.append("## " + name + "\n\n" + ("```json\n" + text + "\n```" if pfad.suffix == ".json" else text))
    text = "\n\n---\n\n".join(teile) + "\n"
    (lauf / "README.md").write_text(text, encoding="utf-8")
    # Markdown bleibt im Original verfügbar; HTML zeigt denselben Stand ohne
    # ungeprüfte HTML-Fragmente oder automatisch erzeugte Fremdlinks.
    seite = '''<!doctype html><html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Unterrichtspaket</title>
<style>body{font-family:system-ui;max-width:60rem;margin:2rem auto;padding:1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>
<body><h1>Unterrichtspaket</h1><p>Bearbeitbare Materialien und PDF-Dateien stehen im Abschnitt Materialien der Übergabe.</p><pre>'''
    if materialien:
        links = "<ul>" + "".join('<li><a href="' + html.escape(url, quote=True) + '">' + html.escape(name) + '</a></li>' for name, url in materialien) + "</ul>"
        seite = seite.removesuffix("<pre>") + links + "<pre>"
    seite += html.escape(text) + "</pre></body></html>\n"
    (lauf / "ergebnis.html").write_text(seite, encoding="utf-8")
    return lauf / "ergebnis.html"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lauf", required=True)
    args = parser.parse_args()
    lauf = (projekt() / args.lauf).resolve()
    if not lauf.is_relative_to((projekt() / "ergebnisse").resolve()):
        raise ValueError("Ungültiger Laufordner.")
    print(bauen(lauf))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
