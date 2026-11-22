"""Theorem-backed non-tie midpoint-H100 membership, exact-normal-result scope.

No sqrt, floating arithmetic, or MPFR calls. The pinned table relies on the
separately reviewed finite census; this is not a general hypot value oracle.
"""
import hashlib,json
from pathlib import Path
TABLE=Path(__file__).resolve().parents[1]/'data/hypot-h100-families.json'
TABLE_SHA256='9e344278d2e29614d0c2df67ba0c2ea1d024cb5185853654841b5eea369c2261'
A=1<<52

def normalize(u):
    """Positive finite nonzero binary64 bits ->53bit significand,power exponent."""
    exponent=u>>52;fraction=u&(A-1)
    if exponent:return fraction+A,exponent-1075
    shift=53-fraction.bit_length()
    return fraction<<shift,-1074-shift

class Classifier:
    def __init__(self,path=TABLE):
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=TABLE_SHA256:raise ValueError('table identity')
        table=json.loads(raw)
        if table['version']!=1 or table['threshold']!=100:raise ValueError('table version')
        triples=table['triples']
        if len(triples)!=160 or any(len(t)!=3 or any(type(v)is not int for v in t) or not(A<=t[0]<2*A and A<=t[1]<2*A and t[2] in [24,25,26]) for t in triples):raise ValueError('table domain')
        self.families=frozenset(map(tuple,triples))
        if len(self.families)!=160:raise ValueError('duplicate family')
    def classify(self,x,y):
        if any(type(u)is not int or not 0<=u<1<<64 for u in [x,y]):raise ValueError('binary64 bit encoding')
        x&=(1<<63)-1;y&=(1<<63)-1
        if x>>52==2047 or y>>52==2047:return dict(status='unsupported_nonfinite',hit=None)
        if not x or not y:return dict(status='exact_zero_operand',hit=False)
        x,y=max(x,y),min(x,y)
        a,ex=normalize(x);b,ey=normalize(y);g=ex-ey
        if not 0<=g<=2097:raise AssertionError('normalization gap')
        # Common exact integer units2^-1126 support even normalized minsubnormal.
        X=a<<(ex+1126);Y=b<<(ey+1126);S=X*X+Y*Y
        if S<1<<208:return dict(status='outside_subnormal_norm',hit=None)
        if S>((2*A-1)<<2097)**2:return dict(status='outside_overflow_norm',hit=None)
        key=(a,b,g)
        return dict(status='normal_range',hit=key in self.families,canonical=list(key))
