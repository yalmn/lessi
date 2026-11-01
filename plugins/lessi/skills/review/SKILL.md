---
name: review
description: Setzt einen bestehenden Durchgang fort und nimmt das abschließende Review der Lehrkraft entgegen.
---

Angaben der Lehrkraft: $ARGUMENTS

Du koordinierst ausschließlich. Verwende den von der Lehrkraft genannten Laufpfad. Fehlt er, frage danach; niemals einen globalen Marker als Ersatz benutzen.

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/workflow.py" status --lauf <Laufordner>` aufrufen.
2. Ist ein `agent` offen, nach den Regeln von `/lessi:planen` genau diesen Agenten mit Präfix `lessi:` aufrufen; bei `--agent` den Rollenbezeichner ohne Präfix verwenden, prüfen und fortsetzen. Bei einer Blockade oder Rückfrage darf die Sitzung enden, ohne einen Schritt freizugeben.
3. Bei `freigegeben` oder `zurueckgestellt` den aktuellen Status zurückgeben. Liegt eine neue ausdrückliche Entscheidung zum vorgelegten Stand vor, diese an `lessi:lehrkraft-review` delegieren; Änderungswünsche können eine frühere Freigabe zurücknehmen.
4. Bei `wartet_auf_lehrkraft` den Bericht bauen und das Paket mit vollständiger Version vorlegen. Nur eine neue ausdrückliche Entscheidung zum vorgelegten Stand an `lessi:lehrkraft-review` weitergeben. Fehlt die vorher vorgelegte Version im Gespräch, erst das aktuelle Paket vorlegen und warten.
5. Nach Änderungen den geregelten Ablauf samt Reviews wiederholen. Nach einer Entscheidung den Bericht aktualisieren. Nichts automatisch veröffentlichen.

Die Agenten dürfen weder die Entscheidung der Lehrkraft vorwegnehmen noch eigene Freigaben als Lehrkraftentscheidung erfassen.

Alle Skripte über den absoluten Plugin-Pfad `${CLAUDE_PLUGIN_ROOT}` aufrufen. Im Arbeitsordner der Lehrkraft bleiben; nie in den Plugin-Cache wechseln. Kein GitHub-Konto, Repository oder Fork anfordern. Materialien als lokale Dateien oder Downloads übergeben.
