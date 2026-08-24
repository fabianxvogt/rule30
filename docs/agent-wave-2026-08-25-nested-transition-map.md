# Finite nested transition map — 2026-08-25

## Result

Added `PredictivePartition.nested_transition_map(lower)` to the repository-local
Rule 30 API. For every source class in the finite partition `S_h` and each
boundary bit, it applies one width-`h` integer update, removes the highest
encoded bit, and returns the target class in the adjacent partition `S_{h-1}`.
The method checks every member of every source class and raises if either
boundary bit produces more than one lower-horizon target.

The result is indexed as:

```python
mapping[source_class_id][boundary_bit]
```

This exposes the finite nested-transition check already present in the
exploratory automaton analysis while preserving all existing experiment import
paths.

## Bounded evidence

The regression suite exhaustively enumerates every encoded state and both
boundary bits at horizons `h = 1..6`. For every state it verifies that the
returned target equals the lower partition class of the updated state after
dropping the highest bit. It also verifies that all source classes are covered
exactly once and rejects non-adjacent lower partitions.

The existing integer implementation checker remains green through `h = 13`:

```text
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked
```

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a finite API and implementation check.
It does not prove the nested map beyond `h = 6`, make same-horizon class
transitions deterministic, establish an infinite-horizon quotient, prove any
general transition theorem, or say anything about center-column periodicity.
The exhaustive partition and map remain exponential in the horizon and are
intended for small bounded checks.

## Changed paths

- `experiments/rule30_successor.py` — added the checked nested transition API.
- `tests/test_rule30_successor.py` — added exhaustive state and boundary-bit regressions.
- `tests/test_rule30_facade.py` — added facade compatibility coverage.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documented the finite API and limits.
- This report — evidence, classification, and explicit limits.
