# Finite cross-horizon map — 2026-08-25

## Result

Added `PredictivePartition.right_truncation_map(lower)` to the bounded Rule 30
API. Given exhaustive partitions at adjacent horizons `h` and `h - 1`, it
returns a tuple indexed by the `S_h` class IDs. Each entry is the `S_{h-1}`
class reached by removing the highest encoded bit from a member state.

The implementation checks every member of every source class and raises if a
class would map to more than one lower-horizon class. It therefore exposes the
finite well-definedness check already used by the exploratory truncation
analysis, without importing that script or assuming an unbounded quotient.

## Bounded evidence

The regression suite exhaustively checked every encoded state at horizons
`h = 1..6`, including the exact fiber-size distributions:

```text
h=1: {2: 1}
h=2: {1: 1, 2: 1}
h=3: {1: 1, 2: 2}
h=4: {1: 3, 2: 2}
h=5: {1: 3, 2: 4}
h=6: {1: 6, 2: 5}
```

The facade test also exercises the same method through `import rule30`, while
the existing `experiments.rule30_successor` import path remains unchanged.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is an API and finite implementation check.
It does not prove the map for horizons above `h = 6`, establish an
infinite-horizon quotient, make same-horizon class transitions deterministic,
or say anything about center-column periodicity. The partition and map remain
exponential in the horizon and are intended for small bounded checks.

## Changed paths

- `experiments/rule30_successor.py` — added the checked cross-horizon map.
- `tests/test_rule30_successor.py` — exhaustive state and fiber regressions.
- `tests/test_rule30_facade.py` — facade compatibility regression.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documented the bounded seam.
- This report — evidence, classification, and explicit limits.
