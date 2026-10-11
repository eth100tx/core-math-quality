"""Exact coefficient/radius checks plus a separately labelled decimal sum check."""
import sys,re,hashlib,json
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
p=Path(sys.argv[1]);b=p.read_bytes()
assert hashlib.sha256(b).hexdigest()=='39b15256ce4632b163a9f93325c9ada678aacedcdf46cb32ee56f44860a87e64'
s=b.decode().split('static double __attribute__((cold,noinline)) as_exp_accurate')[1].split('static const double ch[][2] =')[1].split(';')[0]
pairs=re.findall(r'\{([^{}]+),([^{}]+)\}',s)
c=[sum((F(float.fromhex(x.strip())) for x in pair),F(0)) for pair in pairs]
assert len(c)==7 and c[0]==1
r=F(9,100000);assert r**1000>F(1,2**13523)
assert (r-F(1,2**23))**1000>F(1,2**13523)
d=sum((i+1)*abs(a)*r**i for i,a in enumerate(c));assert d<F(10001,10000)
assert F(10001,10000)**100<2
with localcontext() as ctx:
 ctx.prec=90;t=Decimal(2)
 total=sum(t**Decimal(x) for x in ['-100.677','-102.4','-116.47','-124.5'])
 assert total<t**Decimal('-100.29')
 print(json.dumps({'derivative_at_zero':'1 exactly','radius':str(r),'derivative_rational_upper_bound':str(d),'exact_rational_checks':'PASS','corrected_sum_log2_90digit_decimal':str(total.ln()/t.ln()),'sum_check':'PASS; high-precision arithmetic, not a formal transcendental certificate'},indent=2))
