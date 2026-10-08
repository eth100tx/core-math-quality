"""Prove the non-strict cosine approximation bound using signed Taylor bounds."""
from pathlib import Path
from fractions import Fraction as F
from math import comb,factorial
import json,re,time,resource
R=Path(__file__).resolve().parent;OLD=R;start=time.monotonic();c0=resource.getrusage(resource.RUSAGE_SELF)
src=(R/'source/src/binary64/sin/sin.c').read_text()
body=re.search(r'\bPC\[\] = \{(.*?)\};',src,re.S).group(1)
vals=[(int(hi,0)<<64)|int(lo,0) for lo,hi in re.findall(r'U128\((0x[0-9a-f]+|0),(0x[0-9a-f]+|0)\)',body)]
assert len(vals)==5
coefs=[F((-1)**k*v,1<<(64 if k==4 else 128)) for k,v in enumerate(vals)]
cert=json.loads((OLD/'evidence/exact-polynomials/accurate-cos.json').read_text());B=F(cert['input_abs_upper']);assert B<F(1,1000)
pi_upper=F(json.loads((OLD/'evidence/exact-polynomials/EXACT-RESULTS.json').read_text())['pi_upper']);assert B>=pi_upper/8192
# t=x^2. T8(t)=sum_{k=0}^8 (-1)^k t^k/(2k)!. For 0<=x<=B<1,
# T8(t)-t^9/18! <= cos(x) <= T8(t), by alternating decreasing terms.
err=[(coefs[k] if k<5 else F(0))-F((-1)**k,factorial(2*k)) for k in range(9)]
assert err[0]==-F(2)**-128
# Lower error >= -2^-128 follows from (P-T8+2^-128)/t >= 0;
# at t=0 equality is handled exactly. Upper error <= 2^-128 follows from
# 2^-128-(P-T8)-t^9/18! >= 0.
lower=err[1:];upper=[-v for v in err]+[-F(1,factorial(18))];upper[0]+=F(2)**-128
def bern_range(c,a,b):
 n=len(c)-1
 power=[(b-a)**j*sum((c[k]*comb(k,j)*a**(k-j) for k in range(j,n+1)),F(0)) for j in range(n+1)]
 betas=[sum((power[j]*F(comb(i,j),comb(n,j)) for j in range(i+1)),F(0)) for i in range(n+1)]
 return min(betas),max(betas)
stack=[(F(0),B*B,0)];cells=[]
while stack:
 a,b,depth=stack.pop();lo,_=bern_range(lower,a,b);hi,_=bern_range(upper,a,b)
 if lo>=0 and hi>=0:cells.append(dict(a=str(a),b=str(b),lower_nonnegative=str(lo),upper_nonnegative=str(hi)))
 else:
  assert depth<25 and len(cells)+len(stack)<10000,(float(a),float(b),float(lo),float(hi))
  m=(a+b)/2;stack.extend([(a,m,depth+1),(m,b,depth+1)])
cells.sort(key=lambda c:F(c['a']));assert F(cells[0]['a'])==0 and F(cells[-1]['b'])==B*B
assert all(F(a['b'])==F(b['a']) for a,b in zip(cells,cells[1:]))
c1=resource.getrusage(resource.RUSAGE_SELF)
out=dict(proved=True,claim='abs(PC(x)-cos(x)) <= 2^-128 on abs(x)<=B; equality at x=0',B=str(B),coefficients=[str(v) for v in coefs],cells=cells,method='Exact rational signed Taylor remainder and Bernstein convex-hull positivity; evenness covers negative x. Domain B is the previously certified outward pi/8192 enclosure.',cpu_seconds=c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,wall_seconds=time.monotonic()-start)
(R/'COS-CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n');print('Cosine bound certified, cells',len(cells),flush=True)
