"""Fetch only public pinned inputs and verify their recorded SHA256."""
from pathlib import Path
import json,hashlib,urllib.request,urllib.parse,sys
R=Path(__file__).resolve().parent;m=json.loads((R/'SOURCE-METADATA.json').read_text());p=m['repositories']['source'];pin=p['pin']
def fetch(rel,out,expected):
 if out.is_file() and hashlib.sha256(out.read_bytes()).hexdigest()==expected:return
 url='https://gitlab.inria.fr/api/v4/projects/35719/repository/files/'+urllib.parse.quote(rel,safe='')+'/raw?ref='+pin
 with urllib.request.urlopen(url,timeout=90) as response:data=response.read(128*1024*1024)
 assert hashlib.sha256(data).hexdigest()==expected,'Pinned input mismatch'
 out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);print('Verified',rel)
rel='src/binary64/sin/sin.c';fetch(rel,R/'source'/rel,p['hashes'][rel])
if '--corpus' in sys.argv:
 receipt=R/'runs/candidate-full/sin-gcc-linux-x86_64-errno1/cell.json'
 d=json.loads(receipt.read_text());fetch('src/binary64/sin/sin.wc',R/'candidate-source/src/binary64/sin/sin.wc',d['corpus_sha256'])
