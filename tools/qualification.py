#!/usr/bin/env python3
"""Positive and deliberately broken integration controls; no upstream finding."""
import json
from pathlib import Path
import resource
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import quality as q


def main():
    started = time.monotonic()
    with q.locked():
        env = q.doctor('gcc-linux-x86_64')
        pin = q.read(q.ROOT/'config/source.json')['default_pin']
        source = q.fetch(pin, ['rsqrt'])
        root = q.WORK/'qualification'
        root.mkdir(parents=True,exist_ok=True)
        outcomes = []
        for kind in ['positive','wrong-value','wrong-inexact','wrong-errno']:
            copy = root/kind/'source'
            for folder in ['support','rsqrt']:
                for file in (source/'src/binary64'/folder).iterdir():
                    if file.is_file():
                        dest = copy/'src/binary64'/folder/file.name
                        dest.parent.mkdir(parents=True,exist_ok=True)
                        shutil.copyfile(file,dest)
            wc = copy/'src/binary64/rsqrt/rsqrt.wc'
            wc.write_text('0x1p0\n0x1p2\n0x1p4\n')
            if kind != 'positive':
                file = copy/'src/binary64/rsqrt/rsqrt.c'
                text = file.read_text()
                needle = 'double cr_rsqrt(double x){'
                if text.count(needle) != 1:
                    raise RuntimeError('Control mutation needs review against changed upstream syntax')
                mutation = {'wrong-value':'return 0.0;',
                            'wrong-inexact':'feraiseexcept(FE_INEXACT); return 0.5;',
                            'wrong-errno':'errno = ERANGE; return 0.5;'}[kind]
                file.write_text('#include <fenv.h>\n#include <errno.h>\n'+text.replace(needle,needle+'\n  if (x == 4.0) { '+mutation+' } /* INTENTIONAL TEST MUTATION */\n'))
            manifest = {f.relative_to(copy).as_posix():q.sha(f) for f in copy.rglob('*') if f.is_file() and f.name != 'manifest.json'}
            q.save(copy/'manifest.json',{'files':manifest})
            result = q.run_one(copy,'rsqrt','gcc-linux-x86_64',1,root/kind/'runs',env,time.monotonic()+180)
            expected = 'PASS' if kind == 'positive' else 'FAIL'
            if result['status'] != expected or len(result['modes']) != 4:
                raise RuntimeError('Qualification control did not produce expected '+expected)
            if any(mode['plain'] != expected for mode in result['modes']):
                raise RuntimeError('Every ordinary checker mode must produce '+expected)
            if kind == 'positive' and any(mode.get('covered') != 'PASS' for mode in result['modes']):
                raise RuntimeError('Positive instrumented control must pass every mode')
            outcomes.append({'control':kind,'expected_status':expected,'result':result})
        u=resource.getrusage(resource.RUSAGE_CHILDREN)
        result={'status':'PASS','scope':'Synthetic controls: negative cases test the ordinary checker only; positive case includes coverage. Not upstream defects or full-corpus results',
                'tool_sha256':q.sha(Path(__file__)),
                'upstream_base':pin,'controls':outcomes,'child_cpu_seconds':u.ru_utime+u.ru_stime,
                'wall_seconds':time.monotonic()-started}
        q.save(root/'result.json',result)
        print('Positive, wrong-value, wrong-inexact and wrong-errno controls behaved correctly in all four modes')


if __name__=='__main__':
    main()
