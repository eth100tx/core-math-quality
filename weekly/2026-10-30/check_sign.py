"""Finite sign-algebra check, not a floating-point campaign or input witness."""
import json,time,sys
from pathlib import Path
start=time.process_time();fail=[];cases=0
for b in (0,1):
 for q in (0,1):
  for r in (0,1):
   for w1,w2 in ((1,2),(2,1),(1,1)):
    expected=(-1)**b*((-1)**q*w1-(-1)**r*w2)
    magnitude=w1+w2 if q+r==1 else abs(w1-w2)
    d=int(q==r and w1<=w2)
    corrected=(-1)**((b+q+d)%2)*magnitude
    assert corrected==expected
    printed_d=int(q+r==0 and w1<=w2)
    if (-1)**((b+q+printed_d)%2)*magnitude!=expected:
     fail.append(dict(b=b,q=q,sigma_r=r,w1=w1,w2=w2))
    cases+=1
assert len(fail)==2
out={'cases':cases,'corrected_identity_passes':True,'printed_definition_counterexamples':fail,'cpu_seconds':time.process_time()-start,'scope':'Algebraic cases only; w1/w2 are abstract nonnegative magnitudes, not claimed cr_cos input witnesses.'}
Path(sys.argv[1]).write_bytes((json.dumps(out,indent=2)+'\n').encode())
print('24 sign-algebra cases pass; printed definition misses two nonzero sign cases')
