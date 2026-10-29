"""Exact Taylor/Bernstein certificate for the pinned scaled sine polynomials.

Usage: python3 certify_polynomials.py sin.c output.json
Standard library only. Machin's identity and alternating series enclose pi;
all decisive comparisons are rational/integer. No dirty norm is trusted.
"""
from fractions import Fraction as F
from math import comb, factorial, isqrt, ceil, log2
from decimal import Decimal, localcontext
from pathlib import Path
import re, json, sys, hashlib, time

def atan(q, n=160):
    s = sum((F((-1)**k, (2*k+1)*q**(2*k+1)) for k in range(n)), F(0))
    e = F(1, (2*n+1)*q**(2*n+1))
    return s, s+e  # n even: the first omitted term is positive

def bern(c, a, b):
    n = len(c)-1
    d = [(b-a)**j * sum((c[k]*comb(k,j)*a**(k-j) for k in range(j,n+1)),F(0)) for j in range(n+1)]
    v = [sum((d[j]*F(comb(i,j),comb(n,j)) for j in range(i+1)),F(0)) for i in range(n+1)]
    return min(v), max(v)

def main():
    start = time.process_time()
    source = Path(sys.argv[1]).read_bytes()
    tables = {}
    for name in ['PS','PC']:
        body = re.search(r'\b'+name+r'\[\] = \{(.*?)\};',source.decode(),re.S).group(1)
        vals = [(int(hi,0)<<64)|int(lo,0) for lo,hi in re.findall(r'U128\((0x[0-9a-f]+|0),(0x[0-9a-f]+|0)\)',body)]
        assert len(vals) == (4 if name=='PS' else 5)
        tables[name] = [F((-1)**i*v,1<<(64 if i==len(vals)-1 else 128)) for i,v in enumerate(vals)]
    l5,h5=atan(5); l239,h239=atan(239)
    pl,ph=16*l5-4*h239,16*h5-4*l239
    D=1<<512; pl=F((pl*D).__floor__(),D); ph=F(ceil(ph*D),D)
    # alpha includes X=t^(1/2)*2^-11, hence target argument pi/8192*sqrt(t).
    alo,ahi=pl/8192,ph/8192
    with localcontext() as ctx:
        ctx.prec=100
        goal=F(int(Decimal(2)**(160-Decimal('128.605'))),1<<160)
    # Exact confirmation that the chosen dyadic target is below 2^-128.605.
    assert goal.numerator**200 * (1<<25721) < goal.denominator**200
    results=[]
    for name,odd in [('PS',1),('PC',0)]:
        lo=[]; hi=[]
        for k in range(9):
            j=2*k+odd
            p=tables[name][k]*F(1,1<<(11*j)) if k<len(tables[name]) else F(0)
            tl,th=alo**j/factorial(j),ahi**j/factorial(j)
            if k%2: tl,th=-th,-tl
            lo.append(p-th);hi.append(p-tl)
        # Taylor through sin degree17 / cos degree16. Bound next term with t^9.
        j=19 if odd else 18
        rem=ahi**j/factorial(j)
        lo.append(-rem);hi.append(rem)
        target=goal if odd else F(1,1<<128)
        cells=[]; stack=[(F(0),F(1),0)]
        while stack:
            a,b,depth=stack.pop()
            if odd:
                low,_=bern(lo,a,b); _,high=bern(hi,a,b)
                sqrt_b=F(isqrt((b.numerator<<512)//b.denominator)+1,1<<256)
                upper=max(abs(low),abs(high))*sqrt_b
                ok=upper<=target
            else:
                # At zero the lower bound is attained exactly. Divide the
                # lower comparison by t, avoiding a spurious endpoint epsilon.
                assert lo[0]==hi[0]==-target
                lower,_=bern(lo[1:],a,b)
                up=hi.copy();up[0]-=target
                _,higher=bern(up,a,b)
                ok=lower>=0 and higher<=0
                upper=target
            if ok:
                cells.append({'lo':str(a),'hi':str(b),'absolute_upper':str(F(ceil(upper*(1<<256)),1<<256))})
            else:
                if depth>=24 or len(cells)+len(stack)>10000:
                    raise RuntimeError('Certificate subdivision cap reached: '+name)
                m=(a+b)/2;stack.extend([(a,m,depth+1),(m,b,depth+1)])
        # Check accepted intervals cover [0,1] exactly with no gap/overlap.
        intervals=sorted((F(c['lo']),F(c['hi'])) for c in cells)
        assert intervals[0][0]==0 and intervals[-1][1]==1
        assert all(x[1]==y[0] for x,y in zip(intervals,intervals[1:]))
        results.append({'table':name,'target':str(target),'log2_target_display':log2(float(target)),
                        'cells':cells,'coefficient_values':[str(x) for x in tables[name]],'status':'PROVED'})
        print(name,'proved',len(cells),'cells',flush=True)
    out={'method':'Exact rational Machin pi enclosure, Taylor remainder, Bernstein convex hull; t=(2048*X)^2 in [0,1]',
         'source_sha256':hashlib.sha256(source).hexdigest(),'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'pi_lower':str(pl),'pi_upper':str(ph),'results':results,'cpu_seconds':time.process_time()-start}
    Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__': main()
