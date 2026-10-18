"""Check saved conditional bounds and the derivative calculation independently."""
from pathlib import Path
import json,re,sys,hashlib
from fractions import Fraction as F
from decimal import Decimal,localcontext
R=Path(__file__).resolve().parent
source=Path(sys.argv[1]).read_text();receipt=json.loads((R/'receipt.json').read_text())
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()==receipt['source_sha256']
table=source.split('static double __attribute__((cold,noinline)) as_exp_accurate')[1].split('static const double ch[][2] =')[1].split(';')[0]
coef=[sum((F(float.fromhex(x.strip())) for x in pair),F()) for pair in re.findall(r'\{([^{}]+),([^{}]+)\}',table)]
assert len(coef)==7
radius=F(9,100000);bound=sum((i+1)*abs(c)*radius**i for i,c in enumerate(coef))
assert bound==F(receipt['arithmetic']['derivative_bound_rational'])<F(10001,10000)
assert radius**1000>F(1,2**13527)
with localcontext() as c:
 c.prec=90;two=Decimal(2)
 total=sum(two**Decimal(x) for x in ['-101.191','-102.490','-116.97','-128'])
 assert total<two**Decimal('-100.69')
faithful=json.loads((R/'faithful-receipt.json').read_text())
assert [x['mode'] for x in faithful['checks']]==['ne','zr','up','dn']
for row in faithful['checks']:
 assert row['returncode']==0
 model=R/('faithful-'+row['mode']+'.g')
 assert hashlib.sha256(model.read_bytes()).hexdigest()==row['model_sha256']
 bounds=re.findall(r'in \[0, (\d+)b(-?\d+)',row['output']);assert len(bounds)==2
 for (n,e),power in zip(bounds,[101191,49883]):
  assert (F(int(n))*F(2)**int(e))**1000<F(1,2**power)
print('PASS exact derivative/hull and saved Gappa bound comparisons; 90-digit error sum. Conditional evidence, not full correctness.')
