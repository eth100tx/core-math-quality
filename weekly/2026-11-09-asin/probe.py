"""Build and test the comment-only patch and observe actual refinement calls."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import tempfile

from verify_asin import SOURCE_SHA256
HERE = Path(__file__).resolve().parent
RUNNER = r'''
#include <fenv.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#pragma STDC FENV_ACCESS ON
extern double cr_asin(double);
extern int taken;
extern double observed_phi, observed_j, observed_ph;
int main(void) {
    const int modes[] = {FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
    double x;
    while (scanf("%la", &x)==1) {
        for (int i=0;i<4;i++) {
            if (fesetround(modes[i])) return 1;
            taken=0;
            volatile double y=cr_asin(x);
            (void)y;
            if(taken) printf("%a %d %a %a %a\n",x,i,observed_phi,observed_j,observed_ph);
        }
    }
    return 0;
}
'''

def cmd(args, cwd, **options):
    return subprocess.run(args,cwd=cwd,capture_output=True,text=True,check=True,timeout=120,**options)

def run(source, ranges):
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError('source identity')
    src=raw.decode()
    vals={float.fromhex(x) for x in re.findall(r'\{(0x1\.[a-f0-9]+p[-+]\d+),',src.split('double db[][3] = {')[1])}
    vals.update(i/4096 for i in range(1,4097))
    vals.update(math.nextafter(1-2.0**-k,1) for k in range(1,54))
    vals.update([math.nextafter(1.,0.),math.nextafter(0.5,0.),math.nextafter(0.5,1.)])
    inputs=sorted(vals|{-x for x in vals})
    reports=[]
    with tempfile.TemporaryDirectory() as tmp:
        td=Path(tmp)
        unit=td/'src/binary64/asin/asin.c';unit.parent.mkdir(parents=True)
        driver=td/'driver.c';driver.write_text(RUNNER)
        for cc,arch,contract in [(c,a,f) for c in ('gcc','clang-18') for a,f in (('x86-64','off'),('x86-64-v3','fast'))]:
            flags=['-O3','-frounding-math','-ffp-contract='+contract,'-fno-finite-math-only','-march='+arch,'-DCORE_MATH_SUPPORT_ERRNO']
            unit.write_bytes(raw)
            compile_args=[cc,*flags,'-c',str(unit.relative_to(td)),'-o','asin.o']
            cmd(compile_args,td);orig=(td/'asin.o').read_bytes()
            cmd(['git','apply',str(HERE/'asin-signed-index.patch')],td)
            cmd(compile_args,td)
            if (td/'asin.o').read_bytes()!=orig:raise ValueError('patch changed object bytes')
            marker='  b64u64_u th = {.f = ph}'
            if src.count(marker)!=1:raise ValueError('instrumentation site')
            unit.write_text('int taken; double observed_phi, observed_j, observed_ph;\n'+src.replace(marker,'  taken=1; observed_phi=phi; observed_j=jf; observed_ph=ph;\n'+marker))
            cmd([cc,*flags,'driver.c',str(unit.relative_to(td)),'-lm','-o','probe'],td)
            obs=cmd(['./probe'],td,input=''.join(x.hex()+'\n' for x in inputs)).stdout.splitlines()
            per_mode=[0]*4;exponents=[];indices=[];negative=None
            for row in obs:
                x,m,phi,j,ph=row.split();j=float.fromhex(j);ph=float.fromhex(ph)
                be=(struct.unpack('>Q',struct.pack('>d',ph))[0]>>52)&2047
                if not (j.is_integer() and 0<=j<=32 and float.fromhex(ranges['abs_ph_lower'])<=abs(ph)<=float.fromhex(ranges['abs_ph_upper'])):raise ValueError(row)
                per_mode[int(m)]+=1;exponents.append(be);indices.append(int(j))
                if j>0 and float.fromhex(x)<0 and negative is None:negative=dict(x=x,mode=['nearest','zero','up','down'][int(m)],j=int(j),jt=-int(j),ph=ph.hex())
            if min(per_mode)==0 or negative is None:raise ValueError('missing reached cases')
            reports.append(dict(profile=arch, contraction=contract, compiler=cmd([cc,'--version'],td).stdout.splitlines()[0],flags=flags,
                                input_count=len(inputs),calls=4*len(inputs),refinements_by_mode=per_mode,
                                observed_index_range=[min(indices),max(indices)],observed_biased_exponent_range=[min(exponents),max(exponents)],
                                negative_jt_example=negative,object_sha256=hashlib.sha256(orig).hexdigest(),patch_object_identical=True))
    return reports
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);args=p.parse_args()
    print(json.dumps(run(args.source,json.loads((HERE/'range.json').read_text())),indent=2))
