# Macro-cycle-aware periodic-input coverage — 2026-08-25

## Scope

Added `experiments/periodic_input_coverage.py`, a dependency-free finite
experiment that applies a periodic boundary word as an exact raw-state map.
For each selected initial state it detects the exact macro-transient and
eventual macro-cycle, reports the induced machine period, and separates
predictive classes seen during the pre-cycle phases from classes on every phase
of the eventual machine cycle. Macro-boundary class coverage is also retained
separately. The default CLI envelope is deliberately bounded at `h=6` and
primitive word periods `1..3`.

The experiment does not generate the Rule 30 center column and does not infer
that a periodic center column exists. It tests finite periodic driving as a
separate falsifiable input family.

## Reproduction

```text
python3 experiments/periodic_input_coverage.py --horizon 6 --max-period 3
python3 -m unittest -q tests.test_periodic_input_coverage
```

The JSON payload records the bounds, number of primitive words and initial
states, total predictive classes, and every finite observation. Each observation
includes macro-transient length, macro-cycle length, machine period, separate
pre-cycle/eventual-machine-cycle class counts, and the macro-boundary cycle
class count.

## Independent audit — 2026-08-25

An independent phase-augmented state walk checked the raw cycle decomposition
for all horizons `h=0..7`, all primitive binary words of lengths `1..4`, and
all initial raw states: 5,610 bounded cases. It found and corrected a phase
alignment edge case in `precycle_class_count`: a trajectory can enter its
eventual phase cycle between two macro boundaries. The implementation now
classifies pre-cycle and cycle samples from `(raw_state, input_phase)` directly.

The smallest counterexample to the retracted Proposition 13 claim is even
smaller than the historical `h=6`, word `10` example: at `h=1`, constant input
word `1`, and initial state `0`, the state alternates `0,1,0,...`; the input
period is `1`, while the phase-lifted machine period is `2` and both finite
classes are visited. The `h=6`, word `10` case remains a useful nonconstant
period-2 witness, visiting 7 of 16 classes.

## Classification and limits

`INCREMENTAL / EMPIRICAL`: exact finite raw-state and phase-lifted cycle
detection only. It does not prove aperiodicity, eventual coverage failure
beyond the supplied bounds, center-column behavior, or an infinite-horizon
quotient. Larger horizons and periods remain intentionally deferred until the
bounded result and runtime are reviewed.
