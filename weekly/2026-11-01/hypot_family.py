"""Eight explicit +1 midpoint residuals; exact certificates and full-file membership."""
import sys,json,hashlib,base64,urllib.parse,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import quality as q
from bivariate.make_fixtures import record
from hypot_verify import verify
PIN='5f65574e2b3631fb31e9b88dd27782a936c68095'
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
  m=(1<<51)-1-2*j;x=3*m+2;y=4*m+1;z=5*m+2
  require(x*x+y*y-z*z==1 and z%2==1,'Construction identity')
  require((1<<52)<=x<(1<<53) and (1<<52)<=y<(1<<53),'Input domain')
  require(4*(1<<104)<=x*x+y*y<8*(1<<104),'Result domain')
  # sqrt(z*z+1) is strictly between z and z+1, so distance in ulps
  # 1/(4*z+2) < (sqrt(z*z+1)-z)/2 < 1/(4*z).
  require(4*z>1<<55,'Claimed distance <2^-55 ulp')
  for a,b in [(x,y),(y,x)]:
   r=record(a,b);v=verify(r)
   require(not v['exact'] and v['midpoint_relation']==1,'Independent certificate check')
   rows.append(r)
  details.append({'j':j,'m':str(m),'x_significand':str(x),'y_significand':str(y),'midpoint_scaled':str(z),'squared_residual':1,'ulp_distance_strict_lower':f'1/{4*z+2}','ulp_distance_strict_upper':f'1/{4*z}'})
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
 v=verify(rows[0]);bad=json.loads(json.dumps(rows[0]));bad['expected_bits']['rndn']=bad['lower_bits']
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('Corrupt nearest answer accepted')
 receipt={'schema_version':1,'kind':'restricted-hypot-family-membership','pin':PIN,'family':'x=3m+2,y=4m+1,z=5m+2,m=2^51-1-2j,j=0..7','scope':'16 ordered rows, 8 unordered pairs; no exhaustive census or novelty claim','corpus':{'path':path,'git_blob':meta['blob_id'],'sha256':hashlib.sha256(data).hexdigest(),**counts},'certificates_sha256':q.sha(out/'certificates.json'),'generator_sha256':q.sha(Path(__file__)),'verifier_sha256':q.sha(ROOT/'hypot_verify.py'),'details':details,'membership':matches,'controls':'PASS: sign/swap/power2, adjacent mismatch, zero/nonfinite exclusion, incorrect nearest certificate rejected','all_certificates_verified':True,'completeness_census_regenerated':False}
 q.save(out/'family.json',receipt);print(json.dumps({'rows':len(rows),'corpus':counts,'matching_rows':sum(bool(x['absolute_swap_power2_lines'])for x in matches)}),flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);run(p.parse_args().output)
