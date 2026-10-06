#!/usr/bin/env python3
"""Reproduce a proposed coverage-only .wc addition in disposable copies."""
from pathlib import Path
import difflib
import json
import resource
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import quality as q

PIN = 'e78b460c41e5e155f45a5ff824140b81c84f55cc'
ROW = '0x1.8p+0\n'

def main():
    start = time.monotonic()
    with q.locked():
        env = q.doctor('gcc-linux-x86_64')
        source = q.fetch(PIN,['asinpi'])
        wd = q.WORK/'candidates/asinpi-domain-witness'
        changed = wd/'source'
        for folder in ['support','asinpi']:
            for f in (source/'src/binary64'/folder).iterdir():
                if f.is_file():
                    dest = changed/'src/binary64'/folder/f.name
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(f,dest)
        wc = changed/'src/binary64/asinpi/asinpi.wc'
        old = wc.read_text()
        assert old.endswith('\n')
        values = []
        for line in old.splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            try: values.append(float.fromhex(line.strip()) if '0x' in line.lower() else float(line.strip()))
            except ValueError: pass  # special NaN spellings are handled upstream
        assert not any(abs(x)==1.5 for x in values), 'Witness already present; review candidate status'
        wc.write_text(old+ROW)
        q.save(changed/'manifest.json', {'files':{p.relative_to(changed).as_posix():q.sha(p) for p in changed.rglob('*') if p.is_file() and p.name!='manifest.json'}})
        patch = ''.join(difflib.unified_diff(old.splitlines(True),(old+ROW).splitlines(True),
                     fromfile='a/src/binary64/asinpi/asinpi.wc',tofile='b/src/binary64/asinpi/asinpi.wc'))
        (wd/'asinpi.wc.patch').write_text(patch)
        results = {}
        for name,src in [('before',source),('after',changed)]:
            results[name] = q.run_one(src,'asinpi','gcc-linux-x86_64',1,wd/name,env,time.monotonic()+300)
            assert results[name]['status']=='PASS', name+' did not pass'
        before,after = results['before'],results['after']
        assert before['coverage_union']['missing_arcs']==[['cr_asinpi',517,3]]
        assert after['coverage_union']['missing_lines']==[] and after['coverage_union']['missing_arcs']==[]
        assert after['corpus_rows']==before['corpus_rows']+1
        assert after['expected_tests_per_mode']==before['expected_tests_per_mode']+2
        u=resource.getrusage(resource.RUSAGE_CHILDREN)
        q.save(wd/'checks.json',{'status':'PASS','pin':PIN,'witness':ROW.strip(),
            'scope':'Coverage-only corpus candidate; no implementation defect or upstream acceptance claimed',
            'runner_sha256':q.RUNNER_HASH,'reproduce_sha256':q.sha(Path(__file__)),
            'results':results,'child_cpu_seconds':u.ru_utime+u.ru_stime,'wall_seconds':time.monotonic()-start})
        print('asinpi: original corpus passes; one added row closes the measured branch gap in all-mode union')

if __name__=='__main__':
    main()
