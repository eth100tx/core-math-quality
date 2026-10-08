from pathlib import Path
from fractions import Fraction as F
import json,re
R=Path(__file__).resolve().parent
x0=F(float.fromhex('0x1.7137449123ef6p-26'));u=F(2)**-78;threshold=u*F(2)**-49
def dl(x):return x**3/6-x**5/120+x**7/5040-x**9/362880
def dh(x):return dl(x)+x**11/39916800
rows=[]
for j in range(129):
 x=x0-j*u;lower=u/2-dh(x);upper=u/2-dl(x)
 if max(abs(lower),abs(upper))<threshold:rows.append(dict(offset_below_x0=j,x=float(x).hex(),midpoint_distance_lower=str(lower),midpoint_distance_upper=str(upper)))
 else:assert min(abs(lower),abs(upper))>threshold and lower*upper>0
assert u/2-dh(x0-128*u)>threshold
# The remaining new interval is farther from this midpoint by monotonicity;
# the power-of-two endpoint and representable boundaries are handled separately.
wc=(R/'candidate-source/src/binary64/sin/sin.wc').read_text();existing={float.fromhex(v) for v in re.findall(r'(?mi)^\s*([+-]?0x[0-9a-f]+(?:\.[0-9a-f]*)?p[+-]?\d+)',wc)}
for row in rows:row['already_in_pinned_wc']=float.fromhex(row['x']) in existing
missing=[r['x'] for r in rows if not r['already_in_pinned_wc']]
(R/'threshold-hardcases.wc').write_text('# All isolated near-midpoint cases in the newly routed interval; checker tests both signs.\n'+'\n'.join(r['x'] for r in rows)+'\n')
out=dict(criterion='distance to midpoint <2^-49 ulp(sin(x)), exact directed rational Taylor enclosure',rows=rows,missing=missing,statement='All below-x0 newly routed cases satisfying this criterion are listed. The x0+ offsets were already routed before the threshold change.')
(R/'THRESHOLD-HARDCASES.json').write_text(json.dumps(out,indent=2)+'\n');print('Hard suffix',len(rows),'already in corpus',sum(r['already_in_pinned_wc'] for r in rows),'new rows',len(missing))
