---
name: planen
description: Koordiniert Unterrichtsplanung, getrennte Reviews und Canva-Materialien bis zur Entscheidung der Lehrkraft.
---

Eingabe der Lehrkraft: $ARGUMENTS

Du koordinierst ausschließlich. Inhalte, Gestaltung, Reviews und Lehrkraft-Review übernehmen die jeweils benannten Agenten. Keine Ergebnisdatei selbst schreiben oder korrigieren.

1. Prüfe zunächst `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/start.py"`. Bei einer fehlenden Voraussetzung den konkreten Fehler weitergeben und warten. Übergib anschließend die Eingabe der Lehrkraft unverändert über stdin an `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/neuer_lauf.py"`. Nutze eine temporäre Textdatei oder eine sichere Werkzeugübergabe. Keine Nutzereingaben in Shell-Befehle oder feste Heredoc-Begrenzer interpolieren.
2. Behalte den ausgegebenen Laufpfad für den gesamten Durchgang. Jeder Aufruf erhält diesen Pfad ausdrücklich. Keinen globalen Marker lesen.
3. Rufe `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/workflow.py" status --lauf <Laufordner>` auf.
4. Delegiere ausschließlich an den unter `agent` genannten Agenten dieses Plugins: `lessi:<agent>`. Der Status nennt den Rollenbezeichner ohne Präfix; bei `--agent` ebenfalls nur diesen Rollenbezeichner verwenden. Gib Laufpfad und noch offene Rückmeldungen mit. Die Rollen stehen in `${CLAUDE_PLUGIN_ROOT}/agents/`, die feste Reihenfolge in `${CLAUDE_PLUGIN_ROOT}/scripts/ablauf.py`.
5. Hat der Agent sein Ergebnis geschrieben, führe `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/workflow.py" pruefen --lauf <Laufordner> --agent <Agent>` aus. Das ist eine technische Prüfung; die fachlichen, didaktischen und visuellen Reviews sind eigene Schritte.
6. Wiederhole ab Schritt 3. Ein Review mit Änderungsbedarf setzt den Ablauf auf den zuständigen Erstellungsagenten zurück. Betroffene Folgeschritte einschließlich Reviews werden erneut ausgeführt. Reviewer korrigieren keine Inhalte.
7. Braucht ein Agent Angaben der Lehrkraft, gib seine Rückfrage weiter und warte. Bei fehlendem Canva-Zugriff oder anderen Blockaden den konkreten Grund weitergeben und den Durchgang offen lassen. Nach drei erfolglosen Versuchen am selben Problem pausieren und Hilfe anfordern; niemals einen Schritt als bestanden behandeln.
8. Sobald `wartet_auf_lehrkraft` erreicht ist, baue `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bericht.py" --lauf <Laufordner>`. Zeige Materiallinks, lokale Exporte, Berichtspfad, offene Punkte, Laufpfad und die vollständige `version` aus dem Status. Bitte die Lehrkraft ausdrücklich um Freigabe, Änderungswünsche oder Zurückstellung. Dann warten.
9. Eine neue ausdrückliche Entscheidung wird ausschließlich an `lessi:lehrkraft-review` delegiert, mit dem zuvor vorgelegten Lauf und Versionswert. Vor einer Freigabe niemals „final einsetzbar“ melden.
10. Nach Änderungswünschen ab Schritt 3 fortfahren. Nach Freigabe oder Zurückstellung den Bericht neu bauen und den Status zurückgeben. Gib die vorhandenen Dateien zum Öffnen oder Herunterladen aus. Kein GitHub-Konto verlangen, nichts committen, pushen oder automatisch veröffentlichen.

Das installierte Plugin liegt unter `${CLAUDE_PLUGIN_ROOT}`. Dieser Pfad wird in dieser Anweisung bereits aufgelöst; im Bash-Prozess muss keine gleichnamige Umgebungsvariable existieren. Skripte immer über diesen absoluten Pfad aufrufen, im gewählten Arbeitsordner bleiben und nie in das Plugin-Verzeichnis wechseln. Ergebnisse gehören ausschließlich in den Arbeitsordner, nicht in den Plugin-Cache.

Bei jeder Fortsetzung zuerst den Status prüfen. Nie einen erledigten Schritt aus Dateiexistenz ableiten. Keine Inhalte, Links, Canva-Zugriffe oder Freigaben erfinden. Keine zusätzlichen Autorennamen, Herkunftsvermerke oder Co-Autoren-Zeilen ergänzen.
