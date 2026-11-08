"""Receipt replay with a separate exact-rational membership cross-check."""
import sys,json,re,math,hashlib,urllib.parse,base64,subprocess,tempfile
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import quality as q
from hypot_verify import read_table,verify,MODES
from hypot_run import classify
def need(c,m):
 if not c:raise ValueError(m)
def exact(s):
 s=s.strip().lower()
 if s.lstrip('+-') in ('inf','nan','snan'):return None
 if '0x' not in s:
  need(s in ('-0','+0','0','-1','+1','1'),'Unsupported finite decimal syntax')
  return Fraction(s)
 m=re.fullmatch(r'([+-]?)0x([0-9a-f]*)(?:\.([0-9a-f]*))?(?:p([+-]?\d+))?',s)
 need(m is not None,'Unknown corpus syntax')
 sign,a,b,e=m.groups();b=b or '';need(bool(a+b),'Empty mantissa')
 v=Fraction(int((a or '0')+b,16),16**len(b));ex=int(e or '0')
 v=v*(2**ex) if ex>=0 else v/Fraction(2**(-ex))
 return -v if sign=='-'else v
def canonical(a,b):
 if a is None or b is None or not a or not b:return None
 a,b=abs(a),abs(b);den=math.lcm(a.denominator,b.denominator)
 x=a.numerator*(den//a.denominator);y=b.numerator*(den//b.denominator)
 while x%2==0 and y%2==0:x//=2;y//=2
 return tuple(sorted((x,y)))
def main():
 family=q.read(HERE/'hypot-family.json');execution=q.read(HERE/'hypot-execution.json');rows=read_table(HERE/'hypot-certificates.json')
 need(len(rows)==16 and family['all_certificates_verified'] is True,'Wrong population')
 need(q.sha(HERE/'hypot-certificates.json')==family['certificates_sha256']==execution['certificates_sha256'],'Certificate hash')
 keys={}
 for j in range(8):
  k=73000000+5*j;u=2*k*k;v=2*k;x=(3*u-4*v)//5;y=(4*u+3*v)//5;z=u+1
  need(x*x+y*y==z*z-1 and z%2==1 and 4*z-2>2**55,'Exact identity/bound')
  for i,(a,b) in enumerate([(x,y),(y,x)],2*j):
   r=rows[i];need(int(r['x_bits'],16)-(0x3ff<<52)+2**52==a and int(r['y_bits'],16)-(0x3ff<<52)+2**52==b,'Wrong generated input')
   need(verify(r)['midpoint_relation']==-1,'Wrong midpoint side');keys[i]=canonical(Fraction(a,2**52),Fraction(b,2**52))
 corpus=HERE/'../../.work/bivariate/20261108-hypot-below/hypot.wc'
 if corpus.exists():data=corpus.read_bytes()
 else:
  api=q.read(ROOT/'config/source.json')['project_api'];path=family['corpus']['path'];meta=json.loads(q.get(api+'/repository/files/'+urllib.parse.quote(path,safe='')+'?ref='+family['pin']));data=base64.b64decode(meta['content'])
 need(hashlib.sha256(data).hexdigest()==family['corpus']['sha256'],'Corpus bytes')
 membership={i:[]for i in range(16)};count=0;finite=0;nonhex_finite=0
 for line,text in enumerate(data.decode('utf-8').splitlines(),1):
  text=text.split('#',1)[0].strip()
  if not text:continue
  fields=text.split(',');need(len(fields)==2,'Bad corpus row');a,b=map(exact,fields);count+=1;k=canonical(a,b)
  nonhex_finite+=sum('0x'not in s.lower() and v is not None for s,v in zip(fields,(a,b)))
  if k is None:continue
  finite+=1
  for i,v in keys.items():
   if k==v:membership[i].append(line)
 need(count==family['corpus']['rows'] and finite==family['corpus']['finite_nonzero'],'Corpus count')
 need(len(family['membership'])==16,'Missing membership row')
 for i,row in enumerate(family['membership']):need(row['record']==i and row['absolute_swap_power2_lines']==membership[i],'Independent membership discrepancy')
 need(not any(membership.values()),'A proposed family pair is already present')
 need(q.sha(HERE/'hypot_family.py')==family['generator_sha256'] and q.sha(ROOT/'hypot_verify.py')==family['verifier_sha256'],'Family tool identity')
 wc=HERE/'hypot-below.wc'
 supplied=[line.split('#',1)[0].strip() for line in wc.read_text(encoding='utf-8').splitlines()]
 supplied=[line for line in supplied if line];need(len(supplied)==16,'Pickup row count')
 for i,text in enumerate(supplied):
  fields=text.split(',');need(len(fields)==2,'Pickup syntax');a,b=map(exact,fields)
  r=rows[i];expected=[Fraction(int(r[k],16)-(0x3ff<<52)+2**52,2**52)for k in ('x_bits','y_bits')]
  need([a,b]==expected,'Pickup row differs from certificate')
 need(execution['status']=='PASS' and execution['pin']==family['pin'],'Execution status/pin')
 need([c['profile']for c in execution['profiles']]==['gcc-linux-x86_64','clang-linux-x86_64'],'Profiles')
 for p,h in execution['files'].items():need(q.sha(ROOT/p)==h,'Executed tool changed: '+p)
 for cell in execution['profiles']:
  need(cell['doctor']['status']=='PASS' and cell['status']=='PASS','Qualification')
  obs=cell['observations'];need(len(obs)==64 and {(v['record'],v['mode'])for v in obs}=={(i,m)for i in range(16)for m in MODES},'Observation population')
  for v in obs:
   r=rows[v['record']];need(v['status']=='PASS' and classify(v['observation'],r,v['mode'])=='PASS' and classify(v['oracle'],r,v['mode'],True)=='PASS','Observation mismatch')
  need([(v['fault'],v['expected'],v['observed'])for v in cell['controls']]==[(i,s,s)for i,s in enumerate(['VALUE','MODE','INPUT','FLAGS','ERRNO','TIMEOUT'],1)],'Controls')
 print(json.dumps({'status':'PASS','binary64_observations':128,'four_mode_oracle_checks':128,'correctly_rejected_faults':12,'exact_membership_rows':count,'ordered_input_matches':sum(bool(v) for v in membership.values()),'pickup_rows_verified':16},indent=2))
if __name__=='__main__':main()
