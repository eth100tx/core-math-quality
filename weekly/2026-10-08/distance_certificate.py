"""Exact finite continued-fraction certificate; no sampled inputs or floating decisions."""
from fractions import Fraction as F
from pathlib import Path
import json,time,math
R=Path(__file__).resolve().parent
def atan(q,n=384):
 s=sum((F((-1)**k,(2*k+1)*q**(2*k+1)) for k in range(n)),F(0))
 t=F(1,(2*n+1)*q**(2*n+1));return s,s+t
def nearest(a,Q):
 n,d=a.numerator,a.denominator;p0,p1,q0,q1=0,1,1,0;best=None
 while d:
  v,n,d=n//d,d,n%d;p=v*p1+p0;q=v*q1+q0
  if q>Q:return best,q
  err=abs(q*a-p)
  if q and (best is None or err<best[0]):best=(err,p,q)
  p0,p1,q0,q1=p1,p,q1,q
 return best,None
for a in [F(37,101),F(13,97),F(88,101),F(161,103)]:
 for Q in range(1,80):
  best,_=nearest(a,Q)
  brute=min(min((q*a)%1,1-(q*a)%1) for q in range(1,Q+1))
  assert best[0]==brute,(a,Q,best,brute)
l5,h5=atan(5);l239,h239=atan(239);pl=16*l5-4*h239;ph=16*h5-4*l239
D=1<<1536;pl=F((pl*D).__floor__(),D);ph=F(-(-ph*D).__floor__(),D)
Q=(1<<53)-1;target=F(17,16)*F(2)**-61;rows=[];minimum=None
for e in range(-52,972):
 lo=F(2)**(e+1)/ph;hi=F(2)**(e+1)/pl;a=(lo+hi)/2
 best,nextq=nearest(a,Q);err,p,q=best
 lower=(pl/2)*(err-Q*(hi-lo)/2)
 assert nextq and nextq>Q and lower>target,(e,float(lower))
 row={'e':e,'p':str(p),'q':q,'next_q':nextq,'distance_lower':str(lower)}
 rows.append(row)
 if minimum is None or lower<minimum[0]:minimum=(lower,e,q)
 if (e+52)%128==0:print('distance exponent',e,'of971',flush=True)
low,e,q=minimum
sinlo=target-target**3/6
assert sinlo-F(2)**-123>F(2)**-61
assert target**2/2-target**4/24>F(2)**-123
out={'method':'Machin alternating-series pi enclosure; exact rational midpoint continued fractions, all denominators1..2^53-1, interval correction Q*radius; 1024 exponent values',
 'domain':'All finite binary64 x with abs(x)>=2^-16. For abs(x)<1, distance to any multiple of pi/2 is at least2^-16; otherwise use m*2^e with -52<=e<=971.',
 'pi_lower':str(pl),'pi_upper':str(ph),'target_distance':str(target),'all_1024_pass':True,
 'global_lower_display_log2':math.log2(float(low)),'min_e':e,'min_m':q,
 'conditional_consequence':'If accurate fixed-point absolute error <2^-123, no overflow and high64>=8; h==0 unreachable, sh<=60. Approximation bound is a separate obligation.',
 'rows':rows}
(R/'DISTANCE-CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS exact distance bound',float(target),'minimum log2',out['global_lower_display_log2'],flush=True)
