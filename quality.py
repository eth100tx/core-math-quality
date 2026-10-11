#!/usr/bin/env python3
"""Bounded, reproducible CORE-MATH checks. Python standard library only."""
import argparse
import contextlib
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
WORK = ROOT / '.work'
MODES = ('rndn', 'rndz', 'rndu', 'rndd')
BASE_FLAGS = ['-O3', '-frounding-math', '-fno-finite-math-only',
              '-ffp-contract=off', '-DCORE_MATH_NO_OPENMP', '-DCORE_MATH_CHECK_INEXACT']
RUNNER_HASH = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
ACTIVE_RUN = None


class RunInterrupted(Exception):
    pass


def stop_run(signum, frame):
    raise RunInterrupted('INTERRUPTED by signal ' + str(signum))


def read(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def clean(text):
    # Stable published paths, no host identity/environment dump.
    for value, replacement in [(str(ROOT), '<workspace>'), (str(Path.home()), '<home>')]:
        text = text.replace(value, replacement)
    return text


def command(args, cwd=None, stdin=None, timeout=300):
    started = time.monotonic()
    def limits():
        import resource
        resource.setrlimit(resource.RLIMIT_FSIZE, (256 * 1024 * 1024, 256 * 1024 * 1024))
        # The spawn guard belongs to the parent; preserve the caller's child mask.
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    # Block termination around spawn so no detached child escapes the handler.
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGINT})
    with tempfile.TemporaryFile() as output:
        try:
            proc = subprocess.Popen([str(a) for a in args], cwd=cwd, stdin=stdin,
                              stdout=output, stderr=subprocess.STDOUT,
                              start_new_session=True, preexec_fn=limits)
        except BaseException:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
            raise
        with proc:
            def interrupted(signum, frame):
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGKILL)
                raise RunInterrupted('INTERRUPTED by signal ' + str(signum))
            old_handlers = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
            try:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                raise RuntimeError('TIMEOUT: ' + clean(' '.join(map(str, args))))
            finally:
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                for s, handler in old_handlers.items():
                    signal.signal(s, handler)
            size = output.tell()
            output.seek(0)
            out = output.read(65536)
            if size > 131072:
                output.seek(-65536, 2)
                out += b'\n[OUTPUT TRUNCATED]\n' + output.read()
            elif size > 65536:
                out += output.read()
    return {'returncode': proc.returncode, 'output': clean(out.decode(errors='replace')),
            'output_bytes': size, 'output_truncated': size > 131072,
            'wall_seconds': round(time.monotonic() - started, 3)}


def checked(args, **kwargs):
    r = command(args, **kwargs)
    if r['returncode']:
        raise RuntimeError(r['output'][-5000:])
    return r


@contextlib.contextmanager
def locked(lock_path=None):
    import fcntl
    # Shared among independent clones on this host; released on process exit.
    path = Path(lock_path) if lock_path else Path.home() / '.local/state/core-math-quality.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another core-math-quality run is active on this host')
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def get(url):
    start = time.monotonic()
    with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept-Encoding': 'gzip'}), timeout=90) as r:
        chunks, size = [], 0
        while True:
            data = r.read(1024 * 1024)
            if not data:
                break
            size += len(data)
            if size > 256 * 1024 * 1024 or time.monotonic() - start > 600:
                raise RuntimeError('Download size/time limit exceeded')
            chunks.append(data)
            if size % (8 * 1024 * 1024) == 0:
                print('Downloaded', size // (1024 * 1024), 'MiB', flush=True)
        content = b''.join(chunks)
        if r.headers.get('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=io.BytesIO(content)) as compressed:
                content = compressed.read(256 * 1024 * 1024 + 1)
            if len(content) > 256 * 1024 * 1024:
                raise RuntimeError('Decompressed download too large')
        return content


def pin_value(value):
    if not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('Require an immutable, full 40-character commit SHA')
    return value


def targets(value):
    all_targets = read(ROOT / 'config/targets.json')
    chosen = all_targets if value == 'all' else value.split(',')
    if not chosen or len(set(chosen)) != len(chosen) or any(x not in all_targets for x in chosen):
        raise ValueError('Select unique names from config/targets.json, or all')
    return chosen


def fetch(pin, functions):
    api = read(ROOT / 'config/source.json')['project_api']
    source = WORK / 'sources' / pin
    source.mkdir(parents=True, exist_ok=True)
    record = source / 'manifest.json'
    manifest = read(record) if record.exists() else {'pin': pin, 'files': {}, 'archives': {}}
    manifest.setdefault('git_blobs', {})
    for folder in ['src/binary64/support'] + ['src/binary64/' + f for f in functions]:
        existing = {p: h for p, h in manifest['files'].items() if p.startswith(folder + '/')}
        # Bind each file to the pinned Git tree, including already cached downloads.
        tree, page = {}, 1
        while True:
            listing = json.loads(get(api + '/repository/tree?' + urllib.parse.urlencode(
                {'path': folder, 'ref': pin, 'recursive': 'true', 'per_page': 100, 'page': page})))
            for item in listing:
                if item['type'] == 'blob':
                    tree[item['path']] = item['id']
            if len(listing) < 100:
                break
            page += 1
        def valid_file(path):
            content = (source / path).read_bytes()
            return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == tree[path]
        if existing and set(existing) == set(tree) and all((source / p).is_file() and sha(source / p) == h and valid_file(p) for p, h in existing.items()):
            manifest['git_blobs'].update(tree)
            save(record, manifest)
            print('Verified cached source', folder, flush=True)
            continue
        if not tree:
            raise RuntimeError('Empty pinned source tree: ' + folder)
        # Per-blob retrieval avoids slow server-side archive generation for large corpora.
        for rel, blob_id in tree.items():
            dest = source / rel
            if not rel.startswith(folder + '/') or '..' in PurePosixPath(rel).parts or not dest.resolve().is_relative_to(source.resolve()):
                raise ValueError('Unsafe source tree path')
            if not dest.is_file() or not valid_file(rel):
                print('Fetch pinned file', rel, flush=True)
                content = get(api + '/repository/blobs/' + blob_id + '/raw')
                if hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() != blob_id:
                    raise RuntimeError('Downloaded Git blob mismatch: ' + rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
            manifest['files'][rel] = sha(dest)
        if not all((source / path).is_file() and valid_file(path) for path in tree):
            raise RuntimeError('Downloaded source does not match pinned Git tree')
        for old in list(manifest['files']):
            if old.startswith(folder + '/') and old not in tree:
                del manifest['files'][old]
                manifest['git_blobs'].pop(old, None)
        manifest['git_blobs'].update(tree)
        save(record, manifest)
    return source


def profile(name):
    profiles = read(ROOT / 'config/profiles.json')
    if name not in profiles:
        raise ValueError('Unknown profile')
    p = profiles[name]
    if platform.system() != p['system'] or platform.machine() != p['machine']:
        raise RuntimeError('Profile platform mismatch: ' + name)
    return p


def flags(p, errno):
    return BASE_FLAGS + p['flags'] + (['-fsignaling-nans'] if p['coverage'] else []) + (
        ['-DCORE_MATH_SUPPORT_ERRNO'] if errno else [])


def doctor(name):
    p = profile(name)
    wd = WORK / 'doctor' / name
    wd.mkdir(parents=True, exist_ok=True)
    code = r'''
#include <stdio.h>
#include <float.h>
#include <fenv.h>
#include <math.h>
#include <mpfr.h>
int main(void) {
  if (sizeof(double)!=8 || DBL_MANT_DIG!=53 || FLT_RADIX!=2 || FLT_EVAL_METHOD!=0) return 1;
  volatile double a=1.0,b=0x1p-53,lo,hi;
  if (fesetround(FE_DOWNWARD)) return 2; lo=a+b;
  if (fesetround(FE_UPWARD)) return 3; hi=a+b;
  if (!(lo==1.0 && hi==0x1.0000000000001p0)) return 4;
  if (fesetround(FE_TONEAREST)) return 5;
  volatile double tiny=0x1p-1022,half=0.5; if(tiny*half != 0x1p-1023) return 6;
  volatile double fa=0x1.0000000000001p0,fb=0x1.fffffffffffffp-1,fc=-1.0;
  if (fma(fa,fb,fc) != 0x1.ffffffffffffep-54) return 7;
  mpfr_t x; mpfr_init2(x,128); mpfr_set_ui(x,1,MPFR_RNDN); mpfr_clear(x);
  printf("binary64 rounding/subnormal/fma PASS; MPFR %s; GMP %s\n",mpfr_get_version(),gmp_version);
  return 0;
}'''
    (wd / 'probe.c').write_text(code)
    compiler = checked([p['cc'], '--version'])['output'].splitlines()[0]
    if '-march=x86-64-v3' in p['flags']:
        (wd / 'isa.c').write_text('int main(void){__builtin_cpu_init();return !__builtin_cpu_supports("x86-64-v3");}')
        checked([p['cc'], 'isa.c', '-o', 'isa'], cwd=wd)
        checked(['./isa'], cwd=wd)
    checked([p['cc'], *flags(p, False), 'probe.c', '-lmpfr', '-lgmp', '-lm', '-o', 'probe'], cwd=wd)
    probe = checked(['./probe'], cwd=wd)['output'].strip()
    d = {'profile': name, 'compiler': compiler, 'platform': p['system'], 'architecture': p['machine'],
         'libc': list(platform.libc_ver()),
         'probe': probe, 'status': 'PASS', 'experimental': p.get('experimental', False)}
    if p['coverage']:
        gcov = checked([p['gcov'], '--version'])['output'].splitlines()[0]
        gcc_version = checked([p['cc'], '-dumpfullversion'])['output'].strip()
        if not re.search(r'\b' + re.escape(gcc_version) + r'\b', gcov):
            raise RuntimeError('GCC/gcov version mismatch')
        d['gcov'] = gcov
    save(wd / 'result.json', d)
    return d


def coverage_maps(sf):
    lines, arcs = {}, {}
    for line in sf['lines']:
        key = (line.get('function_name', ''), line['line_number'])
        if key in lines:
            raise ValueError('Duplicate gcov line identity')
        lines[key] = line['count']
        for n, branch in enumerate(line.get('branches', [])):
            arcs[key + (n,)] = branch['count']
    return lines, arcs


def coverage_summary(lines, arcs):
    return {'lines_total': len(lines), 'lines_hit': sum(v > 0 for v in lines.values()),
            'arcs_total': len(arcs), 'arcs_hit': sum(v > 0 for v in arcs.values()),
            'missing_lines': [list(k) for k, v in sorted(lines.items()) if v == 0],
            'missing_arcs': [list(k) for k, v in sorted(arcs.items()) if v == 0]}


def add_union(total, new):
    if total and total.keys() != new.keys():
        raise ValueError('Coverage denominator changed between modes')
    return {k: total.get(k, 0) + v for k, v in new.items()}


def expected_rows(wc, header):
    rows = sum(bool(l.strip()) and not l.startswith('#') for l in wc.read_text().splitlines())
    symmetric = bool(re.search(r'^\s*#\s*define\s+WORST_SYMMETRIC\b', header.read_text(), re.M))
    return rows, rows * (2 if symmetric else 1)


def check_output(result, expected):
    match = re.search(r'^(\d+) tests passed, (\d+) failure\(s\)$', result['output'], re.M)
    if result['returncode'] or not match or int(match[1]) != expected or int(match[2]) != 0:
        raise RuntimeError('Checker failed or accepted-row count mismatch: ' + result['output'][-3000:])


def failed_status(result):
    match = re.search(r'^(\d+) tests passed, (\d+) failure\(s\)$', result['output'], re.M)
    return 'FAIL' if result['returncode'] or (match and int(match[2]) > 0) else 'INCOMPLETE'


def run_one(source, fn, name, errno, runroot, environment, deadline):
    p = profile(name)
    key = f'{fn}-{name}-errno{errno}'
    wd = runroot / key
    if wd.exists():
        if wd.is_symlink() or not wd.resolve().is_relative_to(runroot.resolve()):
            raise RuntimeError('Unsafe cell directory')
        shutil.rmtree(wd)
    wd.mkdir(parents=True, exist_ok=True)
    src = source / 'src/binary64'
    manifest = read(source / 'manifest.json')['files']
    copied = {}
    for folder in [src / 'support', src / fn]:
        for file in folder.iterdir():
            rel = file.relative_to(source).as_posix()
            if file.is_file() and rel in manifest:
                if file.name in copied:
                    raise RuntimeError('Source flattening collision: ' + file.name)
                if sha(file) != manifest[rel]:
                    raise RuntimeError('Source changed after verification')
                shutil.copyfile(file, wd / file.name)
                copied[file.name] = manifest[rel]
    wc = wd / (fn + '.wc')
    rows, expected = expected_rows(wc, wd / 'function_under_test.h')
    if not rows:
        raise RuntimeError('Empty corpus')
    result = {'function': fn, 'profile': name, 'errno': errno, 'status': 'RUNNING',
              'started_utc': utc(), 'flags': flags(p, errno), 'environment': environment,
              'corpus_rows': rows, 'expected_tests_per_mode': expected,
              'source_sha256': sha(wd / (fn + '.c')), 'corpus_sha256': sha(wc),
              'checker_sha256': sha(wd / 'check_worst_uni.c'), 'modes': [], 'logs': {}, 'copied_files': copied,
              'coverage_flags': ['-O0', '-g'] + flags(p, errno)[1:] + ['--coverage'] if p['coverage'] else None}

    def invoke(label, args, input_path=None, allow_failure=False):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('Run wall-clock budget exhausted')
        save(runroot / 'status.json', {'state': 'RUNNING', 'current': key, 'operation': label,
                                     'heartbeat_utc': utc(), 'unit_timeout_seconds': min(600, remaining)})
        with input_path.open('rb') if input_path else contextlib.nullcontext(None) as inp:
            r = command(args, cwd=wd, stdin=inp, timeout=min(600, remaining))
        r['command'] = [clean(str(arg)) for arg in args]
        (wd / (label + '.log')).write_text(r['output'])
        result['logs'][label] = r
        if r['returncode'] and not allow_failure:
            raise RuntimeError(label + ' failed: ' + r['output'][-3000:])
        return r

    try:
        checker_text = (wd / 'check_worst_uni.c').read_text()
        result['macros_referenced'] = {name: name in checker_text for name in
                                      ['CORE_MATH_CHECK_INEXACT', 'CORE_MATH_SUPPORT_ERRNO', 'CORE_MATH_NO_OPENMP']}
        if not all(result['macros_referenced'].values()):
            raise RuntimeError('Upstream checker changed required macro support')
        common = [p['cc'], *flags(p, errno), '-I.']
        invoke('reference-build', [*common, '-c', fn + '_mpfr.c', '-o', 'ref.o'])
        invoke('plain-build', [*common, '-c', fn + '.c', '-o', 'plain.o'])
        invoke('checker-build', [*common, '-c', 'check_worst_uni.c', '-o', 'checker.o'])
        invoke('plain-link', [*common, 'checker.o', 'plain.o', 'ref.o', '-lmpfr', '-lgmp', '-lm', '-o', 'plain'])
        if p['coverage']:
            invoke('covered-build', [p['cc'], *result['coverage_flags'], '-I.', '-c', fn + '.c', '-o', fn + '.o'])
            invoke('covered-link', [*common, 'checker.o', fn + '.o', 'ref.o', '-lgcov', '-lmpfr', '-lgmp', '-lm', '-o', 'covered'])
        union_l, union_a = {}, {}
        for mode in MODES:
            print(key, mode, flush=True)
            plain = invoke('plain-' + mode, ['./plain', '--' + mode], wc, allow_failure=True)
            entry = {'mode': mode, 'plain': 'PASS', 'accepted_tests': expected}
            try:
                check_output(plain, expected)
            except RuntimeError as e:
                entry.update(plain=failed_status(plain), accepted_tests=None, error=str(e))
                result['modes'].append(entry)
                continue
            if p['coverage']:
                for counter in wd.glob('*.gcda'):
                    counter.unlink()
                covered = invoke('covered-' + mode, ['./covered', '--' + mode], wc, allow_failure=True)
                try:
                    check_output(covered, expected)
                except RuntimeError as e:
                    entry.update(covered=failed_status(covered), error=str(e))
                    result['modes'].append(entry)
                    continue
                if not (wd / (fn + '.gcda')).exists():
                    raise RuntimeError('Missing current-mode counters')
                (wd / (fn + '.gcov.json.gz')).unlink(missing_ok=True)
                invoke('gcov-' + mode, [p['gcov'], '-b', '-c', '-j', fn + '.gcno'])
                data = json.loads(gzip.decompress((wd / (fn + '.gcov.json.gz')).read_bytes()))
                matching = [f for f in data['files'] if Path(f['file']).name == fn + '.c']
                if len(matching) != 1:
                    raise RuntimeError('Cannot identify target source coverage')
                sf = matching[0]
                sf['file'] = 'src/binary64/' + fn + '/' + fn + '.c'
                # Publish exact target counts; absolute gcov cwd is deliberately omitted.
                save(wd / (mode + '-coverage.json'), sf)
                ls, ar = coverage_maps(sf)
                if not ls:
                    raise RuntimeError('No instrumented executable lines')
                union_l, union_a = add_union(union_l, ls), add_union(union_a, ar)
                entry.update(covered='PASS', coverage=coverage_summary(ls, ar))
                entry['gcov_json_format_version'] = data['format_version']
                entry['other_instrumented_files'] = sorted(Path(f['file']).name for f in data['files'] if f is not sf)
            result['modes'].append(entry)
        if p['coverage']:
            result['coverage_union'] = coverage_summary(union_l, union_a)
        result['status'] = ('FAIL' if any(m.get('plain') == 'FAIL' or m.get('covered') == 'FAIL' for m in result['modes'])
                            else 'INCOMPLETE' if any(m.get('plain') == 'INCOMPLETE' or m.get('covered') == 'INCOMPLETE' for m in result['modes'])
                            else 'PASS')
    except RunInterrupted:
        raise
    except Exception as e:
        result['status'] = 'INCOMPLETE'
        result['error'] = clean(str(e))
    result['finished_utc'] = utc()
    save(wd / 'result.json', result)
    return result


def ranking(results, functions):
    measured = [r for r in results if r['status'] == 'PASS' and 'coverage_union' in r]
    rows = []
    for r in measured:
        c = r['coverage_union']
        l, a = c['lines_total'] - c['lines_hit'], c['arcs_total'] - c['arcs_hit']
        if l + a:
            rows.append({'function': r['function'], 'missing_lines': l, 'missing_arcs': a})
    rows.sort(key=lambda r: (r['missing_lines'], r['missing_arcs'], r['function']))
    return {'population': functions, 'measured': len(measured), 'complete_population': len(measured) == len(functions),
            'policy': 'exclude zero/zero; ascending missing lines, then missing arcs, then name; zero-line branch gaps remain eligible',
            'candidates': rows, 'recommendation': rows[0] if rows and len(measured) == len(functions) and set(functions) == set(targets('all')) else None}


def execute(args):
    global ACTIVE_RUN
    import resource
    with locked():
        started = time.monotonic()
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        funcs = targets(args.functions)
        environment = doctor(args.profile)
        runroot = WORK / 'runs' / args.run_id
        # Preserve a previous completed run while validating reuse.
        if not (runroot / 'identity.json').exists():
            ACTIVE_RUN = runroot
            save(runroot / 'status.json', {'state': 'ACQUIRING', 'heartbeat_utc': utc()})
        source = fetch(args.pin, funcs)
        identity = {'pin': args.pin, 'profile': args.profile, 'errno': args.errno,
                    'functions': funcs, 'runner_sha256': RUNNER_HASH, 'environment': environment,
                    'resolved_profile': profile(args.profile),
                    'config_hashes': {p.name: sha(p) for p in (ROOT / 'config').glob('*.json')},
                    'source_manifest': {k: ({p: v for p, v in values.items() if any(p.startswith('src/binary64/' + fn + '/') or p == 'src/binary64/' + fn for fn in funcs + ['support'])} if isinstance(values, dict) else values) for k, values in read(source / 'manifest.json').items()}}
        stable_identity = {**identity, 'source_manifest': {k: v for k, v in identity['source_manifest'].items() if k != 'archives'}}
        digest = hashlib.sha256(json.dumps(stable_identity, sort_keys=True).encode()).hexdigest()
        if runroot.exists() and (runroot / 'identity.json').exists():
            if read(runroot / 'identity.json')['digest'] != digest:
                raise RuntimeError('Run ID already belongs to different inputs; use a new ID')
        ACTIVE_RUN = runroot
        save(runroot / 'identity.json', {'digest': digest, **identity})
        results = []
        deadline = started + args.max_minutes * 60
        for fn in funcs:
            save(runroot / 'status.json', {'state': 'RUNNING', 'current': fn, 'completed': len(results),
                                         'total': len(funcs), 'heartbeat_utc': utc()})
            previous = runroot / f'{fn}-{args.profile}-errno{args.errno}' / 'result.json'
            if previous.exists() and read(previous)['status'] == 'PASS':
                result = read(previous)
                print('Resume: completed', fn, flush=True)
            elif time.monotonic() >= deadline:
                result = {'function': fn, 'status': 'NOT_RUN', 'error': 'Run wall-clock budget exhausted'}
            else:
                result = run_one(source, fn, args.profile, args.errno, runroot, environment, deadline)
            results.append(result)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        result = {'schema_version': 1, 'run_id': args.run_id, 'created_utc': utc(),
                  'identity': identity, 'results': results, 'ranking': ranking(results, funcs),
                  'status': 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL' if any(r['status'] == 'FAIL' for r in results) else 'INCOMPLETE',
                  'this_invocation_child_cpu_seconds': cpu,
                  'wall_seconds': time.monotonic() - started,
                  'scope': 'upstream full .wc + unchanged checker built-in checks; four rounding modes; target .c coverage only; tested, not proven'}
        save(runroot / 'result.json', result)
        # Append-only invocation accounting, including resume overhead.
        with (runroot / 'invocations.jsonl').open('a') as log:
            log.write(json.dumps({'utc': utc(), 'child_cpu_seconds': cpu, 'wall_seconds': result['wall_seconds']}) + '\n')
        save(runroot / 'status.json', {'state': result['status'], 'completed': len(results), 'heartbeat_utc': utc()})
        ACTIVE_RUN = None
        print(json.dumps({'run_id': args.run_id, 'status': result['status'], 'ranking': result['ranking']}, indent=2))
        return 0 if result['status'] == 'PASS' else 1


def export(args):
    runroot = WORK / 'runs' / args.run_id
    result = read(runroot / 'result.json')
    if read(runroot / 'status.json')['state'] not in ('PASS', 'INCOMPLETE', 'FAIL'):
        raise RuntimeError('Run has no terminal state')
    from validate import receipt
    receipt(result)
    dest = ROOT / 'weekly' / args.week / 'runs' / args.run_id
    if dest.exists():
        raise RuntimeError('Export exists; do not silently overwrite published evidence')
    dest.mkdir(parents=True)
    save(dest / 'result.json', result)
    for cell in runroot.iterdir():
        if cell.is_dir() and (cell / 'result.json').exists() and read(cell / 'result.json')['status'] == 'PASS':
            for file in cell.glob('*-coverage.json'):
                target = dest / cell.name / file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, target)
    manifest = {p.relative_to(dest).as_posix(): sha(p) for p in dest.rglob('*') if p.is_file()}
    save(dest / 'SHA256SUMS.json', manifest)
    print('Exported evidence for review:', dest.relative_to(ROOT))


def plan(args):
    api = read(ROOT / 'config/source.json')['project_api']
    if args.pin == args.base:
        data = {'commits': [], 'diffs': []}
    else:
        data = json.loads(get(api + '/repository/compare?' + urllib.parse.urlencode(
            {'from': args.base, 'to': args.pin, 'straight': 'true'})))
    if data.get('compare_timeout') or data.get('overflow'):
        raise RuntimeError('Incomplete upstream comparison')
    names = read(ROOT / 'config/targets.json')
    files = []
    for d in data['diffs']:
        path = d['new_path']
        old_path = d['old_path']
        selected = [fn for fn in names if any(x.startswith('src/binary64/' + fn + '/') for x in [path, old_path])]
        clearly_other = all(re.match(r'^src/binary(?:16|32|80|128)/', x) or any(x.startswith('src/binary64/' + fn + '/') for fn in ['pow', 'hypot']) for x in [path, old_path])
        files.append({'path': path, 'old_path': old_path, 'functions': selected,
                      'classification': 'inventory_only' if clearly_other else 'needs_review'})
    out = {'base': args.base, 'pin': args.pin, 'cutoff_utc': utc(), 'files': files,
           'commits': [c['id'] for c in data.get('commits', [])],
           'note': 'Selection aid only: review shared/header/build changes manually. This does not advance a reviewed baseline.'}
    save(WORK / 'plan.json', out)
    print(json.dumps(out, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    defaults = read(ROOT / 'config/source.json')
    for name in ['doctor', 'run']:
        p = commands.add_parser(name)
        p.add_argument('--profile', default='gcc-linux-x86_64')
        if name == 'run':
            p.add_argument('--pin', type=pin_value, default=defaults['default_pin'])
            p.add_argument('--functions', default='all')
            p.add_argument('--errno', type=int, choices=[0, 1], default=1)
            p.add_argument('--run-id', required=True)
            p.add_argument('--max-minutes', type=float, default=60)
    p = commands.add_parser('fetch')
    p.add_argument('--pin', type=pin_value, default=defaults['default_pin'])
    p.add_argument('--functions', default='all')
    p = commands.add_parser('plan')
    p.add_argument('--pin', type=pin_value, default=defaults['default_pin'])
    p.add_argument('--base', type=pin_value, default=defaults['previous_review_pin'])
    p = commands.add_parser('export')
    p.add_argument('--run-id', required=True)
    p.add_argument('--week', required=True)
    args = parser.parse_args()
    for name in ['run_id', 'week']:
        if hasattr(args, name) and not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}', getattr(args, name)):
            parser.error('Unsafe ' + name)
    if hasattr(args, 'week'):
        try:
            dt.date.fromisoformat(args.week)
        except ValueError:
            parser.error('week must be an ISO date YYYY-MM-DD')
    if args.command == 'doctor':
        with locked():
            print(json.dumps(doctor(args.profile), indent=2))
    elif args.command == 'fetch':
        with locked():
            fetch(args.pin, targets(args.functions))
    elif args.command == 'run':
        if not 0 < args.max_minutes <= 240:
            parser.error('max-minutes must be in (0,240]')
        return execute(args)
    elif args.command == 'plan':
        plan(args)
    else:
        with locked():
            export(args)
    return 0


if __name__ == '__main__':
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop_run)
    try:
        sys.exit(main())
    except Exception as exc:
        if ACTIVE_RUN:
            save(ACTIVE_RUN / 'status.json', {'state': 'INTERRUPTED_OR_ERROR', 'error': clean(str(exc)), 'heartbeat_utc': utc()})
        print(clean(str(exc)), file=sys.stderr)
        sys.exit(1)
