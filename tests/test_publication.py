import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate', ROOT/'validate.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class PublicationTests(unittest.TestCase):
    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            v.keys({'compiler': 'gcc', 'private_email': 'x'}, v.ENV, 'environment')

    def test_missing_receipt_fields_rejected(self):
        with self.assertRaises(ValueError):
            v.receipt({'schema_version': 1})

    def test_unknown_schema_rejected(self):
        with self.assertRaises(ValueError):
            v.receipt({**{key: None for key in v.TOP}, 'schema_version': 2})
