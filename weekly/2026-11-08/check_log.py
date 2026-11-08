"""Check the near-one polynomial and replay separately scoped Gappa obligations.
Usage: python3 check_log.py PATH/TO/src/binary64/log [--receipt FILE]
Requires Python 3 and Gappa. No source edits. All series bounds are rational.
"""
import argparse, hashlib, json, re, subprocess, tempfile
from fractions import Fraction as F
from math import comb
from pathlib import Path

def check(b, msg):
    if not b:
        raise ValueError(msg)

def approx(c):
    # Divide P(r)-sum_{j=1}^12 (-1)^(j-1)r^j/j by r; evaluate at r=0 by continuity.
    rho = F(1,512)
    p = [F(1), *c] + [F(0)]*5
    a = [v-F((-1)**n,n+1) for n,v in enumerate(p)]
    # Absolute tail of log(1+r)/r beginning with r^12/13.
    tail = rho**12/(13*(1-rho))
    bound = F(0)
    for i in range(128):
        half = rho/128
        mid = -rho+(2*i+1)*half
        # Coefficients of D(mid+s), |s|<=half, via the binomial theorem.
        b = [sum(a[n]*comb(n,k)*mid**(n-k) for n in range(k,len(a))) for k in range(len(a))]
        bound = max(bound, sum(abs(v)*half**k for k,v in enumerate(b))+tail)
    return bound

def main(root, emit=None):
    csrc=(root/'log.c').read_bytes(); orig=(root/'logtiny.g').read_bytes()
    check(hashlib.sha256(csrc).hexdigest()=='73f778e1ca7656fa473fc48e934ac5d359d4fd7d3c2d8ebcaa2edd5ff09b3eb5','log.c identity')
    check(hashlib.sha256(orig).hexdigest()=='00710f4662d2b2f3c5d4fb99ee5de4b1e4b5d77367c4eb8462cb1cc2a4660f91','logtiny.g identity')
    unit=csrc.decode().split('cr_log_tiny (double x)',1)[1]
    tokens=re.search(r'static const double c\[\] = \{([^}]*)\}',unit).group(1).split(',')
    c=[F.from_float(float.fromhex(t.strip())) for t in tokens]
    g=orig.decode(); check(len(c)==6 and all(t.strip()==re.search(rf'^c{i} = (.*);',g,re.M).group(1) for i,t in enumerate(tokens)),'coefficient binding')
    b=approx(c);limit=F(1,2**70);check(b<limit,'polynomial target')
    # Independent enclosure: power-to-Bernstein coefficients on 32 cells.
    # If D(L+hu)=sum A_j*u^j, Bernstein coefficient i is
    # sum_{j<=i} A_j*C(i,j)/C(n,j). On [0,1] the basis is a convex partition.
    power=[v-F((-1)**i,i+1) for i,v in enumerate([F(1),*c]+[F(0)]*5)]
    n=len(power)-1;rho=F(1,512);bern=F(0)
    for cell in range(32):
        h=2*rho/32;L=-rho+cell*h
        A=[sum(power[l]*comb(l,j)*L**(l-j) for l in range(j,n+1))*h**j for j in range(n+1)]
        bern=max(bern,max(abs(sum(A[j]*F(comb(i,j),comb(n,j)) for j in range(i+1))) for i in range(n+1)))
    bern+=rho**12/(13*(1-rho))
    check(bern<limit,'independent Bernstein target')
    check(approx([c[0]+F(1,2**48),*c[1:]])>limit,'coefficient fault not detected')
    eps=F.from_float(float.fromhex(re.search(r'static const double eps = ([^;]*);',unit).group(1)))
    check(F(29,2**65)+limit+F(1,2**80)<eps,'conditional stopping margin')
    versions=subprocess.check_output(['gappa','--version'],text=True).strip()
    out={'polynomial_error_over_abs_r_upper':str(b),'strict_target':'2^-70','coefficient_fault_detected':True,'bernstein_upper':str(bern),'gappa_version':versions,'runs':[]}
    # Publish a transcript of each goal's success/failure. An unsuccessful proof
    # is unresolved, not a counterexample. Interval inclusion goal fails via nonzero rc.
    template=g[:g.index('# { r in')] # definitions only
    domain='(r in [1b-52,1b-9] \\/ r in [-1b-9,-1b-53]) /\\ @FIX(r,-53)'
    with tempfile.TemporaryDirectory() as td:
        for style in ('contracted','separate','gcc-v3-fused-residual'):
            defs=template
            if style=='gcc-v3-fused-residual':
                # Actual observed GCC v3 fast-contraction graph: product NOT
                # rounded before h or l. h-r is exact under the Sterbenz goal.
                old='t rnd= r2 * p2a;';check(defs.count(old)==1,'t binding')
                defs=defs.replace(old,'t = r2 * p2a;')
            if style=='separate':
                for dest,u,v,w in [('p6','c4','r','c5'),('p4','c2','r','c3'),('p2','c0','r','c1'),('p4a','p4','r2','p6'),('p2a','p2','r2','p4a')]:
                    old=f'{dest} rnd= {u}+{v}*{w};'
                    check(defs.count(old)==1,'operation binding');defs=defs.replace(old,f'm_{dest} rnd= {v}*{w};\n{dest} rnd= {u}+m_{dest};')
                defs=defs.replace('l_l rnd= l - eps*r;', 'er rnd= eps*r;\nl_l rnd= l - er;').replace('l_h rnd= l + eps*r;', 'l_h rnd= l + er;')
            for mode in ('ne','zr','up','dn'):
                for kind,goal in [('sum','|(y-Y)/r| <= 29b-65'),('endpoints','|err_l/r| <= 1b-103 /\\ |err_h/r| <= 1b-103'),('sterbenz','h/r in [0.5,2]')]+([('budget_endpoints','|err_l/r| <= 1b-80 /\\ |err_h/r| <= 1b-80')] if mode=='zr' else []):
                    src=defs.replace('RND',mode)+'{ '+domain+' -> '+goal+' }\n'
                    if kind=='sum':src+='y-(r+t) -> l - (-(h-(r+t)));\n'
                    f=Path(td)/'obligation.g';f.write_text(src)
                    digest=hashlib.sha256(src.encode()).hexdigest()
                    if emit:
                        emit.mkdir(parents=True,exist_ok=True)
                        (emit/f'{style}-{mode}-{kind}.g').write_bytes(src.encode())
                    try:
                        r=subprocess.run(['gappa',str(f)],capture_output=True,text=True,timeout=12)
                        code=r.returncode;diag=(r.stdout+r.stderr).replace(str(f),'obligation.g')[-1400:]
                    except subprocess.TimeoutExpired:
                        code=None;diag='12-second limit'
                    out['runs'].append({'style':style,'mode':mode,'goal':kind,'rc':code,'diagnostic':diag,'input_sha256':hashlib.sha256(src.encode()).hexdigest()})
    # The two stronger RZ targets for old/strict graphs are diagnostic only.
    required=[v for v in out['runs'] if not (v['mode']=='zr' and v['goal']=='endpoints' and v['style']!='gcc-v3-fused-residual')]
    out['required_goals']=len(required)
    out['required_pass']=len(required)==37 and all(v['rc']==0 for v in required)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--emit',type=Path,help='optional output directory for standalone Gappa obligations');a=p.parse_args()
    res=main(a.root,a.emit);s=json.dumps(res,indent=2)+'\n'
    if a.receipt:a.receipt.write_text(s)
    else:print(s,end='')
    if not res['required_pass']:raise SystemExit(1)
