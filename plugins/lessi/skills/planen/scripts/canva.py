"""Hält die geprüften Canva-Folien zu einem Stand fest, oder warum es keine gibt. Angaben als JSON über stdin."""
import argparse
import json
import re
import sys
from urllib.parse import urlparse

from ablauf import lesen, schreiben, status
from gemeinsam import projekt, spur

DATEI = "09_praesentation.json"
FERTIG = ("wartet_auf_lehrkraft", "freigegeben", "zurueckgestellt")


def folien_pruefen(angaben):
    ident = angaben.get("design_id")
    if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", ident):
        raise ValueError("Eine echte Canva-Design-ID fehlt.")
    url = urlparse(str(angaben.get("bearbeitungslink", "")))
    if url.scheme != "https" or url.hostname not in ("canva.com", "www.canva.com") or not url.path.startswith("/design/" + ident + "/"):
        raise ValueError("Ein passender Canva-Bearbeitungslink fehlt.")
    seiten = angaben.get("seiten")
    if not isinstance(seiten, int) or isinstance(seiten, bool) or seiten < 1:
        raise ValueError("Die Folienzahl fehlt.")
    pruefung = angaben.get("pruefung")
    if not isinstance(pruefung, dict) or pruefung.get("urteil") != "freigegeben":
        raise ValueError("Die Folien brauchen eine bestandene Prüfung. Mängel erst in Canva beheben.")
    geprueft = pruefung.get("geprueft")
    if not isinstance(geprueft, list) or not all(isinstance(g, str) and g.strip() for g in geprueft):
        raise ValueError("Die Prüfung braucht unter geprueft konkrete Ergebnisse.")
    # Jede Folie muss einzeln angesehen worden sein
    if len(geprueft) < seiten:
        raise ValueError("Für jede Folie wird ein eigenes Prüfergebnis gebraucht (%d von %d)." % (len(geprueft), seiten))
    return {"design_id": ident, "bearbeitungslink": angaben["bearbeitungslink"], "seiten": seiten, "geprueft": geprueft}


def festhalten(lauf, angaben):
    stand = status(lauf)
    if stand["status"] not in FERTIG:
        raise ValueError("Die Folien erst bauen, wenn alle Prüfungen bestanden sind.")
    if not isinstance(angaben, dict):
        raise ValueError("Ein JSON-Objekt wird erwartet.")
    if "ohne" in angaben:
        grund = angaben["ohne"]
        if not isinstance(grund, str) or len(grund.strip()) < 15:
            raise ValueError("Bitte konkret angeben, warum es keine Folien gibt.")
        eintrag = {"ohne": grund.strip()}
    else:
        eintrag = folien_pruefen(angaben)
    eintrag["version"] = stand["version"]
    schreiben(lauf / DATEI, eintrag)
    spur(lauf, "praesentation", "ohne" not in eintrag, eintrag.get("ohne", eintrag.get("design_id")))
    return eintrag


def aktuelle(lauf):
    """Eintrag zu den Folien, wenn er zum aktuellen Stand gehört."""
    eintrag = lesen(lauf / DATEI)
    if eintrag and eintrag.get("version") == status(lauf)["version"]:
        return eintrag
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lauf", required=True)
    args = parser.parse_args()
    lauf = (projekt() / args.lauf).resolve()
    if not lauf.is_relative_to((projekt() / "ergebnisse").resolve()) or not (lauf / "00_eingabe.md").is_file():
        raise ValueError("Kein gültiger Laufordner.")
    print(json.dumps(festhalten(lauf, json.load(sys.stdin)), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
