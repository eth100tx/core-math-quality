"""Bounded noncoverage regression of pinned sine and its forced accurate path.
Run from the workbench under an outer 30-minute job monitor. Immutable cache
is blob-verified; only copies in .work are compiled or instrumented.
"""
from pathlib import Path
import sys, shutil, time, resource, math
W=Path(__file__).resolve().parent; Q=W.parents[1];sys.path.insert(0,str(Q))
import quality as q
PIN='336752ca18e1204321225ec90c1f43fcb90ada1b'
OUT=Q/'.work/candidates/20261026-sine-v2'

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();cpu=time.process_time();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    records=[]
    with q.locked():
        source=q.fetch(PIN,['sin'])/'src/binary64'
        for profile in ['gcc-linux-x86_64','clang-linux-x86_64']:
            env=q.doctor(profile)
            for variant in ['normal','forced-accurate']:
                wd=OUT/(profile+'-'+variant);wd.mkdir()
                inputs={}
                for folder in [source/'support',source/'sin']:
                    for p in folder.iterdir():
                        if p.is_file() and p.suffix!='.wc':
                            shutil.copyfile(p,wd/p.name);inputs[p.relative_to(source).as_posix()]=q.sha(p)
                if variant=='forced-accurate':
                    p=wd/'sin.c';s=p.read_text();assert s.count('\ncr_sin (double x)')==1
                    s=s.replace('\ncr_sin (double x)','\noriginal_cr_sin (double x)')
                    s+='\n/* Test-only wrapper: actual large-accurate caller domain. */\ndouble cr_sin(double x) { return __builtin_isfinite(x) && __builtin_fabs(x)>=0x1p-16 ? sin_large_accurate(x) : original_cr_sin(x); }\n'
                    p.write_text(s)
                flags=q.flags(q.profile(profile),1); checks=[]
                def run(label,args,corpus=None):
                    remaining=1500-(time.monotonic()-start)
                    if remaining<=0:raise TimeoutError('Overall cap')
                    print(profile,variant,label,flush=True)
                    with open(corpus,'rb') if corpus else q.contextlib.nullcontext(None) as inp:
                        r=q.command(args,cwd=wd,stdin=inp,timeout=min(240,remaining))
                    checks.append({'label':label,'command':args,**r});return r
                r=run('build',[q.profile(profile)['cc'],*flags,'-I.','check_worst_uni.c','sin.c','sin_mpfr.c','-lmpfr','-lgmp','-lm','-o','check'])
                assert r['returncode']==0,r
                # Full corpus plus exact binary64 neighbors of dispatch and angle boundaries.
                vals=set()
                for v in [float.fromhex('0x1.7137449123ef6p-26'),2**-16,2.0**31,math.pi,2*math.pi,math.pi/2,*[i*math.pi/64 for i in [31,32,33,63,64]]]:
                    vals.add(v)
                    for d in [-math.inf,math.inf]:
                        t=v
                        for _ in range(64):t=math.nextafter(t,d);vals.add(t)
                corpus=wd/'boundaries.wc';corpus.write_text(''.join(x.hex()+'\n' for x in sorted(vals)))
                for corpus in [source/'sin/sin.wc',corpus]:
                    rows,expected=q.expected_rows(corpus,wd/'function_under_test.h')
                    for mode in q.MODES:
                        r=run(corpus.stem+'-'+mode,['./check','--'+mode],corpus)
                        checks[-1].update(mode=mode,rows=rows,expected_tests=expected,corpus_sha256=q.sha(corpus))
                        q.check_output(r,expected)
                records.append({'profile':profile,'environment':env,'variant':variant,'pin':PIN,
                    'inputs_sha256':inputs,'compiled_source_sha256':q.sha(wd/'sin.c'),'binary_sha256':q.sha(wd/'check'),
                    'flags':flags,'checks':checks,'status':'PASS'})
                c=resource.getrusage(resource.RUSAGE_CHILDREN)
                q.save(OUT/'replay.json',{'results':records,'complete':len(records)==4,'runner_sha256':q.sha(Path(__file__)),
                    'quality_sha256':q.sha(Q/'quality.py'),'child_cpu_seconds':c.ru_utime+c.ru_stime-c0.ru_utime-c0.ru_stime,
                    'self_cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-start})
    print('DONE: normal and forced accurate checks passed',flush=True)

if __name__=='__main__':main()
