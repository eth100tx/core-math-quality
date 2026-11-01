"""Bounded, source-pinned sine preprocessing regression check; no numerical claim."""
import sys,json,time,hashlib,resource,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import quality as q
PIN='5f65574e2b3631fb31e9b88dd27782a936c68095'
BASE='b5a3f7ffb9315afae57a309623c3c5c226ec8bec'
def main():
 start=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_CHILDREN);own=time.process_time()
 wd=ROOT/'.work/candidates/20261101-sin-build'
 if wd.exists():raise ValueError('Preserve prior run; output directory already exists')
 wd.mkdir(parents=True)
 receipt={'schema_version':1,'kind':'sine-build-regression','status':'INCOMPLETE','pin':PIN,'base':BASE,'profiles':[],'sources':{},'scope':'Standalone strict compilation and preprocessed token equivalence, not numerical tests','driver_sha256':q.sha(Path(__file__))}
 def save():q.save(wd/'receipt.json',receipt)
 save()
 try:
  with q.locked():
   for label,pin in [('current',PIN),('previous',BASE)]:
    api=q.read(ROOT/'config/source.json')['project_api']
    path='src/binary64/sin/sin.c'
    meta=json.loads(q.get(api+'/repository/files/'+urllib.parse.quote(path,safe='')+'?ref='+pin))
    import base64
    data=base64.b64decode(meta['content']);blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!=meta['blob_id']:raise ValueError('Git blob mismatch')
    (wd/(label+'.c')).write_bytes(data);receipt['sources'][label]={'git_blob':blob,'sha256':hashlib.sha256(data).hexdigest()}
   old=(wd/'current.c').read_bytes()
   if old.count(b'#if1\n')!=1:raise ValueError('Unexpected patch context')
   (wd/'fixed.c').write_bytes(old.replace(b'#if1\n',b'#if 1\n'))
   receipt['sources']['fixed']={'sha256':q.sha(wd/'fixed.c')}
   for profile in ['gcc-linux-x86_64','clang-linux-x86_64']:
    env=q.doctor(profile);p=q.profile(profile);flags=q.flags(p,True)+['-fno-lto']
    cell={'profile':profile,'doctor':env,'flags':flags,'checks':{}};receipt['profiles'].append(cell)
    for label in ['current','previous','fixed']:
     out=q.command([p['cc'],*flags,'-c',label+'.c','-o',label+'.o'],cwd=wd,timeout=60)
     cell['checks'][label]={'returncode':out['returncode'],'output':out['output'],'output_truncated':out['output_truncated']}
     expected=label!='current'
     if out['output_truncated'] or (out['returncode']==0)!=expected:raise ValueError('Unexpected compilation outcome')
    for label in ['previous','fixed']:
     out=q.command([p['cc'],*flags,'-E','-P',label+'.c','-o',label+'.i'],cwd=wd,timeout=60)
     if out['returncode']:raise ValueError('Preprocessing failed')
    # Comments/line directives omitted; whitespace does not affect C token sequence here.
    import re
    token=lambda label:re.findall(r'\w+|[^\s\w]',(wd/(label+'.i')).read_text())
    same=token('previous')==token('fixed');cell['fixed_previous_preprocessed_tokens_identical']=same
    if not same:raise ValueError('Unexpected change to active preprocessed code')
    print(profile,'original fails; one-character fix and previous compile; active tokens match',flush=True);save()
   receipt['status']='PASS'
 finally:
  c=resource.getrusage(resource.RUSAGE_CHILDREN);receipt['cost']={'child_cpu_seconds':c.ru_utime+c.ru_stime-cpu.ru_utime-cpu.ru_stime,'parent_cpu_seconds':time.process_time()-own,'wall_seconds':time.monotonic()-start};save()
if __name__=='__main__':main()
