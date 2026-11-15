"""Compare the pinned single-thread worst-case input generators; requires Linux GCC and MPFR."""
import ctypes
import ctypes.util
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

OLD = "4dbfe52b9542e9c412f505d2fad4dc0ed3bb5738d5be699569808101ae26fc45"
NEW = "fe8f55125c456cab195e27a09b317ffa8e120ca7d6bfd2829fe3a4747366ef65"
COUNT = 128
SEEDS = (19, 2026)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replay(file, expected, folder, label):
    data = file.read_bytes()
    if digest(data) != expected:
        raise ValueError("unexpected source hash")
    source = data.decode()
    # Replace the value checker at its boundary. Keep the sampling loop, gap
    # scaling and MPFR y_worst unchanged; the saved raw words precede frexp.
    a = source.index("void\ncheck (double x, double y)")
    b = source.index("#ifndef CORE_MATH_TESTS", a)
    source = source[:a] + '''void check(double x, double y) {
      if (slot != 2) exit(3);
      slot = 0;
      printf("%016llx %016llx %016llx %016llx\\n",
        (unsigned long long)draw[0], (unsigned long long)draw[1],
        (unsigned long long)asuint64(x), (unsigned long long)asuint64(y));
    }
    ''' + source[b:]
    source = source.replace("static double\nget_random", "static uint64_t draw[2];\nstatic unsigned slot;\nstatic double\nget_random", 1)
    source = source.replace("return v.f;", "draw[slot++ % 2] = v.u; return v.f;", 1)
    source = source.replace("getpid ()", "sample_seed").replace("#include <unistd.h>", "#include <unistd.h>\nstatic int sample_seed;")
    source = source[:source.index("static uint64_t\ngcd")] + '''
      void ref_init(void) {}
      int ref_fesetround(int mode) { return mode; }
      int main(int argc, char **argv) {
        if (argc != 2) return 2;
        if (fesetround(FE_TONEAREST) || fegetround() != FE_TONEAREST) return 4;
        sample_seed = atoi(argv[1]);
        for (int gap = 1; gap <= 27; ++gap) check_worst(gap);
        return 0;
      }
    '''
    unit = folder / (label + ".c")
    unit.write_text(source)
    exe = folder / label
    subprocess.run(["gcc", "-O2", "-frounding-math", "-ffunction-sections",
                    "-DCORE_MATH_NO_OPENMP", "-DCORE_MATH_TESTS="+str(COUNT),
                    str(unit), "-Wl,--gc-sections", "-lmpfr", "-lgmp", "-lm", "-o", str(exe)],
                   check=True, timeout=40)
    return {seed: subprocess.check_output([str(exe), str(seed)], timeout=45) for seed in SEEDS}


def verify(old, new):
    receipts = {}
    with tempfile.TemporaryDirectory() as work:
        a = replay(old, OLD, Path(work), "before")
        b = replay(new, NEW, Path(work), "after")
    for seed in SEEDS:
        if a[seed] != b[seed]:
            raise ValueError("old/new candidate trace differs")
        lines = [line.split() for line in a[seed].splitlines()]
        if len(lines) != 27 * COUNT or any(len(line) != 4 for line in lines):
            raise ValueError("incomplete trace")
        gaps = [lines[k:k+COUNT] for k in range(0, len(lines), COUNT)]
        raw = [[row[:2] for row in gap] for gap in gaps]
        if any(group != raw[0] for group in raw[1:]):
            raise ValueError("raw stream changed between gaps")
        if gaps[0][0][2:] == gaps[-1][0][2:]:
            raise ValueError("gap scaling control failed")
        receipts[seed] = {"trace_sha256": digest(a[seed]), "rows": len(lines),
                          "distinct_final_pairs": len({tuple(row[2:]) for row in lines})}
    if a[SEEDS[0]] == a[SEEDS[1]]:
        raise ValueError("seed sensitivity control failed")
    library = ctypes.CDLL(ctypes.util.find_library('mpfr'))
    library.mpfr_get_version.restype = ctypes.c_char_p
    return {"per_gap": COUNT, "gaps": 27, "seeds": receipts, "libc": platform.libc_ver(),
            "compiler": subprocess.check_output(["gcc","-dumpfullversion"],text=True).strip(),
            "mpfr": library.mpfr_get_version().decode(),
            "mode": "round to nearest", "old_sha256": OLD, "new_sha256": NEW,
            "raw_pairs_per_seed_before_gap_scaling": COUNT, "openmp": False,
            "numerical_checker_executed": False}


if __name__ == "__main__":
    print(json.dumps(verify(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
