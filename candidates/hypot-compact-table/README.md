# Compact hypot supplied-table replay

This is a reusable exact-integer checker and the five unchanged source/data files it needs from the October 12 portable bundle. All **160 supplied families** satisfy their non-tie midpoint-H100 inequalities. An independent binary-search reference agrees with the imported integer reference on **1,604 finite ordered input pairs in four modes**. [Receipt](../../weekly/2026-11-22/table-replay.json) · [Provenance and hashes](PROVENANCE.json)

Run from the repository root, with Python 3.10 or later:

```sh
python3 -I -B candidates/hypot-compact-table/verify_table.py candidates/hypot-compact-table
```

Only the Python standard library is required. The imported code hashes are checked before import. The independent checker uses exact squared inequalities to verify each table entry and monotone binary search on binary64 encodings to cross-check the imported square-root reference. It rejects a mathematically invalid row, an exact midpoint tie, a damaged table digest and includes a wrong-neighbor comparison sanity check; four known-answer controls cover zero, 3–4–5, minsubnormal and overflow.

The closed-form **323,428 positive canonical scale realizations** count is conditional on these supplied families. It is not an enumeration of those scales. The 1,280 hard input pairs use one scale per family, all signs and both orders; 324 format-boundary pairs are separate. The omitted-row demonstration still passes the row inequalities, making the completeness limitation explicit.

Two exact Pythagorean midpoint fixtures exercise ties-to-even in both parity directions. The 1,604 ordered signed inputs reduce to 205 distinct unsigned unordered magnitude problems. The two reference algorithms locate neighbors independently but use the same exact midpoint decision formula; the known-answer controls therefore matter.

## What is still missing

The original native replay harness (`qualify_hypot_full_replay.py`, `hypot_full_replay.c`) and its raw receipt are not in this compact archive. Nor is the adjacent-family census generator and its original exclusion/residual evidence. The historical Windows GCC 16.2 run and its 2,587,424 cases have **not** been reproduced here. This publication executes no CORE-MATH implementation and checks no flags or errno. The separately qualified restricted Linux adapter remains [a different result](../../docs/HYPOT-QUALIFICATION.md).

Imported classifier docstrings describe theorem-backed membership relying on a separate finite census. Preserve that provenance, but do not use a negative membership result as a newly established completeness theorem. No new bug, new hard-case discovery, novelty or upstream corpus addition is claimed. Angular and pow import and full-corpus stage comparisons remain separate tasks.
