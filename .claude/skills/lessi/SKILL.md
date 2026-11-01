---
name: lessi
description: Plant eine Unterrichtseinheit. Eingabe - Schulform, Bundesland, Klasse, Fach, Thema.
---

Eingabe der Lehrkraft: $ARGUMENTS

Ablauf, genau in dieser Reihenfolge:

1. Lauf anlegen, die Eingabe unverändert zwischen die beiden Zeilen:
   ```
   python3 scripts/neuer_lauf.py <<'EINGABE'
   $ARGUMENTS
   EINGABE
   ```
   Bricht das Skript mit einer Meldung ab, gib die Meldung unverändert wieder und höre auf.
2. Agent `recherche` aufrufen. Er liest den Laufordner (Pfad steht in `ergebnisse/.aktuell`) und schreibt `01_recherche.md`.
3. Agent `zusammenfassung` aufrufen. Er schreibt `99_zusammenfassung.md`.
4. Bericht bauen: `python3 scripts/bericht.py`
5. Ergebnis hochladen: `python3 scripts/abgeben.py`
6. Der Lehrkraft in höchstens drei Sätzen sagen, was entstanden ist. Die Ausgabe von Schritt 5 mit dem Link unverändert übernehmen.

Regeln:
- Keinen Schritt überspringen und keine Datei der Agenten selbst schreiben.
- Nichts selbst committen oder pushen, das erledigt Schritt 5.
- Meldet ein Prüfschritt einen Fehler, geht der Fehler an den Agenten zurück, nicht an die Lehrkraft.
- Nichts erfinden. Was unklar ist, bleibt als unklar markiert.
