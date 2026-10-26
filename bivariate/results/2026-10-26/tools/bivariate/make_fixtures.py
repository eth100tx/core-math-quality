"""Deterministic qualification fixtures; no hard-case search/census claim."""
import json
from math import isqrt
from pathlib import Path


def record(x, y):
    s = x*x+y*y
    k = isqrt(s)//2
    lo = (0x400 << 52) + k-(1 << 52)
    exact = 4*k*k == s
    mid = (2*k+1)**2
    nearest = lo + int(s > mid or (s == mid and k % 2 == 1))
    return {'schema_version': 1, 'domain': 'positive-unit-binade-normal-result-v1',
            'x_bits': f'{(0x3ff<<52)+x-(1<<52):016x}',
            'y_bits': f'{(0x3ff<<52)+y-(1<<52):016x}',
            'lower_bits': f'{lo:016x}', 'upper_bits': f'{lo+1:016x}',
            'expected_bits': dict(zip(('rndn','rndz','rndu','rndd'),
                [f'{v:016x}' for v in (nearest,lo,lo if exact else lo+1,lo)]))}


def fixtures():
    pairs = [(48<<47,55<<47), (3<<51,3<<51), ((1<<53)-1,(1<<53)-1)]
    # Both tie parities and adjacent input values on either side.
    for m in [(1<<51)-1,(1<<51)-3]:
        for offset in [-1,0,1]:
            pairs.append((3*m+offset,4*m))
    # First result binade boundary: x=1, y just above sqrt(3).
    pairs.append((1<<52,isqrt(3<<104)+1))
    pairs += [(y,x) for x,y in pairs]
    return [record(x,y) for x,y in sorted(set(pairs))]


if __name__ == '__main__':
    Path(__file__).with_name('hypot-fixtures.json').write_text(
        json.dumps(fixtures(),indent=2)+'\n',encoding='utf-8')
