# Finite class-coverage profile — 2026-08-25

## Result

Promoted the dependency-free finite coverage core of
`experiments/fast_class_coverage2.py` into the bounded predictive-partition
API. `PredictivePartition.coverage_profile(state, boundary_bits)` returns a
tuple indexed by finite class ID. Each entry is the first step at which that
class is observed, or `None` when the supplied finite trajectory does not visit
it. Step 0 is the initial state; each supplied boundary bit advances once and
then contributes the next observed state. A functional facade,
`rule30.coverage_profile(partition, state, boundary_bits)`, exposes the same
behavior.

The API accepts boundary bits directly and performs no file I/O, center-column
generation, or external-package import. The experiment's real-trajectory
coverage result remains an input-dependent empirical result and is not moved
into the package as a claim.

## Bounded evidence

The unit suite exhaustively compares both API forms with an independent
tuple-state trajectory reference for every encoded state at horizons
`h = 0..6` and every boundary word of lengths `0..4`. It also checks initial
state inclusion, empty words, invalid states, and one-shot iterable
consumption. The existing facade, partition, transition, and finite-width
successor checks remain covered.

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.test_rule30_successor tests.test_rule30_facade
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked

git diff --check
```

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a finite API and implementation check. It
does not prove coverage for any horizon beyond the tested bounds, assert that
the Rule 30 center column visits every class, establish an infinite-horizon
quotient, or address center-column periodicity. The partition and coverage
profile remain bounded computations over finite supplied words.

## Changed paths

- `experiments/rule30_successor.py` — added the method and functional helper.
- `rule30/__init__.py` — exported the functional facade.
- `tests/test_rule30_successor.py`, `tests/test_rule30_facade.py` — added exhaustive bounded regressions.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documented the API and limits.
- This report — evidence, classification, and explicit non-claims.
