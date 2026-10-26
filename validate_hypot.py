"""Strict publication checks for restricted hypot qualification receipts."""
import hashlib
import math
from pathlib import Path
import re
from hypot_verify import loads, read_table, verify, MODES

TOP={'schema_version','kind','status','pin','started_utc','scope','limits','files','source','profiles','fixture_count','cost','failure'}
CELL={'profile','doctor','compiler_sha256','library_flags','adapter_flags','binaries','observations','controls','parser_controls','symbol_check','oracle_libraries','status'}
TOOLS={'hypot_run.py','hypot_verify.py','bivariate/hypot_probe.c','bivariate/make_fixtures.py','bivariate/hypot-fixtures.json','quality.py','config/targets.json'}
FLAGS={'inexact','invalid','divbyzero','underflow','overflow'}


def exact(d, keys):
    if not isinstance(d,dict) or set(d)!=keys:raise ValueError('Hypot receipt missing/unknown fields')


def require(condition, message):
    if not condition:raise ValueError('Hypot receipt: '+message)


def digest(value):
    require(isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None,'bad digest')


def validate(folder):
    d=loads((folder/'qualification.json').read_text(encoding='utf-8'));exact(d,TOP)
    require(type(d['schema_version']) is int and d['schema_version']==1,'schema')
    require(d['kind']=='restricted-hypot-qualification' and d['status']=='PASS' and d['failure'] is None,'incomplete')
    require(d['scope']=='Listed positive-normal fixtures only; no search, full corpus, imported certificates or completeness census.','scope')
    require(isinstance(d['started_utc'],str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|\+00:00)',d['started_utc']) is not None,'timestamp')
    require(isinstance(d['pin'],str) and re.fullmatch('[0-9a-f]{40}',d['pin']) is not None,'pin')
    exact(d['files'],TOOLS)
    for rel,h in d['files'].items():
        digest(h);require(hashlib.sha256((folder/'tools'/rel).read_bytes()).hexdigest()==h,'tool hash')
    rows=read_table(folder/'tools/bivariate/hypot-fixtures.json')
    require(type(d['fixture_count']) is int and d['fixture_count']==len(rows),'fixture count')
    exact(d['limits'],{'wall_minutes','child_seconds','max_records'})
    require(type(d['limits']['wall_minutes']) is int and 1<=d['limits']['wall_minutes']<=30,'wall limit')
    require(d['limits']['child_seconds']==60 and d['limits']['max_records']==4096,'limits')
    exact(d['cost'],{'child_cpu_seconds','parent_cpu_seconds','wall_seconds'})
    require(all(type(v) in (float,int) and math.isfinite(v) and v>=0 for v in d['cost'].values()),'cost')
    require(d['cost']['wall_seconds']<=60*d['limits']['wall_minutes'],'exceeded wall limit')
    exact(d['source'],{'path','git_blob','sha256','errno_macro_referenced'})
    require(d['source']['path']=='src/binary64/hypot/hypot.c' and d['source']['errno_macro_referenced'] is True,'source identity')
    require(re.fullmatch('[0-9a-f]{40}',d['source']['git_blob']) is not None,'blob')
    digest(d['source']['sha256'])
    require(isinstance(d['profiles'],list) and [c['profile'] for c in d['profiles']]==['gcc-linux-x86_64','clang-linux-x86_64'],'profiles')
    for cell in d['profiles']:
        exact(cell,CELL);require(cell['status']=='PASS','profile status');digest(cell['compiler_sha256'])
        doc=cell['doctor'];exact(doc,{'profile','compiler','platform','architecture','libc','probe','status','experimental'}|({'gcov'} if cell['profile'].startswith('gcc') else set()))
        require(doc['status']=='PASS' and doc['profile']==cell['profile'] and doc['platform']=='Linux' and doc['architecture']=='x86_64' and doc['experimental'] is False,'doctor')
        require(all(isinstance(doc[k],str) and doc[k] for k in ['compiler','probe']),'doctor text')
        require(isinstance(doc['libc'],list) and len(doc['libc'])==2 and all(isinstance(x,str) and x for x in doc['libc']) and doc['libc'][0]=='glibc','libc')
        for flags in [cell['library_flags'],cell['adapter_flags']]:
            require(isinstance(flags,list) and all(type(x) is str for x in flags),'flags type')
            require({'-frounding-math','-march=x86-64','-ffp-contract=off','-fno-lto','-DCORE_MATH_SUPPORT_ERRNO'}<=set(flags),'build flags')
            require(not any(x in flags for x in ['-ffast-math','-flto','-march=native']),'unsafe flags')
        require(cell['symbol_check']=='local hypot.o defines cr_hypot','symbol')
        exact(cell['binaries'],{'normal','oracle'}|{'control'+str(i) for i in range(1,7)})
        for h in cell['binaries'].values():digest(h)
        require(len(cell['oracle_libraries'])==2 and all(re.fullmatch(r'lib(?:mpfr|gmp)\.so\.[0-9.]+',k) for k in cell['oracle_libraries']),'oracle libraries')
        require({k.split('.so.')[0] for k in cell['oracle_libraries']}=={'libmpfr','libgmp'},'both oracle libraries')
        for h in cell['oracle_libraries'].values():digest(h)
        require(len(cell['observations'])==len(rows)*4,'observations count')
        for observation,(i,mode) in zip(cell['observations'],[(i,m) for i in range(len(rows)) for m in MODES]):
            exact(observation,{'record','mode','observation','oracle','status'})
            require(type(observation['record']) is int and observation['record']==i and observation['mode']==mode and observation['status']=='PASS','observation index/status')
            v=verify(rows[i])
            for key in ['observation','oracle']:
                obs=observation[key];exact(obs,{'x_bits','y_bits','value','mode_index','mode_preserved','flags','errno','raw_flags'}|({'bound_lo','bound_hi'} if key=='oracle' else set()))
                require(obs['x_bits']==rows[i]['x_bits'] and obs['y_bits']==rows[i]['y_bits'],'exact inputs')
                require(obs['value']==v['expected_bits'][mode],'value')
                require(type(obs['mode_index']) is int and obs['mode_index']==MODES.index(mode) and type(obs['mode_preserved']) is int and obs['mode_preserved']==1,'mode')
                exact(obs['flags'],FLAGS);require(all(type(x) is int for x in obs['flags'].values()) and obs['flags']==v['expected_flags'],'flags')
                require(type(obs['errno']) is int and obs['errno']==0,'errno')
                require(type(obs['raw_flags']) is int and obs['raw_flags']>=0,'raw flags')
                # This receipt schema is restricted to the recorded x86 glibc ABI.
                require(obs['raw_flags']==0x20*obs['flags']['inexact'],'raw/decoded flags disagree')
                if key=='oracle':require(obs['bound_lo']==v['expected_bits']['rndd'] and obs['bound_hi']==v['expected_bits']['rndu'],'MPFR interval')
        codes=['VALUE','MODE','INPUT','FLAGS','ERRNO','TIMEOUT']
        require(len(cell['controls'])==6,'controls count')
        for i,(c,code) in enumerate(zip(cell['controls'],codes),1):
            exact(c,{'fault','expected','observed'});require(type(c['fault']) is int and c=={'fault':i,'expected':code,'observed':code},'control rejection')
        expected=['3FF0000000000000','0x3ff0000000000000',' 3ff0000000000000','bff0000000000000','7ff0000000000000','0000000000000001']
        require(cell['parser_controls']==[{'input':s,'exit':2} for s in expected],'parser controls')
    manifest=loads((folder/'SHA256SUMS.json').read_text(encoding='utf-8'))
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json'}
    require(set(manifest)==actual,'manifest population')
    for rel,h in manifest.items():
        digest(h);p=(folder/rel).resolve();require(p.is_relative_to(folder.resolve()),'unsafe manifest path')
        require(hashlib.sha256(p.read_bytes()).hexdigest()==h,'manifest hash')
    return d
