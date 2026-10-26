"""Bounded Linux qualification of the restricted hypot certificate adapter."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import resource
import shutil
import time
import urllib.parse
import quality as q
from hypot_verify import loads, read_table, verify, MODES

ROOT=Path(__file__).resolve().parent
FILES=['hypot_run.py','hypot_verify.py','bivariate/hypot_probe.c',
       'bivariate/make_fixtures.py','bivariate/hypot-fixtures.json','quality.py','config/targets.json']
OBS={'x_bits','y_bits','value','mode_index','mode_preserved','flags','errno','raw_flags'}


def classify(obs, row, mode, oracle=False):
    if not isinstance(obs,dict) or set(obs)!=OBS|({'bound_lo','bound_hi'} if oracle else set()):
        return 'SCHEMA'
    if obs['x_bits']!=row['x_bits'] or obs['y_bits']!=row['y_bits']:return 'INPUT'
    if type(obs['mode_index']) is not int or obs['mode_index']!=MODES.index(mode) or type(obs['mode_preserved']) is not int or obs['mode_preserved']!=1:return 'MODE'
    v=verify(row)
    if obs['value']!=v['expected_bits'][mode]:return 'VALUE'
    if obs['flags']!=v['expected_flags'] or not isinstance(obs['flags'],dict) or any(type(x) is not int for x in obs['flags'].values()):return 'FLAGS'
    if type(obs['errno']) is not int or obs['errno']!=0:return 'ERRNO'
    if type(obs['raw_flags']) is not int or obs['raw_flags']<0:return 'SCHEMA'
    if oracle and (obs['bound_lo']!=v['expected_bits']['rndd'] or obs['bound_hi']!=v['expected_bits']['rndu']):return 'ORACLE_BOUND'
    return 'PASS'


def fetch_source(pin, wd):
    api=q.read(ROOT/'config/source.json')['project_api']
    tree=json.loads(q.get(api+'/repository/tree?'+urllib.parse.urlencode({'path':'src/binary64/hypot','ref':pin,'per_page':100})))
    entry=next(x for x in tree if x['path']=='src/binary64/hypot/hypot.c' and x['type']=='blob')
    data=q.get(api+'/repository/blobs/'+entry['id']+'/raw')
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=entry['id']:
        raise ValueError('Source Git blob mismatch')
    if '#include "' in data.decode():
        raise ValueError('Local source dependency requires explicit acquisition')
    (wd/'hypot.c').write_bytes(data)
    return {'path':entry['path'],'git_blob':entry['id'],'sha256':q.sha(wd/'hypot.c'),
            'errno_macro_referenced':'CORE_MATH_SUPPORT_ERRNO' in data.decode()}


def run(args):
    q.pin_value(args.pin)
    if not 1<=args.max_minutes<=30:raise ValueError('max-minutes must be 1..30')
    if not args.run_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in args.run_id):raise ValueError('Unsafe run id')
    if platform.system()!='Linux' or platform.machine()!='x86_64':raise ValueError('Only Linux x86_64 qualified here')
    wd=ROOT/'.work/bivariate'/args.run_id
    if wd.exists():raise ValueError('Run id already exists; preserve evidence and use a new id')
    wd.mkdir(parents=True)
    started=time.monotonic();cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);own0=time.process_time()
    deadline=started+60*args.max_minutes
    receipt={'schema_version':1,'kind':'restricted-hypot-qualification','status':'INCOMPLETE',
             'pin':args.pin,'started_utc':q.utc(),'scope':'Listed positive-normal fixtures only; no search, full corpus, imported certificates or completeness census.',
             'limits':{'wall_minutes':args.max_minutes,'child_seconds':60,'max_records':4096},
             'files':{p:q.sha(ROOT/p) for p in FILES},'source':{},'profiles':[],
             'fixture_count':0,'cost':{},'failure':None}
    def save():q.save(wd/'qualification.json',receipt)
    def command(a, timeout=60):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise RuntimeError('Overall deadline')
        return q.command(a,cwd=wd,timeout=min(timeout,remaining))
    def checked(a):
        r=command(a)
        if r['returncode'] or r['output_truncated']:raise RuntimeError('Child failed: '+r['output'][-1000:])
        return r
    save()
    try:
        with q.locked():
            rows=read_table(ROOT/'bivariate/hypot-fixtures.json');receipt['fixture_count']=len(rows)
            receipt['source']=fetch_source(args.pin,wd);save()
            for name in ['gcc-linux-x86_64','clang-linux-x86_64']:
                print('Qualifying',name,flush=True)
                env=q.doctor(name);p=q.profile(name)
                base=q.flags(p,True)+['-fno-lto']
                adapter=base+(['-ffp-exception-behavior=strict'] if p['cc'].startswith('clang') else [])
                cell={'profile':name,'doctor':env,'compiler_sha256':q.sha(Path(shutil.which(p['cc'])).resolve()),
                      'library_flags':base,'adapter_flags':adapter,'binaries':{},'observations':[],
                      'controls':[],'parser_controls':[],'symbol_check':None}
                receipt['profiles'].append(cell);save()
                checked([p['cc'],*base,'-c','hypot.c','-o','hypot.o'])
                sym=checked(['nm','--defined-only','hypot.o'])['output']
                if not any(line.endswith(' T cr_hypot') for line in sym.splitlines()):raise ValueError('Missing local cr_hypot definition')
                cell['symbol_check']='local hypot.o defines cr_hypot'
                probe=ROOT/'bivariate/hypot_probe.c'
                def build(label, extra, library=True):
                    checked([p['cc'],*adapter,*extra,str(probe),*(['hypot.o'] if library else []),'-lmpfr','-lgmp','-lm','-o',label])
                    cell['binaries'][label]=q.sha(wd/label)
                build('normal',[]);build('oracle',['-DORACLE'],False)
                libs=checked(['ldd','oracle'])['output']
                cell['oracle_libraries']={}
                for line in libs.splitlines():
                    if ('libmpfr.so' in line or 'libgmp.so' in line) and '=>' in line:
                        lib=Path(line.split('=>')[1].strip().split()[0]);cell['oracle_libraries'][lib.name]=q.sha(lib.resolve())
                if len(cell['oracle_libraries'])!=2:raise ValueError('MPFR/GMP library identity missing')
                # Oracle agreement gates every CORE-MATH execution.
                for i,row in enumerate(rows):
                    for mode in MODES:
                        a=[row['x_bits'],row['y_bits'],mode]
                        oracle=loads(checked(['./oracle',*a])['output'])
                        if classify(oracle,row,mode,True)!='PASS':raise ValueError('Independent MPFR disagreement')
                        obs=loads(checked(['./normal',*a])['output'])
                        code=classify(obs,row,mode)
                        cell['observations'].append({'record':i,'mode':mode,'observation':obs,'oracle':oracle,'status':code})
                        if code!='PASS':raise ValueError('Qualification observation '+code+'; not automatically a library defect')
                    if i%4==0:print(name,'fixture',i+1,'of',len(rows),flush=True);save()
                for fault,code in [(1,'VALUE'),(2,'MODE'),(3,'INPUT'),(4,'FLAGS'),(5,'ERRNO'),(6,'TIMEOUT')]:
                    label='control'+str(fault);build(label,['-DFAULT='+str(fault)])
                    row=rows[0];mode='rndu'
                    try:
                        out=command(['./'+label,row['x_bits'],row['y_bits'],mode],timeout=0.2 if fault==6 else 10)
                        actual=classify(loads(out['output']),row,mode) if out['returncode']==0 else 'PROCESS'
                    except RuntimeError as e:
                        if str(e).startswith('TIMEOUT:'):actual='TIMEOUT'
                        else:raise
                    cell['controls'].append({'fault':fault,'expected':code,'observed':actual})
                    if actual!=code:raise ValueError('Wrong control rejection: '+actual)
                for bad in ['3FF0000000000000','0x3ff0000000000000',' 3ff0000000000000','bff0000000000000','7ff0000000000000','0000000000000001']:
                    out=command(['./normal',bad,rows[0]['y_bits'],'rndn'])
                    cell['parser_controls'].append({'input':bad,'exit':out['returncode']})
                    if out['returncode']!=2:raise ValueError('Parser control not rejected')
                cell['status']='PASS';save()
            if any(q.sha(ROOT/p)!=h for p,h in receipt['files'].items()):raise ValueError('Tool/input changed during qualification')
            receipt['status']='PASS'
    except BaseException as e:
        receipt['failure']=q.clean(str(e));raise
    finally:
        c=resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt['cost']={'child_cpu_seconds':c.ru_utime+c.ru_stime-cpu0.ru_utime-cpu0.ru_stime,
                         'parent_cpu_seconds':time.process_time()-own0,'wall_seconds':time.monotonic()-started}
        save()
    print('PASS:',wd.relative_to(ROOT)/'qualification.json',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pin',required=True);p.add_argument('--run-id',required=True);p.add_argument('--max-minutes',type=int,default=20)
    run(p.parse_args())
