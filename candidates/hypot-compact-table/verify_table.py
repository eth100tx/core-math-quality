"""Replay supplied hypot families and finite references using exact integers.

This verifies entries in a supplied table. It does not regenerate the census.
Run with the portable package directory as the sole argument.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile

MAX_FINITE = 0x7fefffffffffffff
INFINITY = 0x7ff0000000000000
TABLE_HASH = "9e344278d2e29614d0c2df67ba0c2ea1d024cb5185853654841b5eea369c2261"
CODE_HASHES = {
    "hypot_family_classifier.py": "e0365361ea0de0172dc82b862282564f48063d4e4c61a27f3ab63e9baf78f2c2",
    "hypot_finite_classifier.py": "43096c7d81ca216d8f81b853dbf035d1a2b483bb1417fc09fafc2e7637ec478a",
    "hypot_integer_reference.py": "7684a19ea7578469e81a7f9c134ef6501425a79ccb7477abe0f81b4e2f531f10",
    "hypot_qa_cli.py": "001a76b0e31413e3705b16a1498b486a3bcbf78ebd409fd96c6a35334bdf67c0",
}


def check_family(row):
    a, b, gap = row
    if any(type(v) is not int for v in row):
        raise ValueError("integer family required")
    if not (2**52 <= a < 2**53 and 2**52 <= b < 2**53 and gap in (24, 25, 26)):
        raise ValueError("family domain")
    squared = (a << gap)**2 + b*b
    root_floor = math.isqrt(squared)
    spacing = 1 << (root_floor.bit_length() - 53)
    lower = root_floor // spacing * spacing
    if not lower*lower <= squared < (lower+spacing)**2:
        raise ValueError("containing cell")
    twice_midpoint = 2*lower + spacing
    # Multiply sqrt(S) and both tolerance endpoints by 2**100.
    center = twice_midpoint << 99
    if not (center-spacing)**2 <= squared << 200 <= (center+spacing)**2:
        raise ValueError("family misses H100 midpoint interval")
    residual = 4*squared - twice_midpoint**2
    if residual == 0:
        raise ValueError("exact midpoint tie excluded")
    return {"a": a, "b": b, "gap": gap, "spacing": str(spacing), "squared_residual_times_four": str(residual)}


def integer_units(bits):
    magnitude = bits & ((1 << 63)-1)
    exponent, fraction = divmod(magnitude, 1 << 52)
    if exponent == 2047:
        raise ValueError("finite inputs required")
    if exponent == 0:
        return fraction
    return ((1 << 52)+fraction) << (exponent-1)


def binary_search_reference(x, y):
    """Locate bounding binary64 values by monotone squared comparisons."""
    squared = integer_units(x)**2 + integer_units(y)**2
    lo, hi = 0, MAX_FINITE
    while lo < hi:
        middle = (lo+hi+1)//2
        if integer_units(middle)**2 <= squared:
            lo = middle
        else:
            hi = middle-1
    lower_units = integer_units(lo)
    if lower_units**2 == squared:
        return [lo]*4
    upper = lo+1
    upper_units = 1 << 2098 if upper == INFINITY else integer_units(upper)
    side = 4*squared - (lower_units+upper_units)**2
    nearest = lo if side < 0 or (side == 0 and lo % 2 == 0) else upper
    return [nearest, lo, upper, lo]


def replay(package):
    for name, digest in CODE_HASHES.items():
        if hashlib.sha256((package/"tools"/name).read_bytes()).hexdigest() != digest:
            raise ValueError("imported code identity: "+name)
    table_path = package / "data/hypot-h100-families.json"
    raw = table_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != TABLE_HASH:
        raise ValueError("supplied table identity")
    table = json.loads(raw)
    rows = table["triples"]
    if len(rows) != 160 or len(set(map(tuple, rows))) != 160:
        raise ValueError("family count or uniqueness")
    checks = [check_family(row) for row in rows]
    # This control bypasses digest verification and must fail mathematically.
    bad = list(sorted(rows)[0])
    bad[1] ^= 1
    try:
        check_family(bad)
    except ValueError as err:
        if str(err) != "family misses H100 midpoint interval":
            raise
    else:
        raise ValueError("mathematical negative control escaped")
    tie = [(1 << 52)+(1 << 26), (1 << 52)+(1 << 25), 26]
    try:
        check_family(tie)
    except ValueError as err:
        if str(err) != "exact midpoint tie excluded":
            raise
    else:
        raise ValueError("tie negative control escaped")
    scales = 0
    for a, b, gap in rows:
        valuation_a = (a & -a).bit_length()-1
        valuation_b = (b & -b).bit_length()-1
        low = max(-1074-valuation_a-gap, -1074-valuation_b)
        high = 971-gap
        if (a << gap)**2+b*b > (((1 << 53)-1) << gap)**2 or valuation_b > 4:
            raise ValueError("scale endpoint premise")
        scales += high-low+1
    if scales != 323428:
        raise ValueError("scale count")
    sys.path.insert(0, str(package / "tools"))
    from hypot_family_classifier import Classifier
    from hypot_finite_classifier import FiniteClassifier
    from hypot_qa_cli import hard_cases, boundary_cases
    from hypot_integer_reference import expected
    with tempfile.TemporaryDirectory() as directory:
        mutated = dict(table)
        mutated["triples"] = [bad] + rows[1:]
        path = Path(directory)/"corrupted.json"
        path.write_text(json.dumps(mutated))
        try:
            Classifier(path)
        except ValueError as err:
            if str(err) != "table identity":
                raise
        else:
            raise ValueError("digest negative control escaped")
    classifier = FiniteClassifier()
    hard = list(hard_cases(classifier))
    boundary = list(boundary_cases())
    if len(hard) != 1280 or len(boundary) != 324:
        raise ValueError("export population changed")
    digest = hashlib.sha256()
    for x, y, kind in hard+boundary:
        reference = binary_search_reference(x, y)
        if expected(x, y) != reference:
            raise ValueError("reference mismatch")
        if kind == "non_tie_midpoint_h100" and classifier.classify(x, y)["hit"] is not True:
            raise ValueError("hard row classification mismatch")
        digest.update((json.dumps([x, y, reference], separators=(",", ":"))+"\n").encode())
    known = [(0, 0, [0]*4), (0x4008000000000000, 0x4010000000000000, [0x4014000000000000]*4),
             (1, 1, [1, 1, 2, 1]), (MAX_FINITE, MAX_FINITE, [INFINITY, MAX_FINITE, INFINITY, MAX_FINITE])]
    for x, y, answer in known:
        if binary_search_reference(x, y) != answer or expected(x, y) != answer:
            raise ValueError("known-answer control failed")
    # Exact 3k,4k Pythagorean inputs give a norm 5k at a binary64 midpoint.
    # Both inputs are exact integers below 2**53; the norm lies in spacing 2.
    def integer_bits(n):
        exponent = n.bit_length()-1
        if exponent <= 52:
            significand = n << (52-exponent)
        else:
            significand, remainder = divmod(n, 1 << (exponent-52))
            if remainder:
                raise ValueError("control integer is not exactly representable")
        return ((exponent+1023) << 52) | (significand-(1 << 52))
    tie_controls = []
    for k, rounds_up in [(2*10**15+1, False), (2*10**15+3, True)]:
        x, y = integer_bits(3*k), integer_bits(4*k)
        lower, upper = integer_bits(5*k-1), integer_bits(5*k+1)
        if lower % 2 != int(rounds_up):
            raise ValueError("tie control parity")
        answer = [upper if rounds_up else lower, lower, upper, lower]
        if binary_search_reference(x, y) != answer or expected(x, y) != answer:
            raise ValueError("exact tie control failed")
        tie_controls.append({"k": k, "x": x, "y": y, "expected": answer})
    wrong = expected(hard[0][0], hard[0][1])
    wrong[0] ^= 1
    if wrong == binary_search_reference(hard[0][0], hard[0][1]):
        raise ValueError("wrong-neighbor control escaped")
    return {"table_sha256": TABLE_HASH, "family_count": len(rows),
            "gap_counts": dict(sorted(Counter(row[2] for row in rows).items())),
            "scale_realizations_counted_without_enumeration": scales,
            "top_scale_overflow_excluded_for_each_supplied_row": True,
            "omitting_one_row_still_passes_arithmetic": all(check_family(row) for row in rows[1:]),
            "family_checks": checks, "hard_inputs": len(hard), "boundary_inputs": len(boundary),
            "reference_modes": ["RN", "RD", "RU", "RZ"], "reference_comparisons": 4*(len(hard)+len(boundary)),
            "reference_digest": digest.hexdigest(), "distinct_unsigned_unordered_magnitude_pairs": len({tuple(sorted((x & ((1 << 63)-1), y & ((1 << 63)-1)))) for x, y, _ in hard+boundary}),
            "tie_controls": tie_controls, "controls": ["invalid family rejected mathematically",
            "modified table rejected by digest", "exact midpoint family tie rejected", "four known answers", "two exact rounding ties with opposite parity", "wrong-neighbor comparison sanity check"],
            "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "package_code_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((package/'tools').glob('*.py'))},
            "completeness_census_regenerated": False, "core_math_executed": False,
            "flags_checked": False, "errno_checked": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.package.resolve()), indent=2))
