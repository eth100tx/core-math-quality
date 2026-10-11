"""Bounded supplementary checks; source caches are read-only."""
from pathlib import Path
import sys,json,shutil,re,time,resource,math,struct,difflib
Q=Path(__file__).resolve().parents[2]
R=Q/'.work/20261011-supplement'
R.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(Q));import quality as q
PIN='81a899d67953a619d703660fd9630f0554673524'
SRC=Q/'.work/sources'/PIN/'src/binary64'
OUT=R/'focused';OUT.mkdir(exist_ok=True)
FLAGS=['-frounding-math','-fno-finite-math-only','-ffp-contract=off','-march=x86-64','-DCORE_MATH_NO_OPENMP','-DCORE_MATH_CHECK_INEXACT','-DCORE_MATH_SUPPORT_ERRNO']
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def instrument(fn,s):
 prefix='#include <stdio.h>\n#include <stdint.h>\nstatic unsigned long long audit_n,audit_bad,audit_diff,audit_x,audit_tail;\n__attribute__((destructor)) static void audit_report(void){fprintf(stderr,"AUDIT n=%llu bad=%llu diff=%llu x=%016llx tail=%016llx\\n",audit_n,audit_bad,audit_diff,audit_x,audit_tail);}\n'
 if fn=='log2':
  s=replace(s,'int d = ((int)((t.u^w.u)>>63))*2 + 1;', 'audit_n++; if((t.u^w.u)>>63){audit_bad++;audit_x=((b64u64_u){.f=x}).u;}\n    int d = ((int)((t.u^w.u)>>63))*2 + 1;')
 elif fn in ('sinh','cosh'):
  s=s.replace('// b64u64_u uh =', 'b64u64_u uh =').replace('// int64_t eh =','int64_t eh =')
  pat=r'((?:int64_t|int) ml = \(ul.u \+ 8\)&\(~0ul>>12\);)'
  def ins(m):
   return m[0]+'\n audit_n++; uint64_t audit_wide=(ul.u+8)&(~0ul>>12); if(audit_wide>16 && eh-el>103) audit_bad++; if((ml<=16)!=(audit_wide<=16)){audit_diff++;if(!audit_x){audit_x=((b64u64_u){.f=x}).u;audit_tail=ul.u;}}'
  s,n=re.subn(pat,ins,s);assert n==2,n
 elif fn=='exp2':
  s=replace(s,'// we assume fl is not be zero here','audit_n++; if((ix.u<<1)==0){audit_bad++;audit_x=((b64u64_u){.f=x}).u;}\n        // we assume fl is not be zero here')
 else: raise ValueError(fn)
 return prefix+s
def extra(fn,s,wd):
 vals={float.fromhex(x) for x in re.findall(r'[-+]?0x[0-9a-fA-F.]+p[-+]?\d+',s)}
 vals.update(float(k) for k in range(-1075,1025))
 vals.update(float(10**k) for k in range(23))
 for b in [2.0**-54,2.0**-12,2.0**-5,2.0**51,2.0**52,36.736801]:
  for sign in [-1,1]:
   x=b*sign
   for direction in [-math.inf,math.inf]:
    y=x
    for _ in range(65):vals.add(y);y=math.nextafter(y,direction)
 vals.update([0.,-0.,math.ldexp(1.,-1074),-math.ldexp(1.,-1074),math.nextafter(math.ldexp(1.,-1022),0),-math.nextafter(math.ldexp(1.,-1022),0)])
 p=wd/'extra.wc';p.write_text(''.join(x.hex()+'\n' for x in sorted(vals) if math.isfinite(x)))
 return p
def database_instrument(s):
 start=s.index('as_exp');start=s.index('while (a <= b)',start);end=s.index('return f;',start)
 body=s[start:end]
 body,n=re.subn(r'(for\((?:i64|int64_t) \w+ = -1;[^\n]+\{)',r'audit_n++; \1',body);assert n==1
 body=replace(body,'      }\n    } else {','      }\n      audit_bad++; fprintf(stderr,"DATABASE EXHAUSTION\\n"); __builtin_abort();\n    } else {')
 prefix='#include <stdio.h>\nstatic unsigned long long audit_n,audit_bad;\n__attribute__((destructor)) static void audit_report(void){fprintf(stderr,"DATABASE entries=%llu exhausted=%llu\\n",audit_n,audit_bad);}\n'
 return prefix+s[:start]+body+s[end:]
def cell(fn,cc,opt,kind):
 name=f'{fn}-{cc}-{opt}-{kind}';wd=OUT/name;wd.mkdir(exist_ok=True)
 for folder in [SRC/'support',SRC/fn]:
  for p in folder.iterdir():
   if p.is_file():shutil.copyfile(p,wd/p.name)
 original=(wd/(fn+'.c')).read_text();s=original
 if kind=='instrumented':s=instrument(fn,s)
 if kind=='database':s=database_instrument(s)
 if kind=='candidate':
  if fn=='log2':s=replace(s,'((int)((t.u^w.u)>>63))*2 + 1','1 - 2*(int)((t.u^w.u)>>63)')
  if fn=='sinh':s=replace(s,'int ml = (ul.u + 8)&(~0ul>>12);','int64_t ml = (ul.u + 8)&(~0ul>>12);')
  patch=''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile=f'a/src/binary64/{fn}/{fn}.c',tofile=f'b/src/binary64/{fn}/{fn}.c'))
  (OUT/(fn+'.patch')).write_text(patch)
 (wd/(fn+'.c')).write_text(s)
 extras=extra(fn,original,wd)
 if kind=='database':
  table=re.search(r'static const double db\[\] = \{(.*?)\};',original,re.S)[1]
  keys=re.findall(r'[-+]?0x[0-9a-fA-F.]+p[-+]?\d+',table)
  bits=[struct.unpack('>Q',struct.pack('>d',float.fromhex(x)))[0] for x in keys]
  assert bits==sorted(set(bits))
  extras=wd/'database.wc';extras.write_text('\n'.join(keys)+'\n')
 flags=[opt,*FLAGS]
 if cc=='gcc':flags+=['-fsignaling-nans']
 if kind=='shift':flags+=['-fsanitize=shift','-fno-sanitize-recover=shift']
 if kind=='finite':flags+=['-ffinite-math-only']
 result={'function':fn,'compiler':cc,'flags':flags,'kind':kind,'source_pin':PIN,'upstream_source_sha256':q.sha(SRC/fn/(fn+'.c')),'tested_source_sha256':q.sha(wd/(fn+'.c')),'checks':[]}
 before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.monotonic()
 def invoke(label,args,inp=None):
  print(name,label,flush=True)
  q.save(OUT/'status.json',{'state':'RUNNING','cell':name,'operation':label,'heartbeat_utc':q.utc()})
  with open(inp,'rb') if inp else q.contextlib.nullcontext(None) as f:rec=q.command(args,cwd=wd,stdin=f,timeout=600)
  rec['command']=args;rec['output']=rec['output'].replace(str(R),'<private-work>')
  (wd/(label+'.log')).write_text(rec['output']);result['checks'].append({'label':label,**rec})
  if rec['returncode']:raise RuntimeError(name+' '+label+' '+rec['output'][-1200:])
  return rec
 try:
  if kind=='finite':
   invoke('function-build',[cc,*flags,'-I.','-c',fn+'.c','-o','finite.o'])
   checker_flags=[f for f in flags if f!='-ffinite-math-only']
   result['checker_flags']=checker_flags
   invoke('checker-build-link',[cc,*checker_flags,'-I.','check_worst_uni.c','finite.o',fn+'_mpfr.c','-lmpfr','-lgmp','-lm','-o','check'])
  else:invoke('build',[cc,*flags,'-I.','check_worst_uni.c',fn+'.c',fn+'_mpfr.c','-lmpfr','-lgmp','-lm','-o','check'])
  inputs=[extras] if kind in ('literals','database') else [wd/(fn+'.wc'),extras]
  for wc in inputs:
   rows,expected=q.expected_rows(wc,wd/'function_under_test.h')
   for mode in q.MODES:
    rec=invoke(wc.stem+'-'+mode,['./check','--'+mode],wc);q.check_output(rec,expected)
    result['checks'][-1].update(corpus_sha256=q.sha(wc),rows=rows,expected_tests=expected,mode=mode)
  result['status']='PASS'
 except Exception as e:result.update(status='FAIL_OR_INCOMPLETE',error=str(e))
 after=resource.getrusage(resource.RUSAGE_CHILDREN)
 result['child_cpu_seconds']=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime;result['wall_seconds']=time.monotonic()-started
 q.save(wd/'cell.json',result);return result
def main():
 jobs=[]
 for cc,opt in [('gcc','-O0'),('gcc','-O3'),('clang-18','-O3')]:
  jobs += [(fn,cc,opt,'database') for fn in ['exp','exp2','exp10']]
 for cc in ['gcc','clang-18']:
  jobs += [(fn,cc,'-O3','instrumented') for fn in ['log2','sinh','cosh','exp2']]
  jobs += [(fn,cc,'-O3','shift') for fn in ['sinpi','cospi']]
  jobs += [(fn,cc,'-O3','literals') for fn in ['exp','exp10','log','log10']]
  jobs += [(fn,cc,'-O3','candidate') for fn in ['log2','sinh']]
  jobs += [('sin',cc,'-O3','finite')]
 jobs += [('log2','gcc','-O0','instrumented')]
 jobs += [(fn,'clang-18','-O3','plain') for fn in ['log2','sinh']]
 results=[]
 with q.locked():
  environment=q.doctor('clang-linux-x86_64')
  q.save(OUT/'clang-qualification.json',environment)
  for job in jobs:
   path=OUT/('-'.join([job[0],job[1],job[2],job[3]]))/'cell.json'
   if path.exists() and q.read(path).get('status')=='PASS':results.append(q.read(path));continue
   res=cell(*job);results.append(res)
   if res['status']!='PASS':break
 q.save(OUT/'summary.json',{'source_pin':PIN,'completed':len(results),'planned':len(jobs),'results':results,'status':'PASS' if len(results)==len(jobs) and all(x['status']=='PASS' for x in results) else 'INCOMPLETE'})
 q.save(OUT/'status.json',{'state':'DONE','completed':len(results),'heartbeat_utc':q.utc()})
if __name__=='__main__':main()
