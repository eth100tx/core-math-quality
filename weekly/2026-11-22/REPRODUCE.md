# Reproduce the November 22 scoped results

Implementation `333d11d04d73ef165cf217e773b3b3d6372aa66f`; proof `08b804138d9e39b507522762c5b0df5e1b0b1478`. Workbench start `61a3e35ef41c4dc62b48b4dafdb530a6a40ea4a3`.

## Hypot reference and table

Run the [candidate's standard-library command](../../candidates/hypot-compact-table/README.md). The verifier checks the pinned table SHA-256 and mathematical row predicates, then compares a monotone binary64-bit-pattern binary search with the imported integer-square-root oracle. Mode order is RN, RD, RU, RZ. Positive hypot outputs mean RD=RZ. For overflow the binary-search upper neighbor is the virtual exact value 2^1024 before encoding infinity. Input scaling uses integer units of 2^-1074. No platform floating arithmetic enters either oracle. Provenance lists each unmodified imported byte hash.

## Clang object comparison

Obtain the exact `src/binary64/asin/asin.c` from the implementation pin into a disposable directory. The following command refuses any other source hash:

```sh
python3 -I -B weekly/2026-11-22/compare_clang.py /path/to/asin.c /tmp/clang-asin.objdump
```

The listing tool was GNU objdump (GNU Binutils for Ubuntu) 2.42. The two objects use `clang-18 -O3 -march=x86-64-v3 -frounding-math -fno-finite-math-only -DCORE_MATH_SUPPORT_ERRNO`, varying only contraction fast/off. Both hashes are `4b5a47ca513e3fcf431c2f258055d1d4d74523024cc198f79963d342982382ca`. The stored [listing](clang.objdump) has no debug paths. In `as_asin_refine`, the leading polynomial chain uses `vmulsd` at 0x185 and `vaddsd` at 0x18d, then multiplication/addition at 0x19a/0x19e. The double-double high sum is multiplication at 0x1aa, addition at 0x1b6 and separate subtractions at 0x1ba/0x1be. The explicit FMA at 0x195 is a different source operation. The final high part is moved at 0x329 before the exponent mask at 0x32e. Addresses are scoped to this listing, not future builds. Direct source/debug-listing inspection corroborated these dependencies. The ordinary doctor and a Clang v3 binary64 rounding/subnormal/FMA probe passed.

This is an object-equivalence result only. We did not reproduce the full strict range enclosure on this object or bind every libm square-root assumption; those remain limits of a stronger range-transfer claim.

## Tangent full corpus

```sh
python3 quality.py doctor --profile clang-linux-x86_64
timeout 600 python3 quality.py run --pin 333d11d04d73ef165cf217e773b3b3d6372aa66f --functions tan --profile clang-linux-x86_64 --errno 1 --run-id your-unique-run-id --max-minutes 5
```

Use the normal runner lock and an outer monitored cap. Network acquisition is included in the five-minute dispatch budget; a slow download may produce an incomplete result. Our run completed in 288.4 seconds. Do not reinterpret an incomplete reproduction as a pass. The exported result contains per-mode accepted counts, command flags, source blobs and corpus hashes. Its compiler profile is baseline x86-64, distinct from the asin v3 comparison.
