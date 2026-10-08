"""Bind every accurate-reducer exponent/table window to a directed pi enclosure."""
from pathlib import Path
from fractions import Fraction as F
import json,re
R=Path(__file__).resolve().parent
d=json.loads((R/'DISTANCE-CERTIFICATE.json').read_text());pl=F(d['pi_lower']);ph=F(d['pi_upper'])
s=(R/'source/src/binary64/sin/sin.c').read_text();b=re.search(r'_T\[20\] = \{(.*?)\};',s,re.S).group(1);b=re.sub(r'//[^\n]*','',b)
T=[int(x,0) for x in re.findall(r'0x[0-9a-f]+|\b0\b',b)];assert len(T)==20
M=(1<<64)-1;rows=[]
for e in range(1007,2047):
 i=-1+(e-947)//64;f=(e-1011)&63;V0=T[i] if i>=0 else 0;V1=T[i+1];V2=T[i+2]
 if f:V0=((V0<<f)|(V1>>(64-f)))&M;V1=((V1<<f)|(V2>>(64-f)))&M;V2=((V2<<f)|(T[i+3]>>(64-f)))&M
 scale=F(2)**(e-1075+192)/2
 lower=scale/ph;upper=scale/pl;v=int(lower);assert v==int(upper)
 assert ((V0<<128)|(V1<<64)|V2)==v%(1<<192),e
 rows.append(dict(biased_exponent=e,i=i,f=f,window_hex=hex(v%(1<<192))))
err=F(2)**-128+F(2)**-139
assert 2*ph*err<7*F(2)**-128
out=dict(passed=True,exponents=len(rows),domain='2^-16 <= abs(x) <= maximum finite binary64',fractional_reduction_error_strict_upper=str(err),sine_argument_error_strict_upper_units_2m128=7,method='For each exponent exact interval arithmetic identifies floor(2^192*2^(e-1075)/(2*pi)) modulo2^192 and compares to the three shifted C words. Multiplication by m<2^53 leaves an omitted tail<2^-139; dropping low64(m*V2) loses<2^-128. Centering preserves value modulo1.',rows=rows)
(R/'REDUCER-CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS all1040 exponent windows; analytic error bound <7*2^-128 after multiplying by2pi')
