import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import json
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate', ROOT/'validate.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class PublicationTests(unittest.TestCase):
    def test_raw_discovery_preserves_linux_case_and_recursion(self):
        folder = Mock()
        candidates = [Path(name) for name in [
            'nested/rndu-coverage.json', 'MISSING-COVERAGE.json',
            'foo-Coverage.json', 'rndn-coverage.json']]
        folder.rglob.return_value = iter(candidates)
        self.assertEqual(v.raw_coverage_paths(folder),
                         sorted([candidates[0], candidates[3]]))
        folder.glob.assert_not_called()
        folder.glob.return_value = iter(candidates[1:])
        self.assertEqual(v.raw_coverage_paths(folder, recursive=False), [candidates[3]])
        folder.glob.assert_called_once_with('*-coverage.json')

    def test_summary_does_not_count_as_fifth_mode(self):
        from quality import coverage_maps, coverage_summary
        raw = {'file': 'src/binary64/sin/sin.c', 'functions': [], 'lines': []}
        summary = coverage_summary(*coverage_maps(raw))
        cell = {'modes': [{'mode': m, 'coverage': summary}
                         for m in ['rndn', 'rndz', 'rndu', 'rndd']],
                'coverage_union': summary}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for mode in cell['modes']:
                (folder / (mode['mode'] + '-coverage.json')).write_text(json.dumps(raw))
            (folder / 'MISSING-COVERAGE.json').write_text('{}')
            v.verify_coverage(cell, folder)
            (folder / 'extra-coverage.json').write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, 'four raw coverage files'):
                v.verify_coverage(cell, folder)

    def test_raw_unknown_fields_still_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'weekly').mkdir()
            (root / 'weekly/rndn-coverage.json').write_text(json.dumps({
                'file': 'src/binary64/sin/sin.c', 'functions': [], 'lines': [],
                'pin': 'unexpected', 'profile': 'unexpected'}))
            with patch.object(v, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, "gcov file: unknown fields"):
                    v.main()

    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            v.keys({'compiler': 'gcc', 'private_email': 'x'}, v.ENV, 'environment')

    def test_missing_receipt_fields_rejected(self):
        with self.assertRaises(ValueError):
            v.receipt({'schema_version': 1})

    def test_unknown_schema_rejected(self):
        with self.assertRaises(ValueError):
            v.receipt({**{key: None for key in v.TOP}, 'schema_version': 2})
