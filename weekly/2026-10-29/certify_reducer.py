"""Exact table and index checks supporting the stated reducer extension.
This supplies finite/algebraic premises, not an exhaustive execution proof.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,re,json,hashlib,time
Q=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).resolve().parent))
from certify_polynomials import atan
source=Path(sys.argv[1]);start=time.process_time()
s=source.read_text(encoding='utf-8')
txt=re.sub(r'/\*.*?\*/|//[^\n]*',' ',s,flags=re.S)
table=re.search(r'_T\[20\]\s*=\s*\{(.*?)\};',txt,re.S).group(1)
vals=[int(x.strip(),0) for x in table.split(',') if x.strip()];assert len(vals)==20
l5,h5=atan(5,400);l239,h239=atan(239,400);pl,ph=16*l5-4*h239,16*h5-4*l239
D=1<<1536;pl=F((pl*D).__floor__(),D);ph=F(-((-ph*D).__floor__()),D)
lo,hi=1/(2*ph),1/(2*pl)
assert vals[0]==0
for j in range(1,20):
 a,b=(lo*(1<<(64*j))).__floor__(),(hi*(1<<(64*j))).__floor__()
 assert a==b and a%(1<<64)==vals[j],j
indices=[]
for e in range(996,2047):
 unbiased=e-1075;i=-1+(e-947)//64;f=(e-1011)&63
 assert i==-((-unbiased-1)//64)  # ceil((unbiased+1)/64)
 assert f==unbiased%64 and -1<=i<=16 and 0<=i+1<=17 and 1<=i+2<=18 and i+3<=19
 if e<=1006:indices.append({'biased_exponent':e,'mantissa_exponent':unbiased,'index':i,'shift':f})
# Three 64-bit words truncate the fractional part of 2^e/(2*pi) downwards.
# m<2^53 makes discarded tail <2^-139; dropping low product adds <2^-128.
turn=F(1,1<<128)+F(1,1<<139)
assert turn**1000 < F(1,1<<127999)
out={'table_words_exact_floor_verified':20,'all_supported_exponent_index_checks':1051,
     'new_small_exponents':indices,'fractional_turn_error_strict_upper':str(turn),
     'bound_below_2_power_minus_127_999':True,'pi_lower':str(pl),'pi_upper':str(ph),
     'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'argument':'Exact floor table; three-word truncation, m<2^53, and dropped low product. Modulo 2^128 and nearest-grid recentering preserve turn error. Narrative source-operation binding is separately reviewed.',
     'cpu_seconds':time.process_time()-start}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n');print('20 table words, 1051 exponents and exact tail bound verified')
