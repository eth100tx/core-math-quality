import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from validate_hypot import validate

FOLDER=Path(__file__).resolve().parents[1]/'bivariate/results/2026-10-26'


class HypotReceiptTests(unittest.TestCase):
    def test_published_receipt(self):
        self.assertEqual(validate(FOLDER)['fixture_count'],18)

    def test_resealed_false_evidence_still_rejected(self):
        mutations=[lambda d:d.update(extra=1),lambda d:d.update(status='INCOMPLETE'),
          lambda d:d.update(fixture_count=17),lambda d:d['profiles'][0]['observations'].pop(),
          lambda d:d['profiles'][0]['observations'][0]['observation'].update(value=f"{int(d['profiles'][0]['observations'][0]['observation']['value'],16)^1:016x}"),
          lambda d:d['profiles'][0]['observations'][0]['observation']['flags'].update(invalid=1),
          lambda d:d['profiles'][0]['observations'][0]['observation'].update(errno=1),
          lambda d:d['profiles'][0]['observations'][0]['observation'].update(mode_index=True),
          lambda d:d['profiles'][0]['observations'][0]['oracle'].update(bound_hi=f"{int(d['profiles'][0]['observations'][0]['oracle']['bound_hi'],16)^1:016x}"),
          lambda d:d['profiles'][0]['controls'][0].update(observed='PROCESS'),
          lambda d:d['profiles'][0].update(controls=[]),lambda d:d['cost'].update(wall_seconds=99999),
          lambda d:d.update(scope='All hypot inputs proved'),lambda d:d.update(started_utc='2026-10-26T00:00:00-05:00'),
          lambda d:d['profiles'][0]['observations'][0]['observation'].update(raw_flags=0x21),
          lambda d:d['profiles'][0].update(oracle_libraries={'libmpfr.so.6':'0'*64,'libmpfr.so.7':'0'*64})]
        for i,mutate in enumerate(mutations):
            with self.subTest(case=i),tempfile.TemporaryDirectory() as tmp:
                folder=Path(tmp)/'evidence';shutil.copytree(FOLDER,folder)
                path=folder/'qualification.json';d=json.loads(path.read_text(encoding='utf-8'));mutate(d)
                path.write_text(json.dumps(d),encoding='utf-8')
                sums=folder/'SHA256SUMS.json';m=json.loads(sums.read_text());m['qualification.json']=hashlib.sha256(path.read_bytes()).hexdigest();sums.write_text(json.dumps(m))
                with self.assertRaises(ValueError):validate(folder)

    def test_tool_change_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'evidence';shutil.copytree(FOLDER,folder)
            (folder/'tools/hypot_verify.py').write_text('changed',encoding='utf-8')
            with self.assertRaises(ValueError):validate(folder)

    def test_manifest_hash_change_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'evidence';shutil.copytree(FOLDER,folder)
            path=folder/'SHA256SUMS.json';d=json.loads(path.read_text());d['qualification.json']='0'*64
            path.write_text(json.dumps(d),encoding='utf-8')
            with self.assertRaises(ValueError):validate(folder)
