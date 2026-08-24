# Finite predictive-class trace — 2026-08-25

## Result

Added `PredictivePartition.class_trace(state, boundary_bits)` to the bounded
Rule 30 surface. It records one finite partition class ID immediately before
each supplied boundary-driven update, matching the sampling convention of
`response_trace`. The method consumes an iterable once and returns an empty
tuple for an empty boundary word. A caller can use `set(partition.class_trace(...))`
for the classes visited by that finite trace.

The helper reuses the existing integer successor and partition objects. It does
not build another quotient or alter the recursive partition construction.

## Bounded evidence

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_successor tests.test_rule30_facade
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked

git diff --check
```

The new regression enumerates every encoded state for `h = 0..6` and every
boundary word of lengths `0..4`, comparing each class trace with an independent
step-by-step reference. It also checks one-shot iterable consumption and
initial-state validation.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a finite reproducibility helper. The
exhaustive partition remains exponential in the horizon, and the trace only
describes the supplied finite boundary word. It does not prove coverage beyond
the tested bounds, eventual coverage, an infinite-horizon quotient, or any
center-column periodicity statement.

## Changed paths

- `experiments/rule30_successor.py` — added the finite class-trace method.
- `tests/test_rule30_successor.py`, `tests/test_rule30_facade.py` — added exhaustive bounded regressions.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documented the finite semantics and limits.
