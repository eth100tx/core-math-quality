"""Observe helper arguments in the byte-identical uninstrumented primary binary."""
from pathlib import Path
import sys,json,shutil,re,struct,time,resource
Q=Path(__file__).resolve().parents[2];R=Q/'.work/20261011-supplement';R.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(Q));import quality as q
binary=sys.argv[1] if len(sys.argv)>1 else 'plain';assert binary in ('plain','covered')
O=R/('production-capture' if binary=='plain' else 'coverage-capture');O.mkdir(exist_ok=True)
B=Q/'.work/runs/20261011-baseline-gcc-e1/exp-gcc-linux-x86_64-errno1'
source=(B/'exp.c').read_text();keys=re.findall(r'[-+]?0x[0-9a-fA-F.]+p[-+]?\d+',re.search(r'static const double db\[\] = \{(.*?)\};',source,re.S)[1])
bits=[struct.unpack('>Q',struct.pack('>d',float.fromhex(x)))[0] for x in keys];assert bits==sorted(set(bits)) and len(bits)==51
par=[int(x,16) for x in re.findall(r'0x[0-9a-f]+',re.search(r'static const u64 s2\[2\] = \{(.*?)\}',source)[1])]
(O/'database.wc').write_text('\n'.join(keys)+'\n');shutil.copyfile(B/binary,O/'plain')
assert q.sha(O/'plain')==q.sha(B/binary)
before=resource.getrusage(resource.RUSAGE_CHILDREN);rows=[]
with q.locked():
 for label,args in [('symbols',['nm','plain']),('disassembly',['objdump','-d','--disassemble=as_exp_database','plain']),('gdb-version',['gdb','--version'])]:
  rec=q.command(args,cwd=O,timeout=30);assert rec['returncode']==0;(O/(label+'.txt')).write_text(rec['output'])
 assert re.search(r'\bt as_exp_database\b',(O/'symbols.txt').read_text())
 for mode,roundbits in [('rndn',0),('rndz',3),('rndu',2),('rndd',1)]:
  print('Production exp argument capture',mode,flush=True)
  script='''set pagination off
set confirm off
set disable-randomization off
set environment GCOV_PREFIX gcov-counts
set environment GCOV_PREFIX_STRIP 99
python
import gdb,json
class Probe(gdb.Breakpoint):
 def stop(self):
  x=int(gdb.parse_and_eval('(unsigned long long)$xmm0.v2_int64[0]'))
  f=int(gdb.parse_and_eval('(unsigned long long)$xmm1.v2_int64[0]'))
  mx=int(gdb.parse_and_eval('$mxcsr'))
  print('PROBE '+json.dumps({'x_bits':format(x,'016x'),'f_bits':format(f,'016x'),'mxcsr':mx}))
  return False
Probe('*as_exp_database')
end
run --'''+mode+' < database.wc\n'
  (O/(mode+'.gdb')).write_text(script)
  rec=q.command(['gdb','-q','--batch','-x',mode+'.gdb','--args','./plain'],cwd=O,timeout=180)
  rec['output']=rec['output'].replace(str(R),'<review>');(O/(mode+'.log')).write_text(rec['output'])
  q.check_output(rec,51)
  observations=[json.loads(s[6:]) for s in rec['output'].splitlines() if s.startswith('PROBE ')]
  assert observations
  for row in observations:
   x=int(row['x_bits'],16);f=int(row['f_bits'],16);assert x in bits
   m=bits.index(x);p=(par[m>>5]>>((m<<1)&63))&3
   row.update(key_index=m,stored_residue=p,exhaustion_residue=(f+2)&3)
   assert ((row['mxcsr']>>13)&3)==roundbits
   assert (row['mxcsr']&((1<<15)|(1<<6)))==0 # FTZ/DAZ off
   assert row['exhaustion_residue']!=p
  rows.append({'mode':mode,'tested_public_keys':51,'helper_calls':len(observations),'distinct_helper_keys':len({x['x_bits'] for x in observations}),'observations':observations,'returncode':rec['returncode'],'accepted_tests':51,'failures':0,'wall_seconds':rec['wall_seconds']})
after=resource.getrusage(resource.RUSAGE_CHILDREN)
q.save(O/'receipt.json',{'status':'PASS','binary_kind':binary,'source_pin':'81a899d67953a619d703660fd9630f0554673524','source_sha256':q.sha(B/'exp.c'),'binary_sha256':q.sha(B/binary),'captured_copy_sha256':q.sha(O/'plain'),'baseline_cell':'20261011-baseline-gcc-e1/exp-gcc-linux-x86_64-errno1','flags':q.read(B/'result.json')['flags' if binary=='plain' else 'coverage_flags'],'environment':q.read(B/'result.json')['environment'],'key_bits':[format(x,'016x') for x in bits],'modes':rows,'child_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'scope':'Finite necessary trigger set; unchanged primary GCC binary observed at helper entry. Plain is O3/uninstrumented; covered is original O0/gcov binary. Offline residue check excludes inner-loop exhaustion for all observed helper arguments. No claim about other binaries/platforms or arbitrary helper f.'})
print('PASS all production helper arguments satisfy three-neighbor residue condition',flush=True)
