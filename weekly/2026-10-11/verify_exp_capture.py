"""Offline replay of the finite-key residue condition; no debugger or compiler needed."""
from pathlib import Path
import sys,json,hashlib,re,struct
R=Path(__file__).resolve().parent
p=Path(sys.argv[1]);source=p.read_text();sha=hashlib.sha256(p.read_bytes()).hexdigest()
keys=re.findall(r'[-+]?0x[0-9a-fA-F.]+p[-+]?\d+',re.search(r'static const double db\[\] = \{(.*?)\};',source,re.S)[1])
bits=[struct.unpack('>Q',struct.pack('>d',float.fromhex(x)))[0] for x in keys]
assert bits==sorted(set(bits)) and len(bits)==51
s2=[int(x,16) for x in re.findall(r'0x[0-9a-f]+',re.search(r'static const u64 s2\[2\] = \{(.*?)\}',source)[1])]
sets=[]
for folder in ['production-capture','coverage-capture']:
 d=json.loads((R/folder/'receipt.json').read_text());assert d['status']=='PASS'
 assert d['source_sha256']==sha and d['binary_sha256']==d['captured_copy_sha256']
 assert d['key_bits']==[format(x,'016x') for x in bits]
 assert [x['mode'] for x in d['modes']]==['rndn','rndz','rndu','rndd']
 bymode={}
 for m,modebits in zip(d['modes'],[0,3,2,1]):
  assert m['tested_public_keys']==m['accepted_tests']==51 and m['failures']==m['returncode']==0
  assert len(m['observations'])==m['helper_calls']>0
  assert len({x['x_bits'] for x in m['observations']})==m['distinct_helper_keys']
  vals=[]
  for o in m['observations']:
   x=int(o['x_bits'],16);f=int(o['f_bits'],16);i=bits.index(x)
   residue=(s2[i>>5]>>((2*i)&63))&3
   assert i==o['key_index'] and residue==o['stored_residue']
   assert ((f+2)&3)==o['exhaustion_residue']!=residue
   assert ((o['mxcsr']>>13)&3)==modebits
   assert o['mxcsr']&((1<<15)|(1<<6))==0
   vals.append((x,f))
  bymode[m['mode']]=sorted(vals)
 sets.append(bymode)
assert sets[0]==sets[1]
print('PASS: all51 keys replayed in four modes; every observed helper argument excludes exhaustion; O3/O0 argument multisets agree. This checks the saved evidence, not a portable arithmetic proof or the truth of the acquisition record.')
