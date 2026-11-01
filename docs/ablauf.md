# Einrichtung

Lessi wird über den öffentlichen Marktplatz `yalmn/lessi` installiert. Ein
GitHub-Konto oder Fork ist für Lehrkräfte nicht nötig. Die Schritte stehen unter
[Installation](installation.md); Canva wird [separat verbunden](canva.md).

Ein eigener Arbeitsordner genügt. Die dort verwendete Claude-Code-Sitzung braucht
Python 3.9 oder neuer und Webzugriff. Unterrichtsmaterialien liegen außerhalb des
installierten Plugins und bleiben bei Updates erhalten.

# Zuständigkeiten

| Schritt | Ergebnis | Zuständigkeit |
| --- | --- | --- |
| Auftragsklärung | 01_auftrag.md | Rahmen und fehlende Angaben klären |
| Lehrplanrecherche | 02_lehrplan.md | Offizielle Kompetenzen belegen |
| Fachrecherche | 03_fachrecherche.md | Fachliche Inhalte mit Einzelbelegen sammeln |
| Unterrichtsplanung | 04_unterrichtsplan.md | Lernziele und Stundenverlauf planen |
| Aufgabenentwicklung | 05_aufgaben.md | Aufgaben und Differenzierung erstellen |
| Lösungsentwicklung | 06_loesungen.md | Lösungen und Erwartungshorizont erstellen |
| Fachreview | 07_fachreview.json | Inhalte und Quellen unabhängig prüfen |
| Didaktisches Review | 08_didaktikreview.json | Niveau, Lernziele und Zeit prüfen |
| Canva-Präsentation | 09_praesentation.json, PDF | Folien gestalten |
| Canva-Arbeitsblatt | 10_arbeitsblatt.json, PDFs | Schülerblatt und separate Lösungen gestalten |
| Materialreview | 11_materialreview.json | Alle fertigen Designs und Exporte visuell prüfen |
| Übergabe | 99_uebergabe.md | Bestehende Ergebnisse zur Entscheidung vorlegen |
| Lehrkraft-Review | lehrkraft_review.json | Ausdrückliche Entscheidung der Lehrkraft erfassen |

Der Koordinator verteilt Aufgaben und führt technische Prüfungen aus. Er schreibt
keine Unterrichtsinhalte, korrigiert keine Ergebnisse und erteilt keine Freigaben.
Die Rollenbegrenzung erfolgt über Agentenanweisungen; sie ist keine Dateisystem-Sandbox.

# Änderungen und Freigabe

Ein Review enthält `urteil`, konkrete Prüfergebnisse unter `geprueft` und `befunde`.
Bei `aenderungen` besteht jeder Befund aus `agent` und einem konkreten `auftrag`.
Der Ablauf springt zum frühesten betroffenen Erstellungsagenten zurück. Dieser
überarbeitet ausschließlich sein Ergebnis; die Folgeschritte werden erneut ausgeführt.
Nach wiederholten Problemen bleibt der Durchgang offen, statt Prüfungen zu überspringen.

Die technische Prüfung kontrolliert Struktur, Pflichtdateien, Exportpfade und die
Reihenfolge. Fachliche Richtigkeit und Layout werden von den jeweiligen Reviewern
beurteilt. Ein vorhandener Quellenlink oder PDF-Dateikopf beweist keine inhaltliche Qualität.

Am Ende bekommt die Lehrkraft Materialien, offene Punkte und die Version des
Pakets. Sie entscheidet ausdrücklich: freigeben, Änderungen anfordern oder
zurückstellen. Auch eine spätere Rücknahme der Freigabe oder eine Wiederaufnahme
ist mit einer neuen ausdrücklichen Entscheidung möglich. Nur `lehrkraft-review` erfasst diese Nachricht. Eine technische
Prüfung ersetzt keine menschliche Entscheidung.

Prüfquittungen und Freigabe beziehen sich auf Dateifingerabdrücke. Änderungen an
Eingabe, Ergebnissen, Reviews oder PDF-Exporten entwerten die betroffenen Folgeschritte
und die Freigabe. Lokale Dateien sind die prüfbare Momentaufnahme. Änderungen direkt
in Canva werden nicht automatisch erkannt: Nach jeder solchen Änderung müssen der
zuständige Gestaltungsagent neu exportieren und Materialreview sowie Lehrkraft-Review
erneut stattfinden. Ein Canva-Link allein hält keinen unveränderlichen Stand fest.

Eine Freigabe wird lokal dokumentiert, nicht als digitale Unterschrift einer
extern authentifizierten Person. Die Aufzeichnung setzt die ausdrückliche Nachricht
der Lehrkraft im Gespräch voraus.

# Durchgänge fortsetzen

Jeder Start erhält einen eindeutigen Ordner. Der konkrete Pfad wird bei jedem
Schritt weitergegeben; die zuletzt gestartete Sitzung bestimmt nicht den Lauf
anderer Sitzungen. Derselbe Lauf darf nicht gleichzeitig in mehreren Sitzungen
bearbeitet werden.

```text
/lessi-code:review ergebnisse/<Lauf>
```

Der Koordinator prüft jeden Arbeitsschritt mit den Python-Skripten im installierten
Plugin. Die Skripte werden über den absoluten Plugin-Pfad aufgerufen, während der
Arbeitsordner der Lehrkraft unverändert bleibt. Der Laufpfad ist bei jedem Aufruf
explizit angegeben.

Die Sitzung darf während Rückfragen, fehlenden Verbindungen oder beim Warten auf
die Lehrkraft enden. Dateien bleiben erhalten. Materialien werden als lokale Dateien
oder Downloads übergeben. Es gibt keinen automatischen Upload und keinen Grund,
Lehrkräfte nach einem GitHub-Konto zu fragen.

Keine persönlichen Daten verwenden. Der Eingabefilter erkennt nur einige
offensichtliche Muster und bietet keine zuverlässige Anonymisierung.

# Entwicklung

```sh
python3 -m unittest discover -s tests
```

Die Tests prüfen Reihenfolge, Rückgaben, Versionsbindung, getrennte Durchgänge und
Exportgrenzen. Reale Canva-Erstellung und Sichtprüfung müssen zusätzlich mit einem
verbundenen Lehrkraft-Konto erprobt werden.
