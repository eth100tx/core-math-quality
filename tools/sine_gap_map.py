#!/usr/bin/env python3
"""Pinned helper experiment: map branch indices, never infer public reachability."""
from pathlib import Path
import sys,shutil,json,gzip
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P));import quality as q
with q.locked():
 profile=q.profile('gcc-linux-x86_64')
 environment=q.doctor('gcc-linux-x86_64')
 pin=q.read(P/'config/source.json')['default_pin']
 src=q.fetch(pin,['sin'])/'src/binary64/sin'
 assert q.sha(src/'sin.c') == 'be00fff46e6778510d76c06d43110c7365dc9bd76b54637fccbae8e3a4e9dbd0', 'Review branch mapping against changed sine source'
 wd=P/'.work/sine-branch-map';wd.mkdir(parents=True,exist_ok=True)
 for f in src.iterdir():
  if f.is_file():shutil.copyfile(f,wd/f.name)
 (wd/'map.c').write_text('#include "sin.c"\n#include <stdio.h>\nint main(int argc,char **argv){u128 r=(u128)1 << (argc>1 ? 63 : 127); volatile double y=u128_tod(r,0); printf("%a\\n",y); return 0;}\n')
 coverage_flags=['-O0','-g']+q.flags(profile,1)[1:]+['--coverage']
 q.checked([profile['cc'],*coverage_flags,'-I.','map.c','-lm','-o','map'],cwd=wd)
 out={'scope':'Internal helper branch mapping only; not public cr_sin reachability or rounding validation','pin':pin,'source_sha256':q.sha(src/'sin.c'),'coverage_flags':coverage_flags,'environment':environment,'tool_sha256':q.sha(Path(__file__)),'cases':{}}
 for name,args in [('high-half-nonzero',[]),('high-half-zero',['low'])]:
  for f in wd.glob('*.gcda'):f.unlink()
  q.checked(['./map',*args],cwd=wd)
  q.checked([profile['gcov'],'-b','-c','-j','map.gcno'],cwd=wd)
  d=json.loads(gzip.decompress((wd/'map.gcov.json.gz').read_bytes()))
  sf=next(f for f in d['files'] if Path(f['file']).name=='sin.c')
  ln=next(l for l in sf['lines'] if l.get('function_name')=='u128_tod' and l['line_number']==96)
  out['cases'][name]=[b['count'] for b in ln['branches']]
 assert out['cases']=={'high-half-nonzero':[1,0],'high-half-zero':[0,1]},out
 (wd/'result.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Verified missing sine branch 1 corresponds to high-half zero; no public reachability claim',flush=True)
