"""Schritte, Abhängigkeiten und Freigaben eines Unterrichtspakets."""
import hashlib
import json
import re
from urllib.parse import urlparse

from schritte import CANVA, QUELLEN, SCHRITTE, ZIELE


def lesen(pfad, standard=None):
    return json.loads(pfad.read_text(encoding="utf-8")) if pfad.exists() else standard


def schreiben(pfad, daten):
    tmp = pfad.with_suffix(pfad.suffix + ".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(pfad)


def designs(inhalt, agent):
    if not isinstance(inhalt, dict):
        raise ValueError("Ein Canva-Manifest wird erwartet.")
    result = [inhalt]
    if agent == "canva-arbeitsblatt":
        loesungen = inhalt.get("loesungen")
        if not isinstance(loesungen, dict):
            raise ValueError("Das separate Lösungsdesign fehlt.")
        if loesungen.get("design_id") == inhalt.get("design_id"):
            raise ValueError("Schüler- und Lösungsseiten brauchen getrennte Designs.")
        result.append(loesungen)
    return result


def dateien(lauf, agent):
    datei = lauf / SCHRITTE[agent][0]
    result = [datei]
    if agent in CANVA:
        for design in designs(lesen(datei), agent):
            exporte = design.get("exporte")
            if not isinstance(exporte, list) or not exporte:
                raise ValueError("Mindestens ein lokaler PDF-Export pro Design fehlt.")
            for name in exporte:
                if not isinstance(name, str):
                    raise ValueError("Exportpfade müssen Text sein.")
                pfad = lauf / name
                if pfad.is_symlink() or not pfad.resolve().is_relative_to(lauf.resolve()):
                    raise ValueError("Exporte müssen im Laufordner liegen und dürfen keine Verknüpfungen sein.")
                if not pfad.is_file():
                    raise ValueError("Export fehlt: " + name)
                pfad = pfad.resolve()
                if pfad in result:
                    raise ValueError("Jedes Design braucht einen eigenen Export.")
                result.append(pfad)
    return result


def signatur(lauf, agent, vorher):
    h = hashlib.sha256(vorher.encode())
    for datei in dateien(lauf, agent):
        if datei.is_symlink():
            raise ValueError("Ergebnisdateien dürfen keine Verknüpfungen sein.")
        # Beide Seiten auflösen, sonst scheitert der Vergleich etwa an /var und /private/var auf macOS
        h.update(datei.resolve().relative_to(lauf.resolve()).as_posix().encode())
        h.update(datei.read_bytes())
    return h.hexdigest()


def zustand(lauf):
    daten = lesen(lauf / "status.json", {"schritte": {}, "freigabe": None})
    vorher = hashlib.sha256((lauf / "00_eingabe.md").read_bytes()).hexdigest()
    gueltig = {}
    for agent in SCHRITTE:
        try:
            wert = signatur(lauf, agent, vorher)
        except (OSError, ValueError, TypeError, AttributeError):
            break
        if daten["schritte"].get(agent) != wert:
            break
        gueltig[agent] = wert
        vorher = wert
    if gueltig != daten["schritte"]:
        daten["schritte"] = gueltig
        daten["freigabe"] = None
    return daten, vorher


def verwerfen(daten, agent):
    index = list(SCHRITTE).index(agent)
    for name in list(SCHRITTE)[index:]:
        daten["schritte"].pop(name, None)
    daten["freigabe"] = None


def status(lauf):
    daten, version = zustand(lauf)
    schreiben(lauf / "status.json", daten)
    naechster = next((a for a in SCHRITTE if a not in daten["schritte"]), None)
    freigabe = daten.get("freigabe")
    if naechster:
        return {"status": "in_arbeit", "agent": naechster, "version": version}
    if freigabe and freigabe.get("version") == version:
        return {"status": freigabe["entscheidung"], "agent": None, "version": version}
    return {"status": "wartet_auf_lehrkraft", "agent": None, "version": version}


def pruefen(lauf, agent):
    daten, vorher = zustand(lauf)
    naechster = next((a for a in SCHRITTE if a not in daten["schritte"]), None)
    if agent != naechster:
        raise ValueError("Nächster Schritt: " + str(naechster or "Lehrkraft-Review"))
    datei, abschnitte = SCHRITTE[agent]
    pfad = lauf / datei
    if pfad.is_symlink():
        raise ValueError("Ergebnisdateien dürfen keine Verknüpfungen sein.")
    text = pfad.read_text(encoding="utf-8")
    if abschnitte:
        for titel in abschnitte:
            treffer = re.search(r"^## " + re.escape(titel) + r"\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
            if not treffer or not treffer.group(1).strip():
                raise ValueError("Abschnitt fehlt oder ist leer: " + titel)
        if agent in QUELLEN and not re.search(r"https?://\S+", text):
            raise ValueError("Quellenlinks fehlen.")
    else:
        inhalt = json.loads(text)
        if not isinstance(inhalt, dict):
            raise ValueError("Ein JSON-Objekt wird erwartet.")
        if agent in ZIELE:
            befunde = inhalt.get("befunde")
            urteil = inhalt.get("urteil")
            if urteil not in ("freigegeben", "aenderungen") or not isinstance(befunde, list):
                raise ValueError("Review braucht urteil und befunde.")
            if urteil == "freigegeben" and befunde:
                raise ValueError("Offene Befunde verhindern die Freigabe.")
            if urteil == "aenderungen":
                rueckgabe(lauf, daten, befunde, ZIELE[agent], agent)
                return False
            if not isinstance(inhalt.get("geprueft"), list) or not inhalt["geprueft"] or not all(isinstance(p, str) and p.strip() for p in inhalt["geprueft"]):
                raise ValueError("Review muss konkrete Prüfergebnisse unter geprueft aufführen.")
        elif agent in CANVA:
            for design in designs(inhalt, agent):
                url = urlparse(design.get("bearbeitungslink", ""))
                ident = design.get("design_id", "")
                if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", ident):
                    raise ValueError("Eine echte Canva-Design-ID fehlt.")
                if url.scheme != "https" or url.hostname not in ("canva.com", "www.canva.com") or not url.path.startswith("/design/" + ident + "/"):
                    raise ValueError("Ein passender Canva-Bearbeitungslink fehlt.")
                if not isinstance(design.get("seiten"), int) or isinstance(design["seiten"], bool) or design["seiten"] < 1:
                    raise ValueError("Die Seitenzahl fehlt.")
            for export in dateien(lauf, agent)[1:]:
                if export.suffix.lower() != ".pdf" or not export.read_bytes().startswith(b"%PDF-"):
                    raise ValueError("Ein PDF-Export wird benötigt: " + export.name)
    daten["schritte"][agent] = signatur(lauf, agent, vorher)
    daten["freigabe"] = None
    schreiben(lauf / "status.json", daten)
    return True


def rueckgabe(lauf, daten, befunde, erlaubt, quelle):
    if not befunde:
        raise ValueError("Mindestens ein konkreter Änderungsauftrag ist nötig.")
    for befund in befunde:
        if not isinstance(befund, dict) or befund.get("agent") not in erlaubt or not isinstance(befund.get("auftrag"), str) or not befund["auftrag"].strip():
            raise ValueError("Jeder Befund braucht einen zuständigen Agenten und einen Auftrag.")
    ziel = min((b["agent"] for b in befunde), key=list(SCHRITTE).index)
    historie = lesen(lauf / "rueckmeldungen.json", [])
    historie.append({"quelle": quelle, "befunde": befunde})
    schreiben(lauf / "rueckmeldungen.json", historie)
    verwerfen(daten, ziel)
    schreiben(lauf / "status.json", daten)


def lehrkraft(lauf, entscheidung, version, nachricht, befunde=None):
    aktuell = status(lauf)
    if aktuell["status"] not in ("wartet_auf_lehrkraft", "freigegeben", "zurueckgestellt") or version != aktuell["version"]:
        raise ValueError("Dieser Stand steht nicht zur Freigabe. Aktuellen Status prüfen.")
    if entscheidung not in ("freigegeben", "aenderungen", "zurueckgestellt") or not nachricht.strip():
        raise ValueError("Entscheidung und unveränderte Nachricht der Lehrkraft fehlen.")
    daten, _ = zustand(lauf)
    if entscheidung == "aenderungen":
        rueckgabe(lauf, daten, befunde, list(SCHRITTE), "lehrkraft")
    else:
        daten["freigabe"] = {"entscheidung": entscheidung, "version": version, "nachricht": nachricht}
        schreiben(lauf / "status.json", daten)
    historie = lesen(lauf / "lehrkraft_review.json", [])
    historie.append({"entscheidung": entscheidung, "version": version, "nachricht": nachricht, "befunde": befunde or []})
    schreiben(lauf / "lehrkraft_review.json", historie)
