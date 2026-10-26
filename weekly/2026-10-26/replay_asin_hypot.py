"""Bounded secondary tasks. No coverage campaign, no exp work.
Asin candidate is a portability cleanup, not a confirmed value fix.
"""
from pathlib import Path
import sys,shutil,time,resource,difflib
W=Path(__file__).resolve().parent;Q=W.parents[1];sys.path.insert(0,str(Q))
import quality as q
PIN='336752ca18e1204321225ec90c1f43fcb90ada1b'
OUT=Q/'.work/candidates/20261026-asin-hypot'
OLD='  long dn = (long)tl.u-(long)tn.u, de = (long)((tn.u - tl.u)>>52);'
NEW='  uint64_t gap = tn.u - tl.u;'
PRED='  int hard = (-2<=dn && dn<=0) || (de>47);'
REPLACEMENT='  int hard = (gap <= 2) || ((gap >> 52) > 47);'

def main():
    OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN);records=[]
    with q.locked():
        source=q.fetch(PIN,['asin','hypot'])/'src/binary64'
        for profile in ['gcc-linux-x86_64','clang-linux-x86_64']:
            env=q.doctor(profile);flags=q.flags(q.profile(profile),1)
            for variant in ['asin-portable','asin-sanitized','hypot-timing']:
                fn='hypot' if variant=='hypot-timing' else 'asin';wd=OUT/(profile+'-'+variant);wd.mkdir();inputs={}
                for folder in [source/'support',source/fn]:
                    for p in folder.iterdir():
                        if p.is_file() and p.suffix!='.wc':shutil.copyfile(p,wd/p.name);inputs[p.relative_to(source).as_posix()]=q.sha(p)
                checks=[]
                def run(label,args,corpus=None):
                    left=1200-(time.monotonic()-start)
                    if left<=0:raise TimeoutError('Overall cap')
                    print(profile,variant,label,flush=True)
                    with open(corpus,'rb') if corpus else q.contextlib.nullcontext(None) as inp:r=q.command(args,cwd=wd,stdin=inp,timeout=min(left,240))
                    checks.append({'label':label,'command':args,**r});assert r['returncode']==0,r;return r
                if fn=='asin':
                    p=wd/'asin.c';s=p.read_text();assert OLD in s and PRED in s
                    if variant=='asin-portable':
                        new=s.replace(OLD,NEW).replace(PRED,REPLACEMENT)
                        p.write_text(new)
                        (OUT/'asin-unsigned-gap.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),new.splitlines(True),fromfile='a/src/binary64/asin/asin.c',tofile='b/src/binary64/asin/asin.c')))
                    extra=['-fsanitize=undefined,float-cast-overflow','-fno-sanitize-recover=all'] if variant=='asin-sanitized' else []
                    if extra:
                        (wd/'sanitizer-control.c').write_text('#include <limits.h>\nint main(int argc,char **argv){volatile int x=INT_MAX;return x+argc;}\n')
                        run('sanitizer-control-build',[q.profile(profile)['cc'],*extra,'sanitizer-control.c','-o','sanitizer-control'])
                        control=q.command(['./sanitizer-control'],cwd=wd,timeout=10)
                        assert control['returncode']!=0 and 'signed integer overflow' in control['output']
                        checks.append({'label':'expected-sanitizer-rejection','command':['./sanitizer-control'],**control})
                    run('build',[q.profile(profile)['cc'],*flags,*extra,'-I.','check_worst_uni.c','asin.c','asin_mpfr.c','-lmpfr','-lgmp','-lm','-o','check'])
                    corpus=source/'asin/asin.wc';rows,expected=q.expected_rows(corpus,wd/'function_under_test.h')
                    for mode in q.MODES:
                        r=run('corpus-'+mode,['./check','--'+mode],corpus);q.check_output(r,expected)
                        checks[-1].update(mode=mode,rows=rows,expected_tests=expected,corpus_sha256=q.sha(corpus))
                else:
                    shutil.copyfile(W/'hypot_timing.c',wd/'timing.c')
                    run('build',[q.profile(profile)['cc'],*flags,'hypot.c','timing.c','-lmpfr','-lgmp','-lm','-o','timing'])
                    r=run('timing',['./timing']);assert 'value_failures=0 flag_failures=0 errno_failures=0' in r['output']
                records.append({'profile':profile,'environment':env,'variant':variant,'pin':PIN,'flags':flags,
                    'inputs_sha256':inputs,'compiled_source_sha256':q.sha(wd/(fn+'.c')),'checks':checks,'status':'PASS'})
                c=resource.getrusage(resource.RUSAGE_CHILDREN)
                q.save(OUT/'replay.json',{'results':records,'complete':len(records)==6,'runner_sha256':q.sha(Path(__file__)),
                    'quality_sha256':q.sha(Q/'quality.py'),'child_cpu_seconds':c.ru_utime+c.ru_stime-c0.ru_utime-c0.ru_stime,'wall_seconds':time.monotonic()-start})

if __name__=='__main__':main()
