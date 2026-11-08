"""Eight explicit -1 midpoint residuals; exact certificates and full-file membership."""
import sys,json,hashlib,base64,urllib.parse,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import quality as q
from bivariate.make_fixtures import record
from hypot_verify import verify
PIN='660067dfd3e751c8f07acc31c899ff410aa7206e'
def require(c,s):
 if not c:raise ValueError(s)
def key(x,y):
 """Absolute, swapped and common power-of-two scaled numeric pair key."""
 if not math.isfinite(x) or not math.isfinite(y) or not x or not y:return None
 a,b=abs(x).as_integer_ratio();c,d=abs(y).as_integer_ratio();den=max(b,d)
 a*=den//b;c*=den//d;t=min((a&-a).bit_length()-1,(c&-c).bit_length()-1)
 return tuple(sorted((a>>t,c>>t)))
def value(bits):return struct.unpack('>d',bytes.fromhex(bits))[0]
def generate():
 rows=[];details=[]
 for j in range(8):
  k=73000000+5*j
  a,b,z=6*k*k-8*k,8*k*k+6*k,2*k*k+1
  require(a%5==b%5==0,'Integrality');x,y=a//5,b//5
  require(z*z-x*x-y*y==1 and z%2==1 and (1<<53)<z<(1<<54),'Midpoint identity')
  require((1<<52)<=x<(1<<53) and (1<<52)<=y<(1<<53),'Input domain')
  require(4*z-2>1<<55,'Distance target')
  for u,v in [(x,y),(y,x)]:
   row=record(u,v);checked=verify(row)
   require(not checked['exact'] and checked['midpoint_relation']==-1,'Expected below midpoint')
   rows.append(row)
  details.append({'k':k,'x_significand':str(x),'y_significand':str(y),'midpoint_scaled':str(z),'squared_residual':-1,'ulp_distance_strict_lower':f'1/{4*z}','ulp_distance_strict_upper':f'1/{4*z-2}'})
 return rows,details
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 rows,details=generate();q.save(out/'certificates.json',rows)
 api=q.read(ROOT/'config/source.json')['project_api'];path='src/binary64/hypot/hypot.wc'
 meta=json.loads(q.get(api+'/repository/files/'+urllib.parse.quote(path,safe='')+'?ref='+PIN));data=base64.b64decode(meta['content'])
 require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta['blob_id'],'Corpus Git blob')
 (out/'hypot.wc').write_bytes(data)
 keys={};counts={'rows':0,'finite_nonzero':0,'zero_or_nonfinite':0};direct={}
 for line,text in enumerate(data.decode('utf-8').splitlines(),1):
  text=text.split('#',1)[0].strip()
  if not text:continue
  fields=text.split(',');require(len(fields)==2,'Malformed corpus line '+str(line))
  def parse(s):
   s=s.strip().lower()
   if 'nan' in s:return float('nan')
   return float.fromhex(s)
  x,y=map(parse,fields);counts['rows']+=1;k=key(x,y)
  if k is None:counts['zero_or_nonfinite']+=1;continue
  counts['finite_nonzero']+=1;keys.setdefault(k,[]).append(line)
  direct.setdefault((x.hex(),y.hex()),[]).append(line)
 matches=[]
 for i,r in enumerate(rows):
  x,y=value(r['x_bits']),value(r['y_bits']);matches.append({'record':i,'x':x.hex(),'y':y.hex(),'direct_lines':direct.get((x.hex(),y.hex()),[]),'absolute_swap_power2_lines':keys.get(key(x,y),[])})
 # Membership negative/positive controls independent of candidate absence.
 require(key(1.5,1.75)==key(-3.5,3.0),'Sign/swap/scaling control')
 require(key(1.5,1.75)!=key(1.5,math.nextafter(1.75,2.0)),'Adjacent pair control')
 require(key(0.0,1.0) is None and key(math.inf,1.0) is None,'Excluded-domain control')
 v=verify(rows[0]);bad=json.loads(json.dumps(rows[0]));bad['expected_bits']['rndn']=bad['upper_bits']
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('Corrupt nearest answer accepted')
 receipt={'schema_version':1,'kind':'restricted-hypot-family-membership','pin':PIN,'family':'x=(6k²-8k)/5,y=(8k²+6k)/5,z=2k²+1,k=73000000+5j,j=0..7','scope':'16 ordered rows, 8 unordered pairs; no exhaustive census or novelty claim','corpus':{'path':path,'git_blob':meta['blob_id'],'sha256':hashlib.sha256(data).hexdigest(),**counts},'certificates_sha256':q.sha(out/'certificates.json'),'generator_sha256':q.sha(Path(__file__)),'verifier_sha256':q.sha(ROOT/'hypot_verify.py'),'details':details,'membership':matches,'controls':'PASS: sign/swap/power2, adjacent mismatch, zero/nonfinite exclusion, incorrect nearest certificate rejected','all_certificates_verified':True,'completeness_census_regenerated':False}
 q.save(out/'family.json',receipt);print(json.dumps({'rows':len(rows),'corpus':counts,'matching_rows':sum(bool(x['absolute_swap_power2_lines'])for x in matches)}),flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);run(p.parse_args().output)
