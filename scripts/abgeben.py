"""Lädt den Ordner des Durchgangs auf den Hauptbranch, damit er auf dem iPad über GitHub erreichbar ist."""
import os
import re
import subprocess
import sys
import tempfile

from gemeinsam import ablauf, aktueller_lauf, projekt, spur

AUTOR = {
    "GIT_AUTHOR_NAME": "Lessi", "GIT_AUTHOR_EMAIL": "lessi@invalid",
    "GIT_COMMITTER_NAME": "Lessi", "GIT_COMMITTER_EMAIL": "lessi@invalid",
}


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
    treffer = re.search(r"[/:]([^/:]+)/([^/]+?)(?:\.git)?/?$", git("remote", "get-url", "origin"))
    if not treffer:
        return None
    return "https://github.com/%s/%s/tree/%s/%s" % (treffer.group(1), treffer.group(2), branch, ordner)


def hochladen(lauf, ordner, branch):
    # Eigener Index auf dem aktuellen Stand des Hauptbranchs, der Arbeitsbranch der Sitzung bleibt unberührt
    with tempfile.TemporaryDirectory() as tmp:
        index = {"GIT_INDEX_FILE": os.path.join(tmp, "index")}
        git("fetch", "origin", branch)
        basis = git("rev-parse", "FETCH_HEAD")
        git("read-tree", basis, umgebung=index)
        git("add", "--", ordner, umgebung=index)
        baum = git("write-tree", umgebung=index)
        commit = git("commit-tree", baum, "-p", basis, "-m", "Ergebnis " + lauf.name, umgebung=AUTOR)
        git("push", "origin", commit + ":refs/heads/" + branch)


def abgeben(lauf):
    ordner = lauf.relative_to(projekt()).as_posix()
    if os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        return "Fertig. Alles liegt in " + ordner + ", zum Ansehen ergebnis.html öffnen."

    branch = hauptbranch()
    # Vorab eintragen, damit die Zeile mit hochgeladen wird
    spur(lauf, "abgabe", True)
    fehler = ""
    for _ in range(3):
        try:
            hochladen(lauf, ordner, branch)
            break
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            fehler = str(e)
    else:
        spur(lauf, "abgabe", False, fehler)
        return "Das Hochladen zu GitHub hat nicht geklappt. Die Dateien liegen nur in dieser Sitzung in " + ordner + "."

    # Sonst committet die Sitzung dieselben Dateien noch einmal auf ihren eigenen Branch
    ausschluss = projekt() / git("rev-parse", "--git-dir") / "info" / "exclude"
    ausschluss.parent.mkdir(exist_ok=True)
    with open(ausschluss, "a", encoding="utf-8") as f:
        f.write("/" + ordner + "/\n")

    try:
        adresse = link(branch, ordner)
    except RuntimeError:
        adresse = None
    return "Fertig. Alles auf einer Seite: " + (adresse or "auf GitHub im Ordner " + ordner)


def schon_abgegeben(lauf):
    letzte = [e for e in ablauf(lauf) if e["schritt"] == "abgabe"]
    return bool(letzte) and letzte[-1]["ok"]


if __name__ == "__main__":
    lauf = aktueller_lauf()
    if not lauf:
        sys.exit("Kein laufender Durchgang gefunden.")
    print(abgeben(lauf))
