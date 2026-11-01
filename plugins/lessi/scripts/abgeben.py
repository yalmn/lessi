"""Veröffentlicht auf ausdrücklichen Wunsch ein freigegebenes Paket."""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import quote

from ablauf import status
from bericht import bauen
from gemeinsam import projekt


def git(*argumente, umgebung=None):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", **(umgebung or {}))
    ergebnis = subprocess.run(["git", *argumente], cwd=projekt(), env=env,
                              capture_output=True, text=True, timeout=60)
    if ergebnis.returncode != 0:
        raise RuntimeError(ergebnis.stderr.strip())
    return ergebnis.stdout.strip()


def hauptbranch():
    try:
        return git("symbolic-ref", "--short", "refs/remotes/origin/HEAD").split("/", 1)[1]
    except (RuntimeError, IndexError):
        return "main"


def link(branch, ordner):
    remote = git("remote", "get-url", "origin")
    treffer = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?/?", remote)
    if not treffer:
        return None
    return "https://github.com/%s/%s/tree/%s/%s" % (
        treffer.group(1), treffer.group(2), quote(branch, safe=""), quote(ordner, safe="/"))


def abgeben(lauf):
    stand = status(lauf)
    if stand["status"] != "freigegeben":
        raise ValueError("Nur ein von der Lehrkraft freigegebenes Paket darf veröffentlicht werden.")
    # Die konfigurierte Identität verwenden, niemals einen zusätzlichen Autor anlegen.
    if not git("config", "user.name") or not git("config", "user.email"):
        raise ValueError("Bitte zuerst die eigene Git-Identität konfigurieren.")
    bauen(lauf)
    ordner = lauf.relative_to(projekt()).as_posix()
    branch = hauptbranch()
    with tempfile.TemporaryDirectory() as tmp:
        index = {"GIT_INDEX_FILE": os.path.join(tmp, "index")}
        git("fetch", "origin", branch)
        basis = git("rev-parse", "FETCH_HEAD")
        git("read-tree", basis, umgebung=index)
        git("add", "--", ordner, umgebung=index)
        baum = git("write-tree", umgebung=index)
        # Nach dem Einlesen nochmals prüfen: veränderte Materialien benötigen ein neues Review.
        aktuell = status(lauf)
        if aktuell["status"] != "freigegeben" or aktuell["version"] != stand["version"]:
            raise ValueError("Materialien wurden inzwischen verändert. Erneutes Review erforderlich.")
        commit = git("commit-tree", baum, "-p", basis, "-m", "Unterrichtspaket " + lauf.name)
        git("push", "origin", commit + ":refs/heads/" + branch)
    return "Veröffentlicht: " + (link(branch, ordner) or ordner)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lauf", required=True)
    args = parser.parse_args()
    lauf = (projekt() / args.lauf).resolve()
    if not lauf.is_relative_to((projekt() / "ergebnisse").resolve()):
        raise ValueError("Ungültiger Laufordner.")
    print(abgeben(lauf))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as e:
        print("Nicht veröffentlicht: " + str(e), file=sys.stderr)
        sys.exit(2)
