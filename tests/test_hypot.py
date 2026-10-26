import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from hypot_verify import verify, loads, read_table
from bivariate.make_fixtures import fixtures


class HypotCertificateTests(unittest.TestCase):
    def test_exact_known_bits(self):
        row=next(r for r in fixtures() if r['x_bits']=='3ff8000000000000' and r['y_bits']=='3ffb800000000000')
        self.assertEqual(row['lower_bits'],'4002400000000000')
        self.assertTrue(verify(row)['exact'])

    def test_both_tie_parities_neighbors_and_binade(self):
        results=[(r,verify(r)) for r in fixtures()]
        ties=[r for r,v in results if v['midpoint_relation']==0]
        self.assertEqual({int(r['lower_bits'],16)%2 for r in ties},{0,1})
        self.assertEqual({v['midpoint_relation'] for r,v in results},{-1,0,1})
        self.assertTrue(any(r['lower_bits']=='4000000000000000' for r,v in results))
        self.assertEqual({v['exact'] for r,v in results},{False,True})

    def test_malformed_certificates_rejected(self):
        base=fixtures()[0]
        mutations=[lambda r:r.update(schema_version=True),lambda r:r.update(schema_version=1.0),
          lambda r:r.update(domain='all'),lambda r:r.update(extra=0),lambda r:r.pop('lower_bits'),
          lambda r:r.update(x_bits='3FF0000000000000'),lambda r:r.update(x_bits='1.0'),
          lambda r:r.update(x_bits='bff0000000000000'),lambda r:r.update(y_bits='7ff0000000000000'),
          lambda r:r.update(y_bits='0000000000000001'),lambda r:r.update(upper_bits=r['lower_bits']),
          lambda r:r.update(upper_bits=f"{int(r['upper_bits'],16)+1:016x}"),
          lambda r:r.update(lower_bits=r['upper_bits'],upper_bits=r['lower_bits']),
          lambda r:r['expected_bits'].update(rndn='4000000000000001'),
          lambda r:r['expected_bits'].pop('rndu'),lambda r:r['expected_bits'].update(extra='4000000000000000'),
          lambda r:r.update(x_bits='3ff0000000000000',y_bits='3ff0000000000000')]
        for i,mutate in enumerate(mutations):
            row=copy.deepcopy(base);mutate(row)
            with self.subTest(case=i),self.assertRaises(ValueError):verify(row)

    def test_duplicate_keys_and_nonfinite_json(self):
        for text in ['{"x":1,"x":2}','{"a":{"x":1,"x":2}}','[NaN]','[Infinity]']:
            with self.subTest(text=text),self.assertRaises(ValueError):loads(text)

    def test_optimized_python_still_rejects(self):
        row=fixtures()[0];row['expected_bits']['rndu']=f"{int(row['expected_bits']['rndu'],16)^1:016x}"
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.json';path.write_text(json.dumps([row]),encoding='utf-8')
            result=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve().parents[1]/'hypot_verify.py'),str(path)],capture_output=True,timeout=10)
            self.assertEqual(result.returncode,1)
            self.assertIn(b'Incorrect expected value: rndu',result.stderr)
            path.write_text(json.dumps(fixtures()),encoding='utf-8')
            good=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve().parents[1]/'hypot_verify.py'),str(path)],capture_output=True,timeout=10)
            self.assertEqual(good.returncode,0)
            self.assertEqual(json.loads(good.stdout)['status'],'PASS')

    def test_exact_and_tie_semantic_mutations(self):
        counts={'exact':0,'tie':0}
        for original in fixtures():
            row=copy.deepcopy(original);answer=verify(row)
            if answer['exact']:
                counts['exact']+=1
                row['expected_bits']['rndu']=row['upper_bits']
            elif answer['midpoint_relation']==0:
                counts['tie']+=1
                row['expected_bits']['rndn']=row['upper_bits'] if int(row['lower_bits'],16)%2==0 else row['lower_bits']
            else:continue
            with self.assertRaisesRegex(ValueError,'Incorrect expected value'):verify(row)
        self.assertEqual(counts,{'exact':2,'tie':4})
        row=fixtures()[0]
        for key in ['lower_bits','upper_bits']:row[key]=f"{int(row[key],16)+1:016x}"
        for mode in row['expected_bits']:row['expected_bits'][mode]=f"{int(row['expected_bits'][mode],16)+1:016x}"
        with self.assertRaisesRegex(ValueError,'Invalid bracket'):verify(row)

    def test_table_bound_and_fixture_reproducibility(self):
        path=Path(__file__).resolve().parents[1]/'bivariate/hypot-fixtures.json'
        self.assertEqual(read_table(path),fixtures())
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'empty.json';p.write_text('[]',encoding='utf-8')
            with self.assertRaises(ValueError):read_table(p)
