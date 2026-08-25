# Eventual phase-cycle coverage remains compatible with periodic driving — 2026-08-25

## Question

After the Proposition 13 retraction, does the phase-lift correction itself make
full predictive-class coverage incompatible with a periodic boundary word at a
small finite horizon?

## Bounded probe

The exact phase-augmented walk was checked for every initial raw state, every
horizon `h = 0..7`, and every primitive binary word of length at most `4`.
The walk stops at the first repeated `(raw_state, input_phase)` pair. It records
classes on the eventual phase cycle, not only at complete-word boundaries.

This is a finite driven-system check. It does not generate or assume the Rule 30
center column.

The witness is reproduced by:

```text
python3 -m unittest -q tests.test_periodic_input_coverage
```

The envelope uses `coverage_envelope(h, 4)` for each `h = 0..7`.

## Result

A compact nonconstant phase-alignment witness is:

```text
horizon                 3
predictive classes      5
boundary word           01  (primitive period p = 2)
initial raw state       0
macro-cycle length      4
phase-lifted period     8 = 4 × 2
macro-boundary classes  4  -> {0, 1, 2, 4}
eventual cycle classes  5  -> {0, 1, 2, 3, 4}
```

There is no transient in this witness. The intermediate phase of the periodic
word supplies class `3`, which is absent from the macro-boundary samples. Thus
an eventually periodic finite driver can visit every predictive class on its
eventual phase-lifted cycle at this scale.

Across the full bounded envelope, eventual full coverage occurred for `h = 0,
1, 2, 3`; no word of length at most `4` achieved it for `h = 4, 5, 6, 7`. The
largest eventual cycle class counts at those latter horizons were respectively
`6/7`, `9/11`, `10/16`, and `16/25`.

## Classification and limits

`INCREMENTAL / EMPIRICAL`: the witness is an exact finite-state computation and
is regression-tested in `tests/test_periodic_input_coverage.py`. It falsifies
only the bounded repair “periodic driving must miss at least one class”; it does
not restore Proposition 13, establish an asymptotic pattern, or make any claim
about the Rule 30 center column. The negative results for `h >= 4` are also only
an envelope limit, not a theorem.

## Next bounded test

At `h = 4`, extend the exact sweep to primitive word lengths at most `5` and
all initial states. Compare the best eventual-cycle coverage with the current
`6/7` bound before considering a larger horizon.
