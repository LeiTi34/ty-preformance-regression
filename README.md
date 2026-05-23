# ty 0.0.39 performance regression: `dict(value)` on union of TypedDicts

`ty check` has a severe performance regression in **0.0.39** vs **0.0.38**
when type-checking a call to `dict(value)` (or `dict(**value)`) where
`value` is typed as a union of `TypedDict` classes.

The check still completes (no infinite loop), but the runtime grows
super-linearly in both the number of union members and the number of
keys per `TypedDict`. With 19 variants × 8 keys, ty 0.0.39 takes
~115 seconds on a 250-line file with no imports; ty 0.0.38 takes ~0.08s
on the same file.

In our production codebase this manifests as a CI step exceeding GitHub
Actions' "no output" watchdog and getting cancelled (~57s into the run).

## Setup

```bash
# uv: https://docs.astral.sh/uv/
uv --version    # any recent version
```

No project setup required — repro file has zero imports beyond `typing`.

## Quick reproduction

```bash
# 19 variants × 5 required keys, 200 lines of stdlib-only Python:
time uvx ty@0.0.38 check minimal.py    # ~0.17s  All checks passed!
time uvx ty@0.0.39 check minimal.py    # ~12s    All checks passed!
```

## Full benchmark matrix

```bash
./bench.sh
```

Sample output on Linux x86_64:

```
=== ty 0.0.38 ===
ty 0.0.38  n= 4 k=1  rc=0   0.09s
ty 0.0.38  n= 4 k=8  rc=0   0.07s
ty 0.0.38  n= 8 k=8  rc=0   0.07s
ty 0.0.38  n=12 k=8  rc=0   0.08s
ty 0.0.38  n=16 k=8  rc=0   0.08s
ty 0.0.38  n=19 k=1  rc=0   0.08s
ty 0.0.38  n=19 k=3  rc=0   0.08s
ty 0.0.38  n=19 k=5  rc=0   0.08s
ty 0.0.38  n=19 k=8  rc=0   0.08s

=== ty 0.0.39 ===
ty 0.0.39  n= 4 k=8  rc=0   0.08s
ty 0.0.39  n= 8 k=8  rc=0   0.15s
ty 0.0.39  n=12 k=8  rc=0   2.34s
ty 0.0.39  n=16 k=8  rc=0  75.89s
ty 0.0.39  n=19 k=1  rc=0   2.85s
ty 0.0.39  n=19 k=3  rc=0   3.99s
ty 0.0.39  n=19 k=5  rc=0   7.37s
ty 0.0.39  n=19 k=8  rc=0 115.31s
```

ty 0.0.38: **runtime is flat at ~0.08s** across the entire matrix.
ty 0.0.39: runtime grows roughly exponentially in `n` and `k`
(rc=124 means GNU `timeout` killed the process after 120s).

For our production codebase (19 union variants, mixed `NotRequired` keys),
the wall-clock for the offending file alone is ~60s on ty 0.0.39 vs
~0.7s on ty 0.0.38 — a ~85× slowdown that pushes CI past the
no-output-watchdog cancellation threshold.

## What triggers it

The trigger is **`dict(v)`** where `v` is typed as a union of `TypedDict`
classes. Any other access pattern stays fast on 0.0.39:

| Code in body of `def use(v: U) -> None:` | ty 0.0.39 time |
| ---------------------------------------- | -------------- |
| `_ = dict(v)`                            | 12.05s         |
| `_ = {**v}`                              | 0.15s          |
| `_ = list(v.keys())`                     | 0.16s          |
| `_ = list(v.items())`                    | 0.13s          |
| `_ = v["type"]`                          | 0.15s          |
| `pass`                                   | 0.12s          |

(Measured at n=19 variants × 5 required keys.)

Whether the keys are `Required` or `NotRequired` makes no difference —
the same blowup occurs with all-required `TypedDict` keys.

## Files

- `minimal.py` — fixed-size, self-contained reproducer (n=19 × k=5,
  ~200 lines, no imports beyond `typing`).
- `generate.py` — parameterised generator: `python3 generate.py <n> <k> <out>`.
- `bench.sh` — runs ty 0.0.38 and 0.0.39 over a matrix of (n, k).

## Environment

- Linux x86_64
- ty installed via `uvx ty@<version>` (uv 0.11+)
- Python target inferred from venv (3.12 / 3.14 — tested both, same result)
- ty 0.0.38: known-good baseline
- ty 0.0.39: regression

## Suspected cause

Inferring the return type of `dict(value)` when `value` is a union of
`TypedDict` types appears to be done by enumerating the cross product of
union members and keys instead of being short-circuited to a single
`dict[str, <union of value types>]` (or similar) result. ty 0.0.38
clearly has a fast path here that ty 0.0.39 lost.

All 18 worker threads in the ty process show heavy CPU activity (~98%
summed) and frequent futex waits during this period — i.e., busy work,
not a deadlock.
