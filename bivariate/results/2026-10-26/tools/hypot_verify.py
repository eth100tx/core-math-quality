"""Exact-integer certificate checker for the restricted hypot v1 domain."""
import argparse
import json
from pathlib import Path
import re
import sys
import time

DOMAIN = 'positive-unit-binade-normal-result-v1'
MODES = ('rndn', 'rndz', 'rndu', 'rndd')
FIELDS = {'schema_version', 'domain', 'x_bits', 'y_bits', 'lower_bits', 'upper_bits', 'expected_bits'}


def unique(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError('Duplicate key: ' + k)
        d[k] = v
    return d


def loads(text):
    return json.loads(text, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def bits(s, exponent):
    if not isinstance(s, str) or not re.fullmatch('[0-9a-f]{16}', s):
        raise ValueError('Require canonical 16-digit lowercase bit encoding')
    u = int(s, 16)
    if u >> 52 != exponent:
        raise ValueError('Sign/exponent outside restricted domain')
    return u, (1 << 52) + (u & ((1 << 52) - 1))


def verify(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError('Missing/unknown certificate fields')
    if type(record['schema_version']) is not int or record['schema_version'] != 1 or record['domain'] != DOMAIN:
        raise ValueError('Unsupported version/domain')
    _, x = bits(record['x_bits'], 0x3ff)
    _, y = bits(record['y_bits'], 0x3ff)
    lo, k = bits(record['lower_bits'], 0x400)
    hi, upper = bits(record['upper_bits'], 0x400)
    s = x*x + y*y
    if not 4*(1 << 104) <= s < 8*(1 << 104):
        raise ValueError('Result outside restricted domain')
    if hi != lo+1 or upper != k+1 or not 4*k*k <= s < 4*(k+1)*(k+1):
        raise ValueError('Invalid bracket')
    exact = s == 4*k*k
    delta = s - (2*k+1)**2
    nearest = lo if delta < 0 or (delta == 0 and k % 2 == 0) else hi
    answers = dict(zip(MODES, [lo if exact else nearest, lo, lo if exact else hi, lo]))
    expected = record['expected_bits']
    if not isinstance(expected, dict) or set(expected) != set(MODES):
        raise ValueError('Missing/unknown expected modes')
    for mode in MODES:
        actual, _ = bits(expected[mode], 0x400)
        if actual != answers[mode]:
            raise ValueError('Incorrect expected value: ' + mode)
    return {'expected_bits': {m: f'{v:016x}' for m, v in answers.items()},
            'exact': exact, 'midpoint_relation': (delta > 0) - (delta < 0),
            'expected_flags': {'inexact': int(not exact), 'invalid': 0,
                               'divbyzero': 0, 'underflow': 0, 'overflow': 0},
            'expected_errno': 0}


def read_table(path):
    path = Path(path)
    if path.stat().st_size > 4*1024*1024:
        raise ValueError('Certificate file exceeds 4 MiB')
    d = loads(path.read_text(encoding='utf-8'))
    if not isinstance(d, list) or not 1 <= len(d) <= 4096:
        raise ValueError('Require 1..4096 records')
    for row in d:
        verify(row)
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('certificates', type=Path)
    args = p.parse_args()
    started, cpu = time.monotonic(), time.process_time()
    rows = read_table(args.certificates)
    print(json.dumps({'schema_version': 1, 'status': 'PASS', 'checked': len(rows),
                      'rejected': 0, 'results': [verify(r) for r in rows],
                      'completeness_census_regenerated': False,
                      'cpu_seconds': time.process_time()-cpu,
                      'wall_seconds': time.monotonic()-started}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
