"""Run the explicit family through the qualified adapter with fresh controls."""
import sys,time,resource,shutil,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import quality as q
import hypot_run as h
from hypot_verify import read_table,MODES,loads
from hypot_family import run as family,PIN
def main():
 start=time.monotonic();cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);own=time.process_time();deadline=start+600
 wd=ROOT/'.work/bivariate/20261108-hypot-below'
 if wd.exists():raise ValueError('Existing run; preserve evidence and use a fresh reviewed output path')
 wd.mkdir(parents=True)
 files=['hypot_run.py','hypot_verify.py','quality.py','bivariate/hypot_probe.c','bivariate/make_fixtures.py','config/profiles.json','config/source.json','weekly/2026-11-08/run_hypot_family.py','weekly/2026-11-08/hypot_family.py']
 receipt={'schema_version':1,'kind':'restricted-hypot-family-execution','pin':PIN,'status':'INCOMPLETE','profiles':[],'files':{p:q.sha(ROOT/p)for p in files},'scope':'16 ordered family rows only; no full-corpus execution or census','cost':{}}
 def save():q.save(wd/'execution.json',receipt)
 def command(a,limit=60):
  left=deadline-time.monotonic()
  if left<=0:raise RuntimeError('Overall ten-minute bound')
  return q.command(a,cwd=wd,timeout=min(limit,left))
 def checked(a):
  d=command(a)
  if d['returncode'] or d['output_truncated']:raise RuntimeError('Command failed: '+d['output'][-1000:])
  return d
 save()
 try:
  with q.locked():
   family(wd);rows=read_table(wd/'certificates.json');receipt['certificates_sha256']=q.sha(wd/'certificates.json');receipt['source']=h.fetch_source(PIN,wd);save()
   for name in ['gcc-linux-x86_64','clang-linux-x86_64']:
    env=q.doctor(name);p=q.profile(name);flags=q.flags(p,True)+['-fno-lto'];adapter=flags+(['-ffp-exception-behavior=strict']if p['cc'].startswith('clang')else[])
    cell={'profile':name,'doctor':env,'compiler_driver_sha256':q.sha(Path(shutil.which(p['cc'])).resolve()),'library_flags':flags,'adapter_flags':adapter,'observations':[],'controls':[],'binaries':{}};receipt['profiles'].append(cell)
    checked([p['cc'],*flags,'-c','hypot.c','-o','hypot.o'])
    if not any(x.endswith(' T cr_hypot')for x in checked(['nm','--defined-only','hypot.o'])['output'].splitlines()):raise ValueError('Wrong linked implementation')
    cell['symbol_check']='local hypot.o defines cr_hypot'
    def build(label,extra,lib=True):
     checked([p['cc'],*adapter,*extra,str(ROOT/'bivariate/hypot_probe.c'),*(['hypot.o']if lib else[]),'-lmpfr','-lgmp','-lm','-o',label]);cell['binaries'][label]=q.sha(wd/label)
    build('normal',[]);build('oracle',['-DORACLE'],False)
    cell['oracle_libraries']={}
    for line in checked(['ldd','oracle'])['output'].splitlines():
     if ('libmpfr.so' in line or 'libgmp.so' in line) and '=>' in line:
      lib=Path(line.split('=>')[1].strip().split()[0]);cell['oracle_libraries'][lib.name]=q.sha(lib.resolve())
    if len(cell['oracle_libraries'])!=2:raise ValueError('Oracle libraries not bound')
    for i,row in enumerate(rows):
     for mode in MODES:
      args=[row['x_bits'],row['y_bits'],mode];oracle=loads(checked(['./oracle',*args])['output'])
      if h.classify(oracle,row,mode,True)!='PASS':raise ValueError('MPFR disagreement')
      obs=loads(checked(['./normal',*args])['output']);code=h.classify(obs,row,mode)
      cell['observations'].append({'record':i,'mode':mode,'observation':obs,'oracle':oracle,'status':code})
      if code!='PASS':raise ValueError('Candidate failure '+code)
     if i%4==0:print(name,'family row',i+1,'of',len(rows),flush=True);save()
    for fault,expected in [(1,'VALUE'),(2,'MODE'),(3,'INPUT'),(4,'FLAGS'),(5,'ERRNO'),(6,'TIMEOUT')]:
     label='control'+str(fault);build(label,['-DFAULT='+str(fault)])
     try:
      out=command(['./'+label,rows[0]['x_bits'],rows[0]['y_bits'],'rndu'],0.2 if fault==6 else 10)
      actual=h.classify(loads(out['output']),rows[0],'rndu')if out['returncode']==0 else'PROCESS'
     except RuntimeError as e:
      if str(e).startswith('TIMEOUT:'):actual='TIMEOUT'
      else:raise
     cell['controls'].append({'fault':fault,'expected':expected,'observed':actual})
     if actual!=expected:raise ValueError('Control mismatch')
    cell['status']='PASS';save()
   if any(q.sha(ROOT/p)!=v for p,v in receipt['files'].items()):raise ValueError('Input changed')
   receipt['status']='PASS'
 except BaseException as e:receipt['failure']=q.clean(str(e));raise
 finally:
  c=resource.getrusage(resource.RUSAGE_CHILDREN);receipt['cost']={'child_cpu_seconds':c.ru_utime+c.ru_stime-cpu0.ru_utime-cpu0.ru_stime,'parent_cpu_seconds':time.process_time()-own,'wall_seconds':time.monotonic()-start};save()
 print('PASS family execution',flush=True)
if __name__=='__main__':main()
