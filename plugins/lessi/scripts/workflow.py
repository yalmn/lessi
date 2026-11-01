"""Status, technische Prüfungen und ausdrücklich erteiltes Lehrkraft-Review."""
import argparse
import json
import sys
from pathlib import Path

from ablauf import SCHRITTE, lehrkraft, pruefen, status
from gemeinsam import projekt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("aktion", choices=["status", "pruefen", "lehrkraft"])
    parser.add_argument("--lauf", required=True)
    parser.add_argument("--agent", choices=list(SCHRITTE))
    args = parser.parse_args()
    lauf = (projekt() / args.lauf).resolve()
    if not lauf.is_relative_to((projekt() / "ergebnisse").resolve()) or not (lauf / "00_eingabe.md").is_file():
        raise ValueError("Kein gültiger Laufordner.")
    if args.aktion == "pruefen":
        if not args.agent:
            raise ValueError("Agent fehlt.")
        pruefen(lauf, args.agent)
    elif args.aktion == "lehrkraft":
        daten = json.load(sys.stdin)
        lehrkraft(lauf, daten["entscheidung"], daten["version"], daten["nachricht"], daten.get("befunde"))
    print(json.dumps(status(lauf), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
