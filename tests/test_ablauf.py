import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'plugins' / 'lessi-code' / 'scripts'))
from ablauf import SCHRITTE, ZIELE, CANVA, lehrkraft, pruefen, schreiben, status
from abgeben import abgeben
from bericht import bauen


class AblaufTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.lauf = self.root / 'ergebnisse' / 'testlauf'
        self.lauf.mkdir(parents=True)
        (self.lauf / '00_eingabe.md').write_text('Gymnasium, NRW, Klasse 7, Spanisch, Familie', encoding='utf-8')

    def design(self, ident, name):
        # Nur ein Dateikopf für Strukturtests; kein echter, visuell geprüfter Export.
        (self.lauf / name).write_bytes(b'%PDF-1.7\nTestfixture\n')
        return {'design_id': ident, 'bearbeitungslink': 'https://www.canva.com/design/' + ident + '/edit',
                'seiten': 1, 'exporte': [name]}

    def ergebnis(self, agent):
        datei, abschnitte = SCHRITTE[agent]
        if abschnitte:
            text = '\n'.join('## ' + a + '\nKonkreter Inhalt zu ' + a + '\n' for a in abschnitte)
            text += '\nQuelle: https://example.org/lehrplan\n'
            (self.lauf / datei).write_text(text, encoding='utf-8')
        elif agent in ZIELE:
            schreiben(self.lauf / datei, {'urteil': 'freigegeben', 'geprueft': ['Testbefund'], 'befunde': []})
        elif agent in CANVA:
            if agent == 'canva-praesentation':
                daten = self.design('Folien', 'folien.pdf')
            else:
                daten = self.design('Blatt', 'blatt.pdf')
                daten['loesungen'] = self.design('Loesungen', 'loesungen.pdf')
            schreiben(self.lauf / datei, daten)

    def bis(self, grenze=None):
        for agent in SCHRITTE:
            if agent == grenze:
                return
            self.ergebnis(agent)
            self.assertTrue(pruefen(self.lauf, agent))

    def test_dateien_allein_geben_nichts_frei(self):
        for agent in SCHRITTE:
            self.ergebnis(agent)
        self.assertEqual(status(self.lauf)['agent'], 'auftragsklaerung')
        with self.assertRaisesRegex(ValueError, 'Nächster Schritt'):
            pruefen(self.lauf, 'uebergabe')

    def test_nur_ausdrueckliche_lehrkraftentscheidung(self):
        self.bis()
        stand = status(self.lauf)
        self.assertEqual(stand['status'], 'wartet_auf_lehrkraft')
        with self.assertRaises(ValueError):
            lehrkraft(self.lauf, 'freigegeben', stand['version'], '')
        with self.assertRaises(ValueError):
            lehrkraft(self.lauf, 'freigegeben', 'veraltet', 'Einsetzbar.')
        lehrkraft(self.lauf, 'freigegeben', stand['version'], 'Einsetzbar.')
        self.assertEqual(status(self.lauf)['status'], 'freigegeben')

    def test_fehlerhaftes_review_bleibt_gesperrt(self):
        self.bis('fachreview')
        schreiben(self.lauf / '07_fachreview.json', {'urteil': 'freigegeben', 'befunde': [{'agent': 'fachrecherche', 'auftrag': 'Fehler'}]})
        with self.assertRaisesRegex(ValueError, 'Offene Befunde'):
            pruefen(self.lauf, 'fachreview')
        self.assertEqual(status(self.lauf)['agent'], 'fachreview')

    def test_review_gibt_an_ersteller_zurueck(self):
        self.bis('fachreview')
        schreiben(self.lauf / '07_fachreview.json', {'urteil': 'aenderungen', 'befunde': [
            {'agent': 'loesungsentwicklung', 'auftrag': 'Lösung A3 korrigieren.'},
            {'agent': 'fachrecherche', 'auftrag': 'Beleg B2 korrigieren.'}]})
        self.assertFalse(pruefen(self.lauf, 'fachreview'))
        self.assertEqual(status(self.lauf)['agent'], 'fachrecherche')
        # Ein altes bestandenes Review darf nach Überarbeitung nicht wiederverwendet werden.
        with self.assertRaises(ValueError):
            pruefen(self.lauf, 'fachreview')

    def test_review_darf_nicht_an_beliebige_rolle_delegieren(self):
        self.bis('fachreview')
        schreiben(self.lauf / '07_fachreview.json', {'urteil': 'aenderungen', 'befunde': [
            {'agent': 'uebergabe', 'auftrag': 'Einfach fertigstellen.'}]})
        with self.assertRaises(ValueError):
            pruefen(self.lauf, 'fachreview')
        self.assertEqual(status(self.lauf)['agent'], 'fachreview')

    def test_inhaltsaenderung_entwertet_reviews_und_freigabe(self):
        self.bis()
        stand = status(self.lauf)
        lehrkraft(self.lauf, 'freigegeben', stand['version'], 'Freigegeben.')
        with open(self.lauf / '03_fachrecherche.md', 'a') as f:
            f.write('Nachträgliche Änderung')
        neu = status(self.lauf)
        self.assertEqual(neu['agent'], 'fachrecherche')
        self.assertEqual(neu['status'], 'in_arbeit')
        self.assertNotEqual(neu['version'], stand['version'])

    def test_jeder_export_ist_an_freigabe_gebunden(self):
        for export, agent in [('folien.pdf', 'canva-praesentation'), ('blatt.pdf', 'canva-arbeitsblatt'), ('loesungen.pdf', 'canva-arbeitsblatt')]:
            with self.subTest(export=export):
                # Jeder Fall startet einen vollständigen eigenen Freigabestand.
                (self.lauf / 'status.json').unlink(missing_ok=True)
                self.bis()
                stand = status(self.lauf)
                lehrkraft(self.lauf, 'freigegeben', stand['version'], 'Freigegeben.')
                (self.lauf / export).write_bytes(b'%PDF-1.7\nGeaendert\n')
                self.assertEqual(status(self.lauf)['agent'], agent)

    def test_lehrkraftwuensche_erfordern_neue_reviews(self):
        self.bis()
        stand = status(self.lauf)
        lehrkraft(self.lauf, 'aenderungen', stand['version'], 'Bitte mehr Schreibplatz.', [
            {'agent': 'canva-arbeitsblatt', 'auftrag': 'Mehr Schreibplatz für A2.'}])
        self.assertEqual(status(self.lauf)['agent'], 'canva-arbeitsblatt')
        for agent in list(SCHRITTE)[list(SCHRITTE).index('canva-arbeitsblatt'):]:
            self.ergebnis(agent)
            pruefen(self.lauf, agent)
        self.assertEqual(status(self.lauf)['status'], 'wartet_auf_lehrkraft')

    def test_zurueckstellen_ist_keine_freigabe(self):
        self.bis()
        stand = status(self.lauf)
        lehrkraft(self.lauf, 'zurueckgestellt', stand['version'], 'Später verwenden.')
        self.assertEqual(status(self.lauf)['status'], 'zurueckgestellt')
        with self.assertRaisesRegex(ValueError, 'freigegebenes Paket'):
            abgeben(self.lauf)

    def test_spaetere_aenderungswuensche_nehmen_freigabe_zurueck(self):
        self.bis()
        version = status(self.lauf)['version']
        lehrkraft(self.lauf, 'freigegeben', version, 'Freigegeben.')
        lehrkraft(self.lauf, 'aenderungen', version, 'Bitte doch größere Schrift.', [
            {'agent': 'canva-praesentation', 'auftrag': 'Schrift vergrößern.'}])
        self.assertEqual(status(self.lauf)['agent'], 'canva-praesentation')

    def test_zurueckgestelltes_paket_kann_spaeter_freigegeben_werden(self):
        self.bis()
        version = status(self.lauf)['version']
        lehrkraft(self.lauf, 'zurueckgestellt', version, 'Später verwenden.')
        lehrkraft(self.lauf, 'freigegeben', version, 'Jetzt einsetzbar.')
        self.assertEqual(status(self.lauf)['status'], 'freigegeben')

    def test_ohne_canva_keine_freigabe(self):
        self.bis('canva-praesentation')
        with self.assertRaises(OSError):
            pruefen(self.lauf, 'canva-praesentation')
        self.assertEqual(status(self.lauf)['agent'], 'canva-praesentation')

    def test_export_darf_laufordner_nicht_verlassen(self):
        self.bis('canva-praesentation')
        self.ergebnis('canva-praesentation')
        pfad = self.lauf / '09_praesentation.json'
        daten = json.loads(pfad.read_text())
        daten['exporte'] = ['../../fremd.pdf']
        schreiben(pfad, daten)
        with self.assertRaisesRegex(ValueError, 'Laufordner'):
            pruefen(self.lauf, 'canva-praesentation')

    def test_loesungen_muessen_getrennt_sein(self):
        self.bis('canva-arbeitsblatt')
        self.ergebnis('canva-arbeitsblatt')
        pfad = self.lauf / '10_arbeitsblatt.json'
        original = json.loads(pfad.read_text())
        for art in ['design', 'export', 'fehlend']:
            with self.subTest(art=art):
                daten = json.loads(json.dumps(original))
                if art == 'design':
                    daten['loesungen'] = daten.copy()
                elif art == 'export':
                    daten['loesungen']['exporte'] = daten['exporte']
                else:
                    del daten['loesungen']
                schreiben(pfad, daten)
                with self.assertRaises(ValueError):
                    pruefen(self.lauf, 'canva-arbeitsblatt')

    def test_fremde_canva_domain_wird_abgelehnt(self):
        self.bis('canva-praesentation')
        self.ergebnis('canva-praesentation')
        pfad = self.lauf / '09_praesentation.json'
        daten = json.loads(pfad.read_text())
        daten['bearbeitungslink'] = 'https://canva.com.example.org/design/Folien/edit'
        schreiben(pfad, daten)
        with self.assertRaises(ValueError):
            pruefen(self.lauf, 'canva-praesentation')

    def test_bericht_zeigt_status_und_escaped_html(self):
        self.bis()
        (self.lauf / '00_eingabe.md').write_text('<script>alert(1)</script>', encoding='utf-8')
        bauen(self.lauf)
        html = (self.lauf / 'ergebnis.html').read_text()
        self.assertNotIn('<script>', html)
        self.assertIn('noch nicht freigegeben', html)

    def test_neue_laeufe_sind_eindeutig_und_unabhaengig(self):
        script = Path(__file__).resolve().parents[1] / 'plugins' / 'lessi-code' / 'scripts' / 'neuer_lauf.py'
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root), LESSI_WORKSPACE=str(self.root))
        result = [subprocess.check_output([sys.executable, str(script)], input=b'Thema: Familie', env=env, text=False).decode().strip() for _ in range(2)]
        self.assertNotEqual(*result)
        for pfad in result:
            self.assertEqual(status(self.root / pfad)['agent'], 'auftragsklaerung')

    def test_unfreigegebenes_paket_startet_keinen_upload(self):
        with patch('abgeben.git') as git:
            with self.assertRaises(ValueError):
                abgeben(self.lauf)
            git.assert_not_called()

    def test_cli_laufpfad_und_fehlerausgabe(self):
        script = Path(__file__).resolve().parents[1] / 'plugins' / 'lessi-code' / 'scripts' / 'workflow.py'
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root), LESSI_WORKSPACE=str(self.root))
        result = subprocess.run([sys.executable, str(script), 'status', '--lauf', 'ergebnisse/testlauf'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['agent'], 'auftragsklaerung')
        result = subprocess.run([sys.executable, str(script), 'status', '--lauf', '../anderer-lauf'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)

    def test_bericht_verlinkt_designs_und_exporte(self):
        self.bis()
        bauen(self.lauf)
        html = (self.lauf / 'ergebnis.html').read_text()
        self.assertIn('href="https://www.canva.com/design/Blatt/edit"', html)
        self.assertIn('href="loesungen.pdf"', html)
        self.assertIn('wartet auf das Review', html)

    def test_verspaetete_entscheidung_gilt_nicht_fuer_neuen_stand(self):
        self.bis()
        version = status(self.lauf)['version']
        (self.lauf / '04_unterrichtsplan.md').write_text('Geändert', encoding='utf-8')
        with self.assertRaises(ValueError):
            lehrkraft(self.lauf, 'freigegeben', version, 'Freigegeben.')


if __name__ == '__main__':
    unittest.main()
