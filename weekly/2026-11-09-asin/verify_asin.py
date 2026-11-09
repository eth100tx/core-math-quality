"""Replay two range obligations of the pinned binary64 asin (Python 3.10+).

Exact rational endpoints, rounded outward at each C operation. Model explicit
FMA with one rounding and ordinary expressions with contraction disabled.
Run: python verify_asin.py PATH/TO/asin.c
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import re
import struct

SOURCE_SHA256 = "75b6c144edfb405e916c84931d37e718470948b28c2475b95a2d2459965b2b4d"

def require(condition, detail):
    if not condition:
        raise ValueError(detail)

def outward(q, up):
    """Use float only to select a binary64 endpoint; check its exact side."""
    v = float(q)
    if (up and F(v) < q) or (not up and F(v) > q):
        v = math.nextafter(v, math.inf if up else -math.inf)
    f = F(v)
    require(f >= q if up else f <= q, "endpoint not outward")
    return f

class I:
    def __init__(self, lo, hi=None):
        self.lo = F(lo)
        self.hi = self.lo if hi is None else F(hi)
        require(self.lo <= self.hi, "empty interval")

    @classmethod
    def rounded(cls, lo, hi):
        return cls(outward(lo, False), outward(hi, True))

    def __add__(self, other):
        other = box(other)
        return I.rounded(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-box(other))

    def __rsub__(self, other):
        return box(other) + (-self)

    def __mul__(self, other):
        lo, hi = product(self, box(other))
        return I.rounded(lo, hi)

    __rmul__ = __mul__

    def __rtruediv__(self, other):
        require(self.lo > 0, "positive divisor required")
        lo, hi = product(box(other), I(1/self.hi, 1/self.lo))
        return I.rounded(lo, hi)

    def absolute(self):
        lo = min(abs(self.lo), abs(self.hi)) if self.lo*self.hi > 0 else 0
        return I(lo, max(abs(self.lo), abs(self.hi)))

    def intersect(self, other):
        return I(max(self.lo, other.lo), min(self.hi, other.hi))

    def __repr__(self):
        return f"[{float(self.lo).hex()}, {float(self.hi).hex()}]"

def box(x):
    return x if isinstance(x, I) else I(x)

def product(a, b):
    vals = (a.lo*b.lo, a.lo*b.hi, a.hi*b.lo, a.hi*b.hi)
    return min(vals), max(vals)

def fma(a, b, c):
    lo, hi = product(box(a), box(b))
    c = box(c)
    return I.rounded(lo+c.lo, hi+c.hi)

def ulp(a):
    # Inclusive bound on a single rounding error given an enclosing range.
    v = outward(a.absolute().hi, True)
    return F(math.ulp(float(v)))

def sym(e):
    return I(-e, e)

def root(a):
    require(a.lo > 0, "sqrt domain")
    lo = math.sqrt(float(a.lo))
    hi = math.sqrt(float(a.hi))
    if F(lo)**2 > a.lo:
        lo = math.nextafter(lo, -math.inf)
    if F(hi)**2 < a.hi:
        hi = math.nextafter(hi, math.inf)
    require(0 <= F(lo)**2 <= a.lo and F(hi)**2 >= a.hi, "sqrt outward")
    return I(lo, hi)

def root_residual(ch):
    # ch is rounded sqrt(A). Bound ch^2-A by factoring the difference.
    e = ulp(ch)
    m = ch.absolute().hi
    return sym(outward(e*(2*m+e), True))

def twosum(x, y):
    s = x+y
    z = s-x
    # y-z = -error(x+y)-error(s-x), before its own rounding.
    e = outward(ulp(s)+ulp(z), True)
    return s, (y-z).intersect(sym(e))

def fastsum(x, xl, y, yl):
    h, err = twosum(x,y)
    return h, (xl+yl)+err

def muldd(x, xl, c, cl):
    h = c*x
    return h, (cl*x+c*xl)+sym(ulp(h))

def table(src, decl):
    block = src.split(decl+' = {',1)[1].split('};',1)[0]
    values = lambda s: [I(float.fromhex(v.strip())) for v in s.split(',') if v.strip()]
    rows = re.findall(r'\{([^{}]+)\}',block)
    return [values(row) for row in rows] if rows else values(block)

def ints(i):
    return range(round(i.lo),round(i.hi)+1)

def fast(ax, sign, cc, large):
    x = sign*ax
    if large:
        a = 2-2*ax
        jarg = a*32
        z = -sign*root(a)
        zl = root_residual(z)*((-0.5/a)*z)
        off = I(float.fromhex('0x1.921fb54442d18p+0'))*sign
        tail = I(float.fromhex('0x1.1a62633145c07p-54'))*sign
    else:
        jarg = (x*x)*128
        z, zl, off, tail = x, I(0), I(0), I(0)
    for j in ints(jarg):
        require(0 <= j <= 32,'fast coefficient index')
        t = a*0.25 - F(j,128) if large else fma(x,x,-F(j,128))
        eps = (z*t).absolute()*float.fromhex('0x1.99p-52' if large else '0x1.77p-52')
        c = cc[j]
        t2 = t*t
        d = t*((c[2]+t*c[3])+t2*((c[4]+t*c[5])+t2*(c[6]+t*c[7])))
        h,l = muldd(z,zl,c[0],c[1]+d)
        h,l = fastsum(off,tail,h,l)
        yield h+(l-eps)

def cosine_parts(ax):
    s2 = ax*ax
    dx = sym(ulp(s2))  # rounded exact x*x-s2
    h,l = twosum(I(1),-s2)
    h2,l2 = twosum(h,l-dx)
    if s2.lo >= F(1,2) and s2.hi <= 1:
        # 1-s2 exact by Sterbenz, (1-s2)-1 equals representable -s2.
        # Thus the original low part vanishes, l-dx=-dx, and the real
        # input to the next high rounding is 1-x² minus the FMA error.
        delta = ulp(dx)
        linked = I.rounded(1-ax.hi**2-delta,1-ax.lo**2+delta)
        h2 = h2.intersect(linked)
    ch = root(h2)
    cl = (l2-root_residual(ch))*(0.5/ch)
    return ch,cl

def magic_product(a,b):
    magic = I(float.fromhex('0x1.8p-4'))
    biased = fma(a,b,magic)
    high = biased-magic
    low = fma(a,b,-high).intersect(sym(outward(ulp(biased)+ulp(high),True)))
    return high,low

def refine(ax, sign, j, s, c, ct, ch, cl):
    sl,sh = s[j]
    cltab,chtab = s[32-j]
    dsh,dsl,dch,dcl = ax-sh,-sl,ch-chtab,cl-cltab
    sc,dsc = magic_product(sh,dch)
    cs,dcs = magic_product(chtab,dsh)
    v = cs-sc
    dv = ((chtab*dsl+cltab*dsh)-(sh*dcl+sl*dch))-(dsc-dcs)
    v,dv = twosum(v,dv)
    v2,dv2 = muldd(v,dv,v,dv)
    v,dv = sign*v,sign*dv
    fl = v2*(ct[0]+v2*(ct[1]+v2*ct[2]))
    h,l = twosum(c[4][0],fl)
    l = c[4][1]+l
    for k in (3,2,1,0):
        h,l = muldd(v2,dv2,h,l)
        h,l = fastsum(c[k][0],c[k][1],h,l)
    fh,fl = muldd(v,dv,h,l)
    jt = sign*j
    ph,pl,ps = (I(float.fromhex(t))*jt for t in
                ('0x1.921fb54442dp-5','0x1.8469898cc518p-53','-0x1.fc8f8cbb5bf6cp-102'))
    pl,ps = fastsum(fh,fl,pl,ps)
    ph,pl = twosum(ph,pl)
    pl,ps = twosum(pl,ps)
    ph,pl = twosum(ph,pl)
    return ph

def prove(path):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest()==SOURCE_SHA256,'source identity')
    src = data.decode()
    cc = table(src,'double cc[][8]')
    s = table(src,'double s[33][2]')
    c = table(src,'double c[][2]')
    ct = table(src,'double ct[]')
    require((len(cc),len(s),len(c),len(ct))==(33,33,5,3),'table layout')
    # ax is the magnitude encoding shifted left one bit. Input equality at the
    # tiny cutoff reaches the ordinary caller. The last endpoint precedes 1.
    cutoff_word = int(re.search(r'ax<(0x[0-9a-f]+)ull',src)[1],16)
    require(cutoff_word % 2 == 0,'cutoff encoding')
    cutoff = F(struct.unpack('>d',(cutoff_word//2).to_bytes(8,'big'))[0])
    require(0<cutoff<F(1,256),'cutoff order')
    cuts = [cutoff]+[F(i,256) for i in range(1,256)]+[1-F(1,2**53)]
    scale = float.fromhex(re.search(r'__builtin_fabs\(phi\) \* (0x[\da-f.p+-]+)',src)[1])
    require(float.fromhex('0x1p-26').as_integer_ratio()==(1,2**26),'lower endpoint')
    for jt in range(-32,33):
        for literal in ('0x1.921fb54442dp-5','0x1.8469898cc518p-53'):
            exact = F(float.fromhex(literal))*jt
            require(F(float(exact))==exact,'initial high/low table-angle product')

    indices = set()
    max_arg = F(0)
    min_ph, max_ph, cells = F(10),F(0),0
    for lo,hi in zip(cuts,cuts[1:]):
        ax = I(lo,hi)
        ch,cl = cosine_parts(ax)
        for sign in (-1,1):
            for phi in fast(ax,sign,cc,lo>=F(1,2)):
                arg = phi.absolute()*scale
                max_arg = max(arg.hi,max_arg)
                for j in ints(arg):
                    require(0<=j<=32, f'refinement index {j} at {ax}')
                    ph = refine(ax,sign,j,s,c,ct,ch,cl).absolute()
                    require(ph.lo>=F(1,2**970) and ph.hi<=2,f'ph at {ax}, {sign}, {j}: {ph}')
                    min_ph=min(min_ph,ph.lo)
                    max_ph=max(max_ph,ph.hi)
                    indices.add(j)
                    cells+=1
    return dict(source_sha256=SOURCE_SHA256, input_intervals=len(cuts)-1,
                signed_branch_combinations=cells,possible_indices=sorted(indices),
                rounded_index_argument_upper=float(max_arg).hex(),
                abs_ph_lower=float(min_ph).hex(),abs_ph_upper=float(max_ph).hex(),
                exact_initial_angle_products=130,
                caller_abs_x_lower=float(cutoff).hex(),
                min_biased_exponent=math.frexp(float(min_ph))[1]-1+1023)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path)
    print(json.dumps(prove(p.parse_args().source),indent=2))
