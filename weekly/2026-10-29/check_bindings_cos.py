"""Check coefficient binding and exact numeric implications of Gappa output.
Usage: python3 check_bindings.py sin.c acclarge.g sin.tex gappa_dir polynomials.json output.json
This does not certify the reducer, tables, dispatcher or rounding-hardness census.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
from math import ceil,log2
import json,re,sys,hashlib

def power(exp,up=False):
    e=F(exp)
    with localcontext() as ctx:
        ctx.prec=100; v=Decimal(2)**(256-Decimal(exp))
        n=ceil(v) if up else int(v)
    v=F(n,1<<256)
    lhs=v.numerator**e.denominator*(1<<e.numerator);rhs=v.denominator**e.denominator
    assert lhs>=rhs if up else lhs<=rhs
    return v

def main():
    paths=list(map(Path,sys.argv[1:5]));src,g,tex=[x.read_text() for x in paths[:3]];bindings=[]
    cert=json.loads(Path(sys.argv[5]).read_text())
    assert cert['source_sha256']==hashlib.sha256(paths[0].read_bytes()).hexdigest()
    receipt=json.loads((paths[3]/'gappa.json').read_text())
    assert receipt['complete'] and len(receipt['results'])==13
    assert receipt['source_sha256']==hashlib.sha256(paths[1].read_bytes()).hexdigest()
    for i,r in enumerate(receipt['results']):
        assert r['returncode']==0 and 'Unproved' not in r['output']
        assert (paths[3]/('%02d.log'%i)).read_text()==r['output']
        assert hashlib.sha256((paths[3]/('%02d.g'%i)).read_bytes()).hexdigest()==r['model_sha256']
    # Bind the ideal references' variable, alternating signs and powers too.
    statements=re.sub(r'\s+','',re.sub(r'#[^\n]*','',g)).split(';')
    for expected in ['R=8*r','U=R','u=R','U2=U*U','U4=U2*U2',
                     'S5=c5-c7*U2','T1=c3*U2','S1=c1-T1','T2=S5*U4','S2=S1+T2','Sr=S2*U',
                     'C6=v6-v8*U2','T3=C6*U2','C4=v4-T3','T4=v2*U2','C0=v0-T4','T5=C4*U4','Cr=C0+T5',
                     'SR=Sr+eps5','CR=Cr+eps4']:
        assert expected in statements,expected
    approximations={r['table']:F(r['target']) for r in cert['results']}
    assert set(approximations)=={'PS','PC'}
    for index,table,variable in [(4,'PS','eps5'),(10,'PC','eps4')]:
        goal=receipt['results'][index]['goal']
        m=re.search(variable+r' in \[-(\d+)b(-?\d+),(\d+)b(-?\d+)\]',goal);assert m
        assert m[1]==m[3] and m[2]==m[4]
        bound=F(int(m[1]))*F(2)**int(m[2]);assert approximations[table]<=bound
    for table,names in [('PS',['c1','c3','c5','c7']),('PC',['v0','v2','v4','v6','v8'])]:
        body=re.search(r'\b'+table+r'\[\] = \{(.*?)\};',src,re.S).group(1)
        vals=[(int(h,0)<<64)|int(l,0) for l,h in re.findall(r'U128\((0x[0-9a-f]+|0),(0x[0-9a-f]+|0)\)',body)]
        assert len(vals)==len(names)
        for i,(name,value) in enumerate(zip(names,vals)):
            m=re.search(r'^'+name+r' = (0x[0-9a-f]+)p-(\d+);',g,re.M);assert m
            assert value==int(m[1],16) and int(m[2])==(64 if i==len(vals)-1 else 128)
            tag=name[0]+'_'+name[1]
            m=re.search(re.escape(tag)+r' = \\texttt\{(0x[0-9a-f]+)\}',tex);assert m
            assert value==int(m[1],16)
            bindings.append({'name':name,'integer':str(value),'scale':int(re.search(r'^'+name+r' = 0x[0-9a-f]+p-(\d+);',g,re.M)[1])})
    bounds={}
    for i,exp in [(3,'126.414'),(4,'126.128'),(9,'126.369'),(10,'125.966'),(11,'124.414'),(12,'125.264')]:
        log=(paths[3]/('%02d.log'%i)).read_text()
        goal_label={3:'|sr - Sr|',4:'|sr - SR|',9:'|cr - Cr|',10:'|cr - CR|',11:'|w1 - W1|',12:'|w2 - W2|'}[i]
        matches=re.findall(re.escape(goal_label)+r' in \[0, (\d+)b(-?\d+)',log);assert len(matches)==1
        m=[None,*matches[0]]
        v=F(int(m[1]))*F(2)**int(m[2]);assert v<power(exp)
        bounds[str(i)]={'exact_upper':str(v),'published_power':exp,'checked':True}
    # Convert the October 8 fractional-turn bound to sine-output units.
    # Sine is 1-Lipschitz; Machin's identity supplies an exact pi enclosure.
    from certify_polynomials import atan
    _,h5=atan(5); l239,_=atan(239)
    pi_upper=16*h5-4*l239
    fractional=F(1,1<<128)+F(1,1<<139)
    reduction=2*pi_upper*fractional
    assert reduction<power('125.347')
    assert r'\label{eq2}' in tex and r'|{\cos}(2\pi(z + R)) - \cos(x)| < 2^{-125.347}' in tex
    total=F(bounds['11']['exact_upper'])+F(bounds['12']['exact_upper'])+power('125.347',True)
    assert total<power('123.358')
    result={'coefficients_bound':bindings,'gappa_bounds':bounds,'aggregate_absolute_upper':str(total),
            'aggregate_log2_display':log2(float(total)),
            'polynomial_hypotheses_bound':True,
            'reduction_error':{'fractional_turn_upper':str(fractional),'cosine_output_upper':str(reduction),
                               'published_output_power':'125.347','output_units_verified':True,
                               'premise':'Three-word truncation bound; exact table/index certificate and source binding in this review',
                               'conversion':'2*pi times fractional-turn error; cosine is 1-Lipschitz; current TeX eq2'},
            'aggregate_premises':'Triangle inequality for the same signed table/residual decomposition; Gappa table-error hypotheses and prior certified reducer bound with exact output-unit conversion checked here',
            'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths[:3]}}
    Path(sys.argv[6]).write_text(json.dumps(result,indent=2)+'\n')
    print('Nine coefficients bound to C, Gappa and TeX; six bounds and aggregate verified')

if __name__=='__main__':main()
