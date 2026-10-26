"""Bounded old/new fix checks. Invoke under the runbook's outer timeout."""
from pathlib import Path
import sys, shutil, resource, math, time

W = Path(__file__).resolve().parent
Q = W.parents[1]
sys.path.insert(0, str(Q))
import quality as q

OLD = 'dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3'
NEW = '0ce0cbc15935e24c656280e5a46c34e89f301b7a'
OUT = Q / '.work/candidates/20261025-public-fix-replay'

def main():
    # A new directory avoids silent reuse of a different driver or environment.
    OUT.mkdir(parents=True, exist_ok=False)
    start = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    deadline = started + 600
    records = []
    with q.locked():
        for pin in [OLD, NEW]:
            q.fetch(pin, ['exp', 'rsqrt'])
        environments = {name: q.doctor(name) for name in ['gcc-linux-x86_64', 'clang-linux-x86_64']}
        for profile, environment in environments.items():
            for fn in ['rsqrt', 'exp']:
                for era, pin in [('before', OLD), ('after', NEW)]:
                    name = profile + '-' + fn + '-' + era
                    wd = OUT / name
                    wd.mkdir()
                    source = Q / '.work/sources' / pin / 'src/binary64'
                    inputs = {}
                    for folder in [source / 'support', source / fn]:
                        for p in folder.iterdir():
                            if p.is_file() and p.suffix != '.wc':
                                shutil.copyfile(p, wd / p.name)
                                inputs[p.relative_to(source).as_posix()] = q.sha(p)
                    flags = q.flags(q.profile(profile), 1)
                    checks = []
                    def run(label, args, corpus=None):
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError('Overall science budget exhausted')
                        print(name, label, flush=True)
                        with open(corpus, 'rb') if corpus else q.contextlib.nullcontext(None) as inp:
                            d = q.command(args, cwd=wd, stdin=inp, timeout=min(120, remaining))
                        checks.append({'label': label, 'command': args, **d})
                        return d
                    d = run('build', [q.profile(profile)['cc'], *flags, '-I.', 'check_worst_uni.c', fn+'.c', fn+'_mpfr.c', '-lmpfr', '-lgmp', '-lm', '-o', 'check'])
                    assert d['returncode'] == 0
                    witness = '0x1.0000000000001p+1022' if fn == 'rsqrt' else '0x1.5a3a157335f3bp+9'
                    (wd/'witness.wc').write_text(witness+'\n')
                    corpora = [wd/'witness.wc']
                    if era == 'after':
                        vals = {float.fromhex(witness)}
                        for direction in [-math.inf, math.inf]:
                            x = float.fromhex(witness)
                            for _ in range(256):
                                x = math.nextafter(x, direction); vals.add(x)
                        assert len(vals) == 513
                        (wd/'neighbors.wc').write_text(''.join(x.hex()+'\n' for x in sorted(vals)))
                        corpora.extend([source/fn/(fn+'.wc'), wd/'neighbors.wc'])
                    for corpus in corpora:
                        rows, expected = q.expected_rows(corpus, wd/'function_under_test.h')
                        for mode in q.MODES:
                            d = run(corpus.stem+'-'+mode, ['./check', '--'+mode], corpus)
                            checks[-1].update(mode=mode, rows=rows, expected_tests=expected, corpus_sha256=q.sha(corpus))
                            if era == 'after' or (fn == 'exp' and mode != 'rndz'):
                                q.check_output(d, expected)
                            elif fn == 'exp':
                                assert d['returncode'] != 0 and '0x1.ffdebdc4e28acp+998' in d['output'] and '0x1.ffdebdc4e28abp+998' in d['output']
                            else:
                                assert d['returncode'] != 0 and 'Spurious underflow exception' in d['output']
                    if fn == 'rsqrt':
                        shutil.copyfile(W/'rsqrt_probe.c', wd/'probe.c')
                        d = run('probe-build', [q.profile(profile)['cc'], *flags, 'rsqrt.c', 'probe.c', '-lmpfr', '-lgmp', '-lm', '-o', 'probe'])
                        assert d['returncode'] == 0
                        d = run('flags-probe', ['./probe'])
                        assert d['returncode'] == (0 if era == 'after' else 1)
                        if era == 'after':
                            assert 'SUMMARY cases=32 failures=0' in d['output']
                        else:
                            assert all(any('mode='+m+' ' in line and 'x=0x1.0000000000001p+1022 ' in line and 'underflow=1' in line and 'bad=1' in line for line in d['output'].splitlines()) for m in q.MODES)
                    record = {'profile': profile, 'environment': environment, 'function': fn, 'era': era, 'pin': pin, 'source_sha256': q.sha(wd/(fn+'.c')), 'inputs_sha256': inputs, 'binary_sha256': q.sha(wd/'check'), 'probe_source_sha256': q.sha(W/'rsqrt_probe.c') if fn=='rsqrt' else None, 'flags': flags, 'checks': checks, 'status': 'PASS' if era=='after' else 'EXPECTED_OLD_FAILURES_REPRODUCED', 'runner_sha256': q.sha(Path(__file__)), 'quality_sha256': q.sha(Q/'quality.py'), 'completed_utc': q.utc()}
                    q.save(wd/'receipt.json', record)
                    records.append(record)
                    end = resource.getrusage(resource.RUSAGE_CHILDREN)
                    q.save(OUT/'replay.json', {'results': records, 'child_cpu_seconds': end.ru_utime+end.ru_stime-start.ru_utime-start.ru_stime, 'wall_seconds': time.monotonic()-started, 'complete': len(records)==8})
    print('DONE: all eight old/new cells verified', flush=True)

if __name__ == '__main__':
    main()
