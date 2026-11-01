# Lessi in Claude Code

Für Lehrkräfte reicht das Plugin `lessi` im normalen Chat, siehe README. Diese Seite beschreibt `lessi-code` mit getrennten Agenten für Claude Code.

Ein GitHub-Konto, eigener Fork oder manuelles Klonen ist für Lehrkräfte nicht nötig.
Das öffentliche Repository liefert nur das Plugin an Claude Code aus. Die Anmeldung
für Claude Code erfolgt mit dem eigenen Claude-Pro-Konto. GitHub-Anmeldungen oder
zusätzliche API-Schlüssel werden von Lessi nicht verlangt.

In einer Claude-Code-Sitzung:

```text
/plugin marketplace add yalmn/lessi
/plugin install lessi-code@lessi
```

Alternativ im Plugin-Menü den Marktplatz `yalmn/lessi` hinzufügen, `lessi` auswählen
und für die eigene Nutzung installieren. Falls Claude Code nach der Installation
ein Neuladen verlangt, der angezeigten Aufforderung folgen.

Die Sitzung benötigt Python 3.9 oder neuer, Webrecherche und verbundene Canva-Werkzeuge.
Am Rechner sind das lokale Softwarevoraussetzungen, keine zusätzlichen Konten.
Canva wird mit dem vorhandenen Canva-Konto verbunden. Fehlt eine Voraussetzung,
bleibt der jeweilige Schritt offen und nennt den konkreten Grund.

Das Plugin enthält Rollen, Skills und Python-Skripte. Seine Installation verbindet
Canva nicht automatisch. Der eigene Arbeitsordner kann leer sein; er muss kein
Git-Repository sein. Ergebnisse liegen unter `ergebnisse/`, außerhalb der installierten
Plugin-Dateien. Updates überschreiben dadurch keine Unterrichtsmaterialien.

# Benutzen

```text
/lessi-code:planen Gymnasium, NRW, Klasse 7, Spanisch, Thema: Familie, 45 Minuten
/lessi-code:review ergebnisse/<Lauf>
```

Der erste Befehl startet eine neue Planung. Der zweite setzt einen vorhandenen
Durchgang fort und nimmt die Entscheidung der Lehrkraft entgegen. Bearbeitungslinks
und PDF-Dateien werden am Ende übergeben. Kein automatischer Upload zu GitHub.

# Aktualisieren

Im Plugin-Menü den Marktplatz `lessi` aktualisieren und anschließend das installierte
Plugin aktualisieren. Den Marktplatz kannst du auch mit `/plugin marketplace update lessi` aktualisieren.
Anschließend unter `/plugin` das installierte Plugin auswählen und aktualisieren.

Automatische Updates können im Plugin-Menü für den Marktplatz aktiviert werden.

# Geräte

Diese Anleitung bezieht sich auf Claude Code. Ein Plugin im normalen Claude-Chat
ist nicht automatisch dieselbe Ausführungsumgebung. Ein vollständiger Durchlauf
auf einem iPad ist bislang nicht erprobt. Die öffentliche Marktplatzquelle ersetzt
keine möglicherweise weiterhin erforderliche Einrichtung der Code-Sitzung auf dem
jeweiligen Gerät. Insbesondere ist damit noch kein eigenständiger, GitHub-freier
Code-Web-Zugang auf dem iPad nachgewiesen.

# Entwicklung

Zum lokalen Testen, ohne das Paket zu veröffentlichen:

```sh
claude --plugin-dir ./plugins/lessi-code
claude plugin validate ./plugins/lessi-code
claude plugin validate .
python3 -m unittest discover -s tests
```

Für den Ablauf mit Agenten muss das Plugin `lessi-code` installiert sein. Die Namen
`/lessi-code:planen` und `/lessi-code:review` entstehen aus Pluginname und Skillname.
