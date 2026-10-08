"""Isolate every possible difficult case in the newly routed interval, exactly."""
from pathlib import Path
from fractions import Fraction as F
import struct,json
R=Path(__file__).resolve().parent
xmin=F(2)**-26;x0=F(float.fromhex('0x1.7137449123ef6p-26'));ulp=F(2)**-78
cut=x0-4097*ulp;E=x0*F(2)**-102
# On this positive interval, D=x-sin(x) is increasing, and
# x^3/6-x^5/120 <= D <= x^3/6-x^5/120+x^7/5040.
def dlo(x):return x**3/6-x**5/120
def dhi(x):return dlo(x)+x**7/5040
assert cut>xmin
assert dlo(xmin)>E
assert dhi(cut)<ulp/2-E
# At the power-of-two endpoint the spacing below x is half as large.
assert dhi(xmin)<ulp/4-E
assert dlo(xmin)>E
out=dict(proved=True,domain='2^-26 <= abs(x) <= old x0',old_x0=float(x0).hex(),cut=float(cut).hex(),error_allowance=str(E),normal_spacing=str(ulp),midpoint_margin_at_cut=str(ulp/2-dhi(cut)),statement='Assuming |h+l-sin(x)| <2^-102*abs(x), every newly routed input up to cut is farther from every active-mode rounding boundary than its approximation error. All remaining inputs lie in the tested contiguous 4097-positive-input suffix cut+ulp through x0 (both signs). The x=2^-26 binade boundary is treated separately. Oddness and exchanging directed modes cover negative inputs.',method='Exact rational alternating Taylor bounds for x-sin(x), monotonic derivative 1-cos(x)>=0, constant binary64 spacing except at lower endpoint.')
wc=R/'boundary-source/src/binary64/sin/sin.wc'
values={F(float.fromhex(line)) for line in wc.read_text().splitlines() if line and not line.startswith('#')}
suffix={x0-j*ulp for j in range(4097)};assert suffix<=values
assert '#define WORST_SYMMETRIC' in (wc.parent/'function_under_test.h').read_text()
for folder in ['boundary-gcc-v3/sin-gcc-linux-x86_64-v3-errno1','boundary-clang/sin-clang-linux-x86_64-errno1']:
 result=json.loads((R/'runs'/folder/'cell.json').read_text());assert result['status']=='PASS' and result['expected_tests_per_mode']==2*len(values)
 assert [m['mode'] for m in result['modes']]==['rndn','rndz','rndu','rndd'] and all(m['plain']=='PASS' for m in result['modes'])
out['all_suffix_inputs_present']=True;out['both_signs_and_four_modes_verified']=True
(R/'NEW-INTERVAL-CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS: all potential new hard cases confined to explicitly tested 4097-input suffix, both signs')
