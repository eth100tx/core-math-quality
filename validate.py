#!/usr/bin/env python3
"""Fail closed on unknown receipt fields, broken checksums or private paths."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
TOP = {'schema_version', 'run_id', 'created_utc', 'identity', 'results', 'ranking',
       'status', 'this_invocation_child_cpu_seconds', 'wall_seconds', 'scope'}
IDENTITY = {'pin', 'profile', 'errno', 'functions', 'runner_sha256', 'environment', 'source_manifest', 'resolved_profile', 'config_hashes'}
CELL = {'function', 'profile', 'errno', 'status', 'started_utc', 'flags', 'environment',
        'corpus_rows', 'expected_tests_per_mode', 'source_sha256', 'corpus_sha256',
        'checker_sha256', 'modes', 'logs', 'coverage_flags', 'finished_utc', 'coverage_union', 'error', 'copied_files', 'macros_referenced'}
ENV = {'profile', 'compiler', 'platform', 'architecture', 'libc', 'probe', 'status', 'experimental', 'gcov'}
COVERAGE = {'lines_total', 'lines_hit', 'arcs_total', 'arcs_hit', 'missing_lines', 'missing_arcs'}


def keys(obj, allowed, name):
    extra = set(obj) - allowed
    if extra:
        raise ValueError(f'{name}: unknown fields {sorted(extra)}')


def receipt(d):
    keys(d, TOP, 'receipt')
    if set(d) != TOP or d['schema_version'] != 1:
        raise ValueError('Missing/unknown schema fields')
    ident = d['identity']
    keys(ident, IDENTITY, 'identity')
    if set(ident) != IDENTITY or not re.fullmatch('[a-f0-9]{40}', ident['pin']):
        raise ValueError('Incomplete identity')
    selected = ident['functions']
    if not selected or len(selected) != len(set(selected)):
        raise ValueError('Empty or duplicate selection')
    if [cell['function'] for cell in d['results']] != selected:
        raise ValueError('Receipt results do not match selected functions')
    if any(cell.get('profile',ident['profile']) != ident['profile'] or cell.get('errno',ident['errno']) != ident['errno'] for cell in d['results']):
        raise ValueError('Cell configuration differs from run identity')
    keys(ident['environment'], ENV, 'environment')
    keys(ident['resolved_profile'], {'cc', 'gcov', 'system', 'machine', 'flags', 'coverage', 'experimental'}, 'profile')
    keys(ident['source_manifest'], {'pin', 'files', 'archives', 'git_blobs'}, 'source manifest')
    for path, h in ident['source_manifest']['files'].items():
        if not path.startswith('src/binary64/') or '..' in Path(path).parts or not re.fullmatch('[a-f0-9]{64}', h):
            raise ValueError('Unsafe manifest')
    for archive in ident['source_manifest']['archives'].values():
        keys(archive, {'url', 'sha256'}, 'archive')
        if not archive['url'].startswith('https://gitlab.inria.fr/api/v4/projects/35719/repository/archive.tar.gz?'):
            raise ValueError('Unknown source URL')
    keys(d['ranking'], {'population', 'measured', 'complete_population', 'policy', 'candidates', 'recommendation'}, 'ranking')
    for c in d['ranking']['candidates']:
        keys(c, {'function', 'missing_lines', 'missing_arcs'}, 'rank')
    for cell in d['results']:
        keys(cell, CELL, 'cell')
        if 'environment' in cell:
            keys(cell['environment'], ENV, 'cell environment')
        for log in cell.get('logs', {}).values():
            keys(log, {'returncode', 'output', 'wall_seconds', 'command', 'output_bytes', 'output_truncated'}, 'log')
        for mode in cell.get('modes', []):
            keys(mode, {'mode', 'plain', 'accepted_tests', 'covered', 'coverage',
                        'gcov_json_format_version', 'other_instrumented_files', 'error'}, 'mode')
            if 'coverage' in mode:
                keys(mode['coverage'], COVERAGE, 'mode coverage')
        if 'coverage_union' in cell:
            keys(cell['coverage_union'], COVERAGE, 'union')
        if cell['status'] == 'PASS':
            if [m['mode'] for m in cell['modes']] != ['rndn', 'rndz', 'rndu', 'rndd']:
                raise ValueError('PASS without all modes')
            for mode in cell['modes']:
                if mode['accepted_tests'] != cell['expected_tests_per_mode']:
                    raise ValueError('Mismatched accepted rows')
                if mode['plain'] != 'PASS':
                    raise ValueError('False cell PASS')
                if ident['resolved_profile']['coverage'] and (mode.get('covered') != 'PASS' or 'coverage' not in mode):
                    raise ValueError('Coverage PASS without measurements')
    if d['status'] == 'PASS' and any(c['status'] != 'PASS' for c in d['results']):
        raise ValueError('False aggregate PASS')
    from quality import ranking
    if d['ranking'] != ranking(d['results'], ident['functions']):
        raise ValueError('Ranking differs from measured results')


def raw_coverage_paths(folder, recursive=True):
    # pathlib glob is case-insensitive on Windows. Keep the Linux filename
    # contract on Python 3.10 too (case_sensitive= requires Python 3.12).
    paths = folder.rglob('*-coverage.json') if recursive else folder.glob('*-coverage.json')
    return sorted(p for p in paths if p.name.endswith('-coverage.json'))


def verify_coverage(cell, folder):
    from quality import coverage_maps, coverage_summary, add_union
    if len(raw_coverage_paths(folder, recursive=False)) != 4:
        raise ValueError('PASS needs four raw coverage files')
    ul, ua = {}, {}
    for mode in cell['modes']:
        raw = json.loads((folder / (mode['mode'] + '-coverage.json')).read_text())
        ls, ar = coverage_maps(raw)
        if coverage_summary(ls,ar) != mode['coverage']:
            raise ValueError('Coverage summary disagrees with raw counts')
        ul, ua = add_union(ul,ls), add_union(ua,ar)
    if coverage_summary(ul,ua) != cell['coverage_union']:
        raise ValueError('Coverage union disagrees with raw counts')


def main():
    count = 0
    for path in (ROOT/'weekly').rglob('result.json'):
        d = json.loads(path.read_text())
        receipt(d)
        if d['identity']['resolved_profile']['coverage']:
            for cell in d['results']:
                if cell['status'] != 'PASS':
                    continue
                folder = path.parent / f"{cell['function']}-{cell['profile']}-errno{cell['errno']}"
                verify_coverage(cell, folder)
        count += 1
    for path in (ROOT/'candidates').rglob('checks.json'):
        d=json.loads(path.read_text())
        keys(d, {'status','pin','witness','scope','runner_sha256','reproduce_sha256','results','child_cpu_seconds','wall_seconds'}, 'candidate checks')
        if d['status'] != 'PASS' or set(d['results']) != {'before','after'}:
            raise ValueError('Incomplete candidate comparison')
        for label,cell in d['results'].items():
            keys(cell,CELL,'candidate cell')
            if cell['status']!='PASS' or [m['mode'] for m in cell['modes']]!=['rndn','rndz','rndu','rndd']:
                raise ValueError('Candidate lacks four-mode PASS')
            if any(m['plain']!='PASS' or m['covered']!='PASS' or m['accepted_tests']!=cell['expected_tests_per_mode'] for m in cell['modes']):
                raise ValueError('Candidate mode failure or count mismatch')
            verify_coverage(cell,path.parent/label)
        before,after=d['results']['before'],d['results']['after']
        if before['source_sha256']!=after['source_sha256'] or after['corpus_rows']!=before['corpus_rows']+1:
            raise ValueError('Unexpected candidate source/corpus change')
    for path in raw_coverage_paths(ROOT/'weekly') + raw_coverage_paths(ROOT/'candidates'):
        d = json.loads(path.read_text())
        keys(d, {'file','functions','lines'}, 'gcov file')
        if not re.fullmatch(r'src/binary64/[a-z0-9]+/[a-z0-9]+\.c',d['file']):
            raise ValueError('Unsafe gcov source path')
        for f in d['functions']:
            keys(f, {'name','demangled_name','start_line','start_column','end_line','end_column',
                     'blocks','blocks_executed','execution_count'},'gcov function')
        for line in d['lines']:
            keys(line, {'line_number','function_name','count','branches','unexecuted_block','block_ids',
                        'calls','conditions'},'gcov line')
            for branch in line.get('branches',[]):
                keys(branch,{'count','fallthrough','throw','source_block_id','destination_block_id'},'gcov branch')
    for sums in list((ROOT/'weekly').rglob('SHA256SUMS.json'))+list((ROOT/'candidates').rglob('SHA256SUMS.json')):
        manifest = json.loads(sums.read_text())
        actual = {p.relative_to(sums.parent).as_posix() for p in sums.parent.rglob('*') if p.is_file() and p != sums}
        if actual != set(manifest):
            raise ValueError('Unlisted or missing evidence files')
        for rel, expected in manifest.items():
            path = (sums.parent/rel).resolve()
            if not path.is_relative_to(sums.parent.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('Manifest mismatch: ' + rel)
    # Additional leak screen. Structural allowlists above are the first boundary;
    # free-text evidence must still receive a human/AI privacy review.
    forbidden = [r'[A-Za-z]:\\Users\\', r'/mnt/[a-z]/Users/', r'/home/[^\s/]+', r'/Users/[^\s/]+',
                 r'(?i)authorization:\s*bearer', r'gh[pousr]_[A-Za-z0-9]{20,}',
                 r'(?m)^(?:Received|Delivered-To|Message-Id|From|To|Subject):',
                 r'[\w.+-]+@(?!users\.noreply\.github\.com)[\w.-]+\.[a-zA-Z]{2,}']
    for parent in ['weekly', 'candidates', 'docs', 'prompts', 'templates', 'examples']:
        for path in (ROOT/parent).rglob('*'):
            if path.is_file() and any(re.search(p, path.read_text()) for p in forbidden):
                raise ValueError('Private material in ' + str(path.relative_to(ROOT)))
    for path in ROOT.glob('*.md'):
        if any(re.search(p, path.read_text()) for p in forbidden):
            raise ValueError('Private material in ' + path.name)
    import subprocess
    if (ROOT/'.git').exists():
        p = subprocess.run(['git', 'log', '--format=%ae%n%ce'], cwd=ROOT, capture_output=True, text=True)
        if p.returncode == 0 and any(not email.endswith('@users.noreply.github.com') for email in p.stdout.splitlines()):
            raise ValueError('Use public-safe noreply commit identity')
    print(f'Validated {count} receipts, evidence checksums and publication privacy screen')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
