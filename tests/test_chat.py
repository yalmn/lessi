"""Prüft das Chat-Plugin lessi über seine Skripte, wie es im Chat aufgerufen wird."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / 'plugins' / 'lessi' / 'skills' / 'planen'
CODE = REPO / 'plugins' / 'lessi-code' / 'scripts'
GEMEINSAM = ('ablauf.py', 'gemeinsam.py', 'neuer_lauf.py', 'workflow.py')

INHALT = {
    'auftragsklaerung': '## Rahmen\nGymnasium, NRW, Klasse 7, Spanisch, Familie, 45 Minuten\n## Lerngruppe\nZweites Lernjahr\n## Annahmen\nDauer 45 Minuten\n',
    'lehrplanrecherche': '## Kompetenzen\nÜber die eigene Familie sprechen\n## Fundstellen\n- Kernlehrplan Spanisch, https://example.org/klp\n## Offene Punkte\nnichts\n',
    'fachrecherche': '## Kernpunkte\n- la familia [1]\n## Belege\n[1] Wörterbuch, https://example.org/wb\n## Unsicher\nnichts\n',
    'unterrichtsplanung': '## Lernziele\n- Familienmitglieder benennen\n## Stundenverlauf\n| Zeit | Phase |\n|---|---|\n| 10 | Einstieg |\n| 35 | A1 |\n## Lernkontrolle\nKurze Abfrage\n',
    'aufgabenentwicklung': '## Aufgaben\n### A1 Mi familia\nBeschreibe deine Familie in drei Sätzen. Nutze <tener> & **ser**.\n## Differenzierung\nWortliste als Hilfe\n',
    'loesungsentwicklung': '## Loesungen\n### A1\nTengo dos hermanos.\n## Erwartungshorizont\nDrei korrekte Sätze\n',
}
REVIEW = {'urteil': 'freigegeben', 'geprueft': ['A1 und Beleg [1] geprüft'], 'befunde': []}


def word_text(pfad):
    with zipfile.ZipFile(pfad) as z:
        xml = z.read('word/document.xml')
    ET.fromstring(xml)  # muss gültiges XML sein
    return xml.decode('utf-8')


class ChatTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        wurzel = Path(tmp.name)
        # Im Chat liegt der Skill-Ordner getrennt vom Arbeitsordner
        self.skript = wurzel / 'skills' / 'planen' / 'scripts'
        shutil.copytree(SKILL, self.skript.parent, ignore=shutil.ignore_patterns('__pycache__'))
        self.arbeit = wurzel / 'arbeit'
        self.arbeit.mkdir()
        self.env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_PROJECT_DIR', 'LESSI_WORKSPACE')}
        self.env['PYTHONDONTWRITEBYTECODE'] = '1'

    def run_skript(self, name, *args, eingabe=None, ok=True):
        result = subprocess.run([sys.executable, str(self.skript / name), *args], input=eingabe,
                                cwd=self.arbeit, env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def status(self):
        return json.loads(self.run_skript('workflow.py', 'status', '--lauf', self.lauf).stdout)

    def schritt(self, agent):
        datei = json.loads(subprocess.run(
            [sys.executable, '-c', 'import json, schritte; print(json.dumps(schritte.SCHRITTE))'],
            cwd=self.skript, env=self.env, capture_output=True, text=True).stdout)[agent][0]
        text = json.dumps(REVIEW) if datei.endswith('.json') else INHALT[agent]
        (self.arbeit / self.lauf / datei).write_text(text, encoding='utf-8')
        self.run_skript('workflow.py', 'pruefen', '--lauf', self.lauf, '--agent', agent)

    def bis_fertig(self):
        self.lauf = self.run_skript('neuer_lauf.py', eingabe='Gymnasium, NRW, Klasse 7, Spanisch, Thema: Familie').stdout.strip()
        while self.status()['agent']:
            self.schritt(self.status()['agent'])
        self.assertEqual(self.status()['status'], 'wartet_auf_lehrkraft')

    def test_gemeinsame_skripte_sind_gleich(self):
        for name in GEMEINSAM:
            self.assertEqual((SKILL / 'scripts' / name).read_bytes(), (CODE / name).read_bytes(), name)

    def test_anleitung_nennt_jeden_schritt(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('name: planen\n', text)
        for agent, datei in (('auftragsklaerung', '01_auftrag.md'), ('fachreview', '07_fachreview.json'),
                             ('didaktikreview', '08_didaktikreview.json')):
            self.assertIn('**' + agent + '**', text)
            self.assertIn(datei, text)
        for skript in ('neuer_lauf.py', 'workflow.py', 'dokumente.py', 'canva.py'):
            self.assertIn('S/' + skript, text)
            self.assertTrue((SKILL / 'scripts' / skript).is_file())

    def test_keine_dokumente_vor_den_pruefungen(self):
        self.lauf = self.run_skript('neuer_lauf.py', eingabe='Gymnasium, NRW, Klasse 7, Spanisch, Thema: Familie').stdout.strip()
        for agent in ('auftragsklaerung', 'lehrplanrecherche', 'fachrecherche'):
            self.schritt(agent)
        result = self.run_skript('dokumente.py', '--lauf', self.lauf, ok=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Noch nicht alle Prüfungen', result.stderr)
        self.assertFalse((self.arbeit / self.lauf / 'Arbeitsblatt.docx').exists())

    def test_ganzer_durchgang(self):
        self.bis_fertig()
        lauf = self.arbeit / self.lauf
        self.run_skript('dokumente.py', '--lauf', self.lauf)
        plan, blatt, loesung = (word_text(lauf / n) for n in ('Unterrichtsplan.docx', 'Arbeitsblatt.docx', 'Loesungen.docx'))
        self.assertIn('<w:tbl>', plan)
        self.assertIn('Einstieg', plan)
        self.assertIn('Wortliste', plan)
        self.assertIn('Mi familia', blatt)
        self.assertIn('&lt;tener&gt; &amp; ', blatt)
        self.assertNotIn('Tengo dos hermanos', blatt)
        self.assertNotIn('Wortliste', blatt)
        self.assertIn('Tengo dos hermanos', loesung)
        self.assertIn('Entwurf', plan)

        version = self.status()['version']
        entscheidung = json.dumps({'entscheidung': 'freigegeben', 'version': version, 'nachricht': 'Passt so, danke.'})
        self.run_skript('workflow.py', 'lehrkraft', '--lauf', self.lauf, eingabe=entscheidung)
        self.run_skript('dokumente.py', '--lauf', self.lauf)
        self.assertNotIn('Entwurf', word_text(lauf / 'Arbeitsblatt.docx'))

    def test_canva_link_gehoert_zum_stand(self):
        self.lauf = self.run_skript('neuer_lauf.py', eingabe='Gymnasium, NRW, Klasse 7, Spanisch, Thema: Familie').stdout.strip()
        folien = json.dumps({'design_id': 'DAF1', 'bearbeitungslink': 'https://www.canva.com/design/DAF1/edit', 'seiten': 6})
        self.assertEqual(self.run_skript('canva.py', '--lauf', self.lauf, eingabe=folien, ok=False).returncode, 2)

        self.lauf = None
        self.bis_fertig()
        for falsch in ({'design_id': 'DAF1', 'bearbeitungslink': 'https://canva.example.org/design/DAF1/edit', 'seiten': 6},
                       {'design_id': 'DAF1', 'bearbeitungslink': 'https://www.canva.com/design/ANDERE/edit', 'seiten': 6},
                       {'design_id': 'DAF1', 'bearbeitungslink': 'https://www.canva.com/design/DAF1/edit', 'seiten': 0}):
            self.assertEqual(self.run_skript('canva.py', '--lauf', self.lauf, eingabe=json.dumps(falsch), ok=False).returncode, 2)
        self.run_skript('canva.py', '--lauf', self.lauf, eingabe=folien)
        self.run_skript('dokumente.py', '--lauf', self.lauf)
        self.assertIn('https://www.canva.com/design/DAF1/edit', word_text(self.arbeit / self.lauf / 'Unterrichtsplan.docx'))

        # Ein Änderungswunsch macht den alten Folienlink ungültig
        befunde = [{'agent': 'unterrichtsplanung', 'auftrag': 'Einstieg auf 5 Minuten kürzen'}]
        self.run_skript('workflow.py', 'lehrkraft', '--lauf', self.lauf, eingabe=json.dumps(
            {'entscheidung': 'aenderungen', 'version': self.status()['version'], 'nachricht': 'Einstieg kürzer bitte', 'befunde': befunde}))
        self.assertEqual(self.status()['agent'], 'unterrichtsplanung')
        INHALT_ALT = INHALT['unterrichtsplanung']
        INHALT['unterrichtsplanung'] = INHALT_ALT.replace('| 10 | Einstieg |\n| 35 | A1 |', '| 5 | Einstieg |\n| 40 | A1 |')
        self.addCleanup(INHALT.__setitem__, 'unterrichtsplanung', INHALT_ALT)
        while self.status()['agent']:
            self.schritt(self.status()['agent'])
        self.run_skript('dokumente.py', '--lauf', self.lauf)
        self.assertNotIn('canva.com', word_text(self.arbeit / self.lauf / 'Unterrichtsplan.docx'))


if __name__ == '__main__':
    unittest.main()
