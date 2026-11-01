# Canva verbinden

Die Canva-Verbindung muss in derselben Sitzung verfügbar sein, in der Lessi läuft.
Eine Verbindung im normalen Chat allein reicht dafür nicht.

1. Canva nach der [offiziellen Einrichtungsanleitung](https://www.canva.com/help/mcp-agent-setup/)
   mit dem verwendeten Client verbinden und im eigenen Konto autorisieren.
2. In der Code-Sitzung prüfen, ob die Canva-Werkzeuge tatsächlich verfügbar sind.
   Bei Claude Code zeigt `/mcp` die eingerichteten Verbindungen.
3. Einen vorhandenen Entwurf lesend öffnen lassen. Erst danach mit der Erstellung starten.

Die [Canva-Dokumentation](https://www.canva.dev/docs/apps/mcp/) beschreibt Erstellung,
Bearbeitung und Exporte. Welche Funktionen verfügbar sind, hängt von Verbindung,
Berechtigungen und Konto ab. Lessi installiert keine Verbindung automatisch und
speichert keine Zugangsdaten im Repository.

# Materialien

Es entstehen drei getrennte Designs:

- Präsentation mit PDF-Export aller Folien.
- Schülerarbeitsblatt mit eigenem PDF-Export.
- Lösungen für die Lehrkraft mit eigenem PDF-Export.

Jeder Gestaltungsschritt speichert die echten Design-IDs, Bearbeitungslinks,
Seitenzahlen und lokalen PDF-Pfade in seinem Manifest. Keine kurzlebigen
Download-URLs oder Freigaben für zusätzliche Personen speichern.

Das Materialreview muss die tatsächlichen Designs und alle PDF-Seiten öffnen und
prüfen können. Ohne diesen Zugriff bleibt es offen. Die Lehrkraft erhält die
Bearbeitungslinks und die geprüften PDF-Dateien zur abschließenden Entscheidung.

Direkte Änderungen in Canva nach einem Review erfordern neue Exporte und erneute
Reviews. Im ersten Probelauf insbesondere Seitenumbrüche, Schriften, Schreibplatz,
Lösungstrennung und Zugriff mit dem Konto der Lehrkraft prüfen.
