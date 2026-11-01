# Lessi

Unterricht planen, Materialien in Canva gestalten und vor dem Einsatz prüfen.
Die letzte Freigabe gibst du selbst.

## Einmal einrichten

In Claude Code den Marktplatz hinzufügen und Lessi installieren:

```text
/plugin marketplace add yalmn/lessi
/plugin install lessi@lessi
```

Ein GitHub-Konto oder Fork ist nicht nötig. Du brauchst Claude Pro, eine
Code-Sitzung mit Python 3.9 oder neuer und eine dort verbundene
[Canva-Anbindung](docs/canva.md). Öffne einen eigenen Ordner für deine Materialien.

## Unterricht planen

```text
/lessi:planen Gymnasium, NRW, Klasse 7, Spanisch, Thema: Familie, 45 Minuten
```

Lessi erstellt Unterrichtsplan, Präsentation, Arbeitsblatt und separate Lösungen.
Nach den Reviews kannst du freigeben, Änderungen nennen oder zurückstellen.
Ergebnisse bleiben in deinem Arbeitsordner unter `ergebnisse/<Lauf>/`.
Mit `/lessi:review ergebnisse/<Lauf>` setzt du einen Durchgang fort.

Keine persönlichen Schülerdaten eingeben. Dateien werden nicht automatisch veröffentlicht.

[Ablauf und Einrichtung](docs/ablauf.md) · [Updates](docs/installation.md)
