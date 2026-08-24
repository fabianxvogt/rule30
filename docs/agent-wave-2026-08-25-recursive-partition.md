# Recursive finite predictive partition — 2026-08-25

## Result

The repository-local `predictive_partition(horizon)` API now builds its finite
classes recursively. At width `h`, each encoded state is keyed by its observed
lowest bit and the two classes reached after one update with boundary bits `0`
and `1`, after dropping the highest encoded bit and consulting the already-built
partition at `h - 1`.

This promotes the bounded quotient construction used by
`experiments/predictive_state_growth.py` into the reusable API while preserving
the existing `PredictivePartition` surface and experiment import path. The
construction still enumerates every finite state at every level; it avoids only
the repeated enumeration of all boundary words.

## Bounded evidence

The unit suite exhaustively checks every encoded state and class membership for
the known class-count sequence through `h = 11`:

```text
1, 2, 3, 5, 7, 11, 16, 25, 35, 52, 71, 104
```

It also compares the recursive partition with the direct finite response
signatures for every state pair through `h = 6`, and the existing exhaustive
transition, truncation, fiber, and facade checks remain green. The finite
integer implementation checker remains independently green through `h = 13`:

```text
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked
```

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a finite reproducibility and package
implementation improvement. It does not prove the recorded class counts above
`h = 11`, establish an infinite-horizon quotient, make same-horizon class
transitions deterministic, or make any claim about center-column periodicity.
The state enumeration remains exponential in the horizon and is intended for
small bounded checks.

## Changed paths

- `experiments/rule30_successor.py` — builds the finite partition from recursive lower-horizon class keys.
- `tests/test_rule30_successor.py` — exhaustively checks state coverage, class membership, and the known growth table through `h = 11`.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documents the bounded recursive construction and its limits.
- This report — evidence, classification, and explicit limits.
