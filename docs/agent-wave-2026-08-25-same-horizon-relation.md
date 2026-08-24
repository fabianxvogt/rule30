# Finite same-horizon transition relation — 2026-08-25

## Result

Added `PredictivePartition.same_horizon_transition_relation()` to the bounded
Rule 30 API. The result is indexed as
`relation[source_class_id][boundary_bit]`; each entry is an immutable
`frozenset` of target class IDs obtained by applying that boundary bit to every
raw state in the source class and classifying the resulting state in the same
finite partition.

This is the safe API boundary for same-horizon dynamics. A finite predictive
class does not always determine one same-horizon successor class under a fixed
boundary bit, so the method exposes a set-valued relation rather than claiming
a deterministic quotient transition.

## Bounded evidence

The regression suite exhaustively checks every encoded state, source class, and
boundary bit for horizons `h = 0..6` against an independent tuple-state Rule 30
successor. It also verifies that every returned target set is non-empty and
immutable, and records the number of non-singleton `(class, boundary)` pairs:

```text
h=0..6: 0, 0, 1, 2, 3, 8, 8
```

The facade regression exercises the method through `import rule30`. Existing
transition, recursive-partition, cross-horizon, fiber, nested-transition, and
class-trace tests remain in place. `git diff --check` passes.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a finite, dependency-free API and
implementation check. It does not prove the relation beyond `h = 6`, establish
an infinite-horizon quotient, turn same-horizon dynamics into a deterministic
automaton, prove a general bound on target-set sizes, or make any claim about
center-column periodicity. The partition and relation remain exponential in
the horizon and are intended for small bounded checks.

## Changed paths

- `experiments/rule30_successor.py` — added the finite relation method.
- `tests/test_rule30_successor.py` — added exhaustive bounded relation checks.
- `tests/test_rule30_facade.py` — added facade coverage.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documented the slice and limits.
- This report — evidence, classification, and explicit non-claims.
