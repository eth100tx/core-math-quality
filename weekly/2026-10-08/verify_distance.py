"""Replay the certificate with a second pi identity and separate CF recurrence."""
from pathlib import Path
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parent;d=json.loads((R/'DISTANCE-CERTIFICATE.json').read_text());pl=F(d['pi_lower']);ph=F(d['pi_upper'])
# atan(1/2)+atan(1/3)=pi/4, since its tangent is1 and both summands
# are positive with sum below pi/2. Independent of the Machin formula.
def bounds(q):
 n=900;s=F(0)
 for k in range(n):s+=F((-1)**k,(2*k+1)*q**(2*k+1))
 return s,s+F(1,(2*n+1)*q**(2*n+1))
a,b=bounds(2);c,e=bounds(3);assert pl<4*(a+c)<4*(b+e)<ph
Q=2**53-1;target=F(d['target_distance']);assert len(d['rows'])==1024
for e,row in zip(range(-52,972),d['rows']):
 assert row['e']==e
 L=F(2)**(e+1)/ph;H=F(2)**(e+1)/pl;mid=(L+H)/2
 z=mid;pm2,pm1,qm2,qm1=0,1,1,0;best=None
 while True:
  k=z.numerator//z.denominator;p=k*pm1+pm2;q=k*qm1+qm2
  if q>Q:break
  v=abs(q*mid-p)
  if best is None or v<best[0]:best=(v,p,q)
  pm2,pm1,qm2,qm1=pm1,p,qm1,q;z=1/(z-k)
 assert q==row['next_q'] and str(best[1])==row['p'] and best[2]==row['q']
 lower=pl/2*(best[0]-Q*(H-L)/2)
 assert lower==F(row['distance_lower']) and lower>target
(R/'DISTANCE-REPLAY.json').write_text(json.dumps(dict(passed=True,rows=1024,pi_identity='pi=4*(atan(1/2)+atan(1/3));900 alternating terms',method='Separate exact Fraction continued-fraction recurrence and independent tighter pi enclosure verify every recorded row; mathematical best-approximation theorem remains explicit.'),indent=2)+'\n');print('PASS independent pi identity and1024 certificate rows')
