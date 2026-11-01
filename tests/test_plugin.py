"""Prüft das ausgelieferte Plugin unabhängig vom Entwickler-Repository."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / 'plugins' / 'lessi'
sys.path.insert(0, str(PLUGIN / 'scripts'))
from ablauf import SCHRITTE


class PluginTest(unittest.TestCase):
    def test_marktplatz_liefert_vollstaendiges_plugin(self):
        markt = json.loads((REPO / '.claude-plugin/marketplace.json').read_text())
        eintrag = next(p for p in markt['plugins'] if p['name'] == 'lessi')
        quelle = (REPO / eintrag['source']).resolve()
        self.assertEqual(quelle, PLUGIN)
        manifest = json.loads((quelle / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['name'], eintrag['name'])
        self.assertRegex(manifest['version'], r'^\d+\.\d+\.\d+$')
        for agent, (datei, _) in SCHRITTE.items():
            text = (quelle / 'agents' / (agent + '.md')).read_text()
            self.assertIn('name: ' + agent + '\n', text)
            self.assertIn(datei, text)
        self.assertTrue((quelle / 'agents/lehrkraft-review.md').is_file())
        for skill in ('planen', 'review'):
            text = (quelle / 'skills' / skill / 'SKILL.md').read_text()
            self.assertIn('name: ' + skill + '\n', text)
            self.assertIn('${CLAUDE_PLUGIN_ROOT}/scripts/', text)
            self.assertNotIn('python3 scripts/', text)
            self.assertNotIn('abgeben.py', text)

    def test_installierte_kopie_startet_ohne_repository_und_konten(self):
        with tempfile.TemporaryDirectory() as tmp:
            wurzel = Path(tmp)
            cache = wurzel / 'plugin cache' / 'lessi'
            shutil.copytree(PLUGIN, cache, ignore=shutil.ignore_patterns('__pycache__'))
            arbeit = wurzel / 'Mein Unterricht'
            arbeit.mkdir()
            env = {k: v for k, v in os.environ.items() if k not in (
                'CLAUDE_PROJECT_DIR', 'LESSI_WORKSPACE', 'GH_TOKEN', 'GITHUB_TOKEN', 'CLAUDE_PLUGIN_ROOT')}
            env['PYTHONDONTWRITEBYTECODE'] = '1'
            start = subprocess.run([sys.executable, str(cache / 'scripts/start.py')], cwd=arbeit, env=env, capture_output=True, text=True)
            self.assertEqual(start.returncode, 0, start.stderr)
            neu = subprocess.run([sys.executable, str(cache / 'scripts/neuer_lauf.py')], input='Gymnasium, NRW, Klasse 7, Spanisch, Thema: Familie', cwd=arbeit, env=env, capture_output=True, text=True)
            self.assertEqual(neu.returncode, 0, neu.stderr)
            lauf = neu.stdout.strip()
            status = subprocess.run([sys.executable, str(cache / 'scripts/workflow.py'), 'status', '--lauf', lauf], cwd=arbeit, env=env, capture_output=True, text=True)
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(json.loads(status.stdout)['agent'], 'auftragsklaerung')
            self.assertTrue((arbeit / lauf / '00_eingabe.md').is_file())
            self.assertFalse((cache / 'ergebnisse').exists())
            self.assertFalse((arbeit / '.git').exists())

    def test_plugin_cache_ist_kein_arbeitsordner(self):
        env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_PROJECT_DIR', 'LESSI_WORKSPACE')}
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        result = subprocess.run([sys.executable, str(PLUGIN / 'scripts/start.py')], cwd=PLUGIN, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Arbeitsordner außerhalb', result.stderr)
        self.assertFalse((PLUGIN / 'ergebnisse').exists())

    def test_keine_globalen_projekt_hooks_als_installationsvoraussetzung(self):
        # Installierte Plugins übernehmen nicht die .claude-Dateien des Quell-Repos.
        self.assertFalse((PLUGIN / '.claude').exists())
        self.assertFalse((REPO / '.claude/skills').exists())
        self.assertFalse((REPO / '.claude/agents').exists())
        self.assertTrue((PLUGIN / 'scripts/ablauf.py').is_file())


if __name__ == '__main__':
    unittest.main()
