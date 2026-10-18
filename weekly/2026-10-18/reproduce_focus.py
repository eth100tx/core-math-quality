from pathlib import Path
import sys,json,re,math,shutil,resource,time,struct
W=Path(__file__).resolve().parent;Q=W.parents[1];R=Q/'.work/20261018-supplement';R.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(Q));import quality as q
PIN='dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3';SRC=Q/'.work/sources'/PIN/'src/binary64';OUT=R/'focused';OUT.mkdir(exist_ok=True)
def numbers(path):
 for line in path.read_text().splitlines():
  line=line.split('#')[0].strip()
  if not line:continue
  try:yield float.fromhex(line)
  except ValueError:continue
def extra(fn,wd):
 vals=set()
 if fn=='exp':
  p=wd/'extra.wc';shutil.copyfile(W/'exp-extra.wc',p);return p
 else:
  for x in numbers(SRC/'rsqrt/rsqrt.wc'):
   if x>0 and math.isfinite(x):
    m,e=math.frexp(x);vals.add(math.ldexp(m,1023))
  for center in [math.ldexp(1.,e) for e in [-1022,-2,0,2,1022,1023]]:
   bits=struct.unpack('Q',struct.pack('d',center))[0]
   vals.update(struct.unpack('d',struct.pack('Q',b))[0] for b in range(bits-16384,bits+16385))
 vals={x for x in vals if math.isfinite(x)};p=wd/'extra.wc';p.write_text(''.join(x.hex()+'\n' for x in sorted(vals)));return p
def cell(fn,cc,contract,variant):
 name=f'{fn}-{cc}-v3-{contract}-{variant}';wd=OUT/name
 if (wd/'receipt.json').exists():
  old=q.read(wd/'receipt.json')
  if old['status']=='PASS' or (variant=='upstream' and old['status']=='FAIL'):return old
 wd.mkdir(exist_ok=True)
 for folder in [SRC/'support',SRC/fn]:
  for p in folder.iterdir():
   if p.is_file():shutil.copyfile(p,wd/p.name)
 src=(wd/(fn+'.c'));s=src.read_text()
 if variant.startswith('candidate'):
  assert s.count('e<0x7fe')==1;s=s.replace('e<0x7fe','e<0x7fd')
 if variant=='epsilon-candidate':
  assert s.count('double eps = 1.64e-19;')==1;s=s.replace('double eps = 1.64e-19;','double eps = 0x1.27p-62;')
 if variant=='forced-accurate':
  assert s.count('double cr_exp(double x)')==1;s=s.replace('double cr_exp(double x)','double original_cr_exp(double x)')
  s+='\ndouble cr_exp(double x) { union { double f; uint64_t u; } audit_x={.f=x}; if((audit_x.u & UINT64_C(0x7ff0000000000000)) != UINT64_C(0x7ff0000000000000) && x > -0x1.74910d52d3052p+9 && x < 0x1.62e42fefa39fp+9 && __builtin_fabs(x)>0x1p-54) { if(x < -0x1.6232bdd7abcd2p+9) errno=ERANGE; return as_exp_accurate(x); } return original_cr_exp(x); }\n'
 if variant=='candidate-observed':
  needle='  u64 d = (idr.u + 18)&~0ull>>13;';assert s.count(needle)==1
  s=s.replace(needle,'  if(dr != 0) { audit_n++; if(de<audit_min) audit_min=de; if(de<52) audit_small++; }\n'+needle)
  s='#include <stdio.h>\nstatic unsigned long long audit_n,audit_small;static int audit_min=9999;\n__attribute__((destructor)) static void audit_report(void){fprintf(stderr,"AUDIT n=%llu de_min=%d de_below52=%llu\\n",audit_n,audit_min,audit_small);}\n'+s
 src.write_text(s);extras=extra(fn,wd)
 flags=q.flags(q.profile('gcc-linux-x86_64-v3' if cc=='gcc' else 'clang-linux-x86_64'),1)
 flags=[('-march=x86-64-v3' if f.startswith('-march=') else '-ffp-contract='+contract if f.startswith('-ffp-contract=') else f) for f in flags]
 record={'function':fn,'compiler':cc,'isa':'x86-64-v3','contraction':contract,'variant':variant,'pin':PIN,'source_sha256':q.sha(SRC/fn/(fn+'.c')),'tested_source_sha256':q.sha(src),'flags':flags,'checks':[],'extra_rows':q.expected_rows(extras,wd/'function_under_test.h')[0]};start=resource.getrusage(resource.RUSAGE_CHILDREN)
 def invoke(label,cmd,inp=None):
  print(name,label,flush=True)
  with open(inp,'rb') if inp else q.contextlib.nullcontext(None) as f:res=q.command(cmd,cwd=wd,stdin=f,timeout=600)
  res['command']=cmd;(wd/(label+'.log')).write_text(res['output']);record['checks'].append({'label':label,**res});return res
 try:
  build=invoke('build',[cc,*flags,'-I.','check_worst_uni.c',fn+'.c',fn+'_mpfr.c','-lmpfr','-lgmp','-lm','-o','check']);assert build['returncode']==0,build['output']
  failures=[]
  for corpus in [wd/(fn+'.wc'),extras]:
   rows,expected=q.expected_rows(corpus,wd/'function_under_test.h')
   for mode in q.MODES:
    res=invoke(corpus.stem+'-'+mode,['./check','--'+mode],corpus);record['checks'][-1].update(rows=rows,expected_tests=expected,mode=mode,corpus_sha256=q.sha(corpus))
    try:q.check_output(res,expected)
    except RuntimeError as e:
     record['checks'][-1]['verification_error']=str(e);failures.append(str(e))
  # Retain assembly counts to distinguish an enabled option from actual contraction.
  obj=invoke('assembly',[cc,*flags,'-I.','-S',fn+'.c','-o','function.s']);assert obj['returncode']==0
  asm=(wd/'function.s').read_text();record['fused_instruction_count']=len(re.findall(r'\bvfm(?:add|sub|nadd|nsub)\w*',asm));record['assembly_sha256']=q.sha(wd/'function.s');record['status']='FAIL' if failures else 'PASS';record['failures']=failures
 except Exception as e:record.update(status='FAIL_OR_INCOMPLETE',error=str(e))
 end=resource.getrusage(resource.RUSAGE_CHILDREN);record['child_cpu_seconds']=end.ru_utime+end.ru_stime-start.ru_utime-start.ru_stime;q.save(wd/'receipt.json',record);return record
def validate_completed_cell(record):
 """Fail closed on any failure other than the exact documented exp/RZ case."""
 fn=record['function']
 expected=['build']+[prefix+'-'+mode for prefix in [fn,'extra'] for mode in q.MODES]+['assembly']
 if [c['label'] for c in record['checks']] != expected:
  raise RuntimeError('Incomplete or unexpected checker sequence')
 failures=[]
 for check in record['checks']:
  if check['label'] not in ('build','assembly') and 'expected_tests' not in check:
   raise RuntimeError('Mode check missing accepted-count expectation')
  if 'expected_tests' in check:
   try:q.check_output(check,check['expected_tests'])
   except RuntimeError:failures.append(check)
  elif check['returncode']!=0:
   raise RuntimeError('Build/assembly did not complete')
 if not failures:
  if record['status']!='PASS':raise RuntimeError('Receipt status inconsistent with checks')
  return
 known='FAIL x=0x1.5a3a157335f3bp+9 ref=0x1.ffdebdc4e28abp+998 z=0x1.ffdebdc4e28acp+998'
 if not (record['status']=='FAIL' and fn=='exp' and record['variant']=='upstream' and record['contraction']=='off' and len(failures)==1 and failures[0]['label']=='extra-rndz' and failures[0]['mode']=='rndz' and failures[0]['returncode']==1 and failures[0]['output'].strip()==known and not failures[0]['output_truncated']):
  raise RuntimeError('Unexpected failure; retain receipt and stop for review')

with q.locked():
 q.fetch(PIN,['rsqrt','exp','asinh','atanh','cospi','tanpi'])
 q.save(OUT/'qualification.json',{p:q.doctor(p) for p in ['gcc-linux-x86_64-v3','clang-linux-x86_64']})
 results=[]
 for fn,cc,contract,variant in [('rsqrt','gcc','off','candidate-observed'),('rsqrt','gcc','off','candidate'),('rsqrt','gcc','fast','candidate'),('rsqrt','clang-18','off','candidate'),('rsqrt','clang-18','on','candidate'),('exp','gcc','off','upstream'),('exp','gcc','fast','upstream'),('exp','clang-18','off','upstream'),('exp','clang-18','on','upstream'),('exp','gcc','off','epsilon-candidate'),('exp','gcc','fast','epsilon-candidate'),('exp','clang-18','off','epsilon-candidate'),('exp','clang-18','on','epsilon-candidate'),('exp','gcc','off','forced-accurate')]:
  result=cell(fn,cc,contract,variant);results.append(result);q.save(OUT/'summary.json',{'results':results})
  validate_completed_cell(result)
 builds=[]
 for fn in ['asinh','atanh','cospi','tanpi']:
  wd=OUT/('special-build-'+fn);wd.mkdir(exist_ok=True)
  for folder in [SRC/'support',SRC/fn]:
   for p in folder.iterdir():
    if p.is_file():shutil.copyfile(p,wd/p.name)
  for profile in ['gcc-linux-x86_64','clang-linux-x86_64']:
   cmd=[q.profile(profile)['cc'],*q.flags(q.profile(profile),1),'-I.','check_special.c',fn+'.c',fn+'_mpfr.c','-lmpfr','-lgmp','-lm','-o','check_special'];res=q.command(cmd,cwd=wd,timeout=60);builds.append({'function':fn,'profile':profile,'command':cmd,**res})
   q.save(OUT/'special-builds.json',builds)
   if res['returncode']!=0:raise RuntimeError('Special-checker build failed; receipt retained')
 q.save(OUT/'special-builds.json',builds)
