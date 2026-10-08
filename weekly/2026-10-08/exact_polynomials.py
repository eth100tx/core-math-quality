"""Exact rational Taylor/Bernstein certificates; decimal logs are display only."""
from pathlib import Path
from fractions import Fraction as F
from math import comb,factorial,isqrt,ceil,log2
from decimal import Decimal,localcontext
import json,time,resource,re,hashlib
R=Path(__file__).resolve().parent;E=R/'evidence/exact-polynomials';E.mkdir(exist_ok=True)
t0=time.monotonic();c0=resource.getrusage(resource.RUSAGE_SELF)
def atan(q,N=320):
 s=sum((F((-1)**k,(2*k+1)*q**(2*k+1)) for k in range(N)),F(0));a=F(1,(2*N+1)*q**(2*N+1));return (s,s+a) if N%2==0 else (s-a,s)
l5,h5=atan(5);l239,h239=atan(239);pl=16*l5-4*h239;ph=16*h5-4*l239
# Validate the reciprocal table independently, before reducing pi precision for the polynomials.
FD=1<<1280;plfull=F((pl*FD).__floor__(),FD);phfull=F(ceil(ph*FD),FD)
src=(R/'source/src/binary64/sin/sin.c').read_text();tab=re.search(r'_T\[20\] = \{(.*?)\};',src,re.S).group(1);tab=re.sub(r'//[^\n]*','',tab)
words=[int(x,0) for x in re.findall(r'0x[0-9a-f]+|\b0\b',tab)];assert len(words)==20
truewords=[]
for i in range(20):
 lo=F(1,2)/phfull*(1<<(64*i));hi=F(1,2)/plfull*(1<<(64*i));assert lo.__floor__()==hi.__floor__()
 truewords.append(lo.__floor__()%2**64)
assert [i for i in range(20) if words[i]!=truewords[i]]==[]
assert truewords[19]==0x1580cc11bf1edaea
D=1<<512;pl=F((plfull*D).__floor__(),D);ph=F(ceil(phfull*D),D)
pi2=F(0xc90fdaa22168c234c4c6628b80dc1cd1,1<<128)
assert pl/4>=pi2 and ph/4-pi2<=F(671953,1<<150)
(E/'CONSTANTS.json').write_text(json.dumps({'reciprocal_words_0_through_19_exact':True,'word19_actual':words[19],'word19_expected':hex(truewords[19]),'pi_over_4_error_within_gappa_hypothesis':True,'source_sha256':hashlib.sha256(src.encode()).hexdigest(),'pi_full_lower':str(plfull),'pi_full_upper':str(phfull)},indent=2)+'\n')
def hx(s):
 if 'p' in s and s.startswith('0x'):
  a,e=s.split('p');a=a[2:];e=int(e);digits=a.replace('.','');k=len(a.split('.')[1]) if '.' in a else 0
  return F(int(digits,16),16**k)*F(2)**e
 return F(s)
def target(exp):
 with localcontext() as c:c.prec=100;v=Decimal(2)**(-Decimal(exp));n=int((v*Decimal(2)**256).to_integral_value(rounding='ROUND_CEILING'))
 return F(n,1<<256)
def bern(c,a,b):
 n=len(c)-1;d=[(b-a)**j*sum((c[k]*comb(k,j)*a**(k-j) for k in range(j,n+1)),F(0)) for j in range(n+1)]
 return max(abs(sum((d[j]*F(comb(i,j),comb(n,j)) for j in range(i+1)),F(0))) for i in range(n+1))
def sqrtup(v):return F(isqrt((v.numerator<<512)//v.denominator)+1,1<<256)
def cert(name,coefs,B,kind,alpha=(F(1),F(1)),relative=False,exp='120'):
 if name in ['accurate-sin','accurate-cos']:
  table='PS' if name=='accurate-sin' else 'PC';body=re.search(r'\b'+table+r'\[\] = \{(.*?)\};',src,re.S).group(1)
  vals=[(int(hi,0)<<64)|int(lo,0) for lo,hi in re.findall(r'U128\((0x[0-9a-f]+|0),(0x[0-9a-f]+|0)\)',body)]
  for k,val in enumerate(vals):
   power=2*k+(table=='PS');den=64 if k==len(vals)-1 else 128
   assert coefs[power]==F((-1)**k*val,1<<den),(name,power)
 alo,ahi=alpha;am=(alo+ahi)/2;odd=kind=='sin';n=7 if odd else 8;c=[];uncert=F(0)
 for k in range(n+1):
  j=2*k+int(odd);c.append(coefs.get(j,F(0))-F((-1)**k,factorial(j))*am**j)
  uncert+=(ahi**j-alo**j)*B**j/factorial(j)
 rem=(ahi*B)**(17 if odd else 18)/factorial(17 if odd else 18)
 if relative:
  assert odd and alpha==(F(1),F(1));rem=B**16/F(factorial(17));uncert=0
  divisor=1-B*B/6
 else:divisor=F(1)
 goal=target(exp);stack=[(F(0),B*B,0)];cells=[];worst=F(0)
 while stack:
  a,b,depth=stack.pop();v=bern(c,a,b)
  if odd and not relative:v*=sqrtup(b)
  v=(v+rem+uncert)/divisor
  if v<=goal:
   upper=F(ceil(v*(1<<256)),1<<256);cells.append({'t_lo':str(a),'t_hi':str(b),'upper':str(upper)});worst=max(worst,upper)
  else:
   if depth>=30:raise AssertionError((name,'target not certified',exp,float(a),float(b),log2(float(v))))
   mid=(a+b)/2;stack.extend([(a,mid,depth+1),(mid,b,depth+1)])
  if len(cells)+len(stack)>100000:raise RuntimeError('cell cap')
 out={'name':name,'input_abs_upper':str(B),'kind':kind,'relative':relative,'target_exact':str(goal),'certified_upper_exact':str(worst),'log2_upper_display':log2(float(worst)),'cells':cells,'method':'Exact Fraction arithmetic, Machin pi enclosure from alternating arctangent series, Taylor remainder, Bernstein convex-hull enclosure on t=x^2; all comparisons exact. Decimal target exponent is only a convenient rational-target selector.'}
 (E/(name+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(name,'cells',len(cells),'log2 upper',out['log2_upper_display'],flush=True)
 return {k:v for k,v in out.items() if k!='cells'}
results=[]
smallbody=src[src.index('sin_small_accurate (double x)'):]
smallcoef=re.search(r'static const double c\[\] = \{(.*?)\};',smallbody,re.S).group(1)
smallvalues=[F(float.fromhex(v.strip())) for v in smallcoef.split(',')]
assert smallvalues==[-hx('0x1.5555555555555p-3'),-hx('0x1.55554b00de7e8p-57'),hx('0x1.111111110848p-7')]
results.append(cert('moderate-sin',{1:F(1),3:-hx('0x1.55555553068fp-3')},hx('0x1.94dp-14'),'sin',exp='76.48'))
results.append(cert('moderate-cos',{0:F(1),2:F(-1,2),4:hx('0x1.55555553bfd3p-5')},hx('0x1.94dp-14'),'cos',exp='92.70'))
results.append(cert('large-sin',{1:hx('0x1.921fb54442d18p2'),3:-hx('0x1.4abbcdb6b26d1p5')},F(1,2**16),'sin',(2*pl,2*ph),exp='69.36'))
results.append(cert('large-cos',{0:F(1),2:-hx('0x1.3bd3cc9be45dep4'),4:hx('0x1.03c1eee483083p6')},F(1,2**16),'cos',(2*pl,2*ph),exp='83.68'))
B=F(ceil(ph/F(8192)*(1<<64)),1<<64)
results.append(cert('accurate-sin',{1:hx('0xffffffffffffffffffffffffffffc396p-128'),3:-hx('0x2aaaaaaaaaaaaaaaaaaaa9646e8f872ep-128'),5:hx('0x222222222222220467b898367fb1249p-128'),7:-hx('0xd00d00bfff5eep-64')},B,'sin',exp='128.601'))
results.append(cert('accurate-cos',{0:hx('0xffffffffffffffffffffffffffffffffp-128'),2:-hx('0x7ffffffffffffffffffffffffa998bf0p-128'),4:hx('0xaaaaaaaaaaaaaaaaaa2caecc94962c7p-128'),6:-hx('0x5b05b05b05ac1a642013bc289028b6p-128'),8:hx('0x1a0193d9a550cp-64')},B,'cos',exp='127.99'))
results.append(cert('small-relative',{1:F(1),3:-hx('0x1.5555555555555p-3')-hx('0x1.55554b00de7e8p-57'),5:hx('0x1.111111110848p-7')},F(1,2**16),'sin',relative=True,exp='112.72'))
c1=resource.getrusage(resource.RUSAGE_SELF);(E/'EXACT-RESULTS.json').write_text(json.dumps({'results':results,'pi_lower':str(pl),'pi_upper':str(ph),'cpu_seconds':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'wall_seconds':time.monotonic()-t0},indent=2)+'\n')
