# h=4 phase-lifted coverage envelope through period 5 — 2026-08-25

## Bounded probe

Following the documented next test, the existing phase-lifted coverage
machinery was run at `h = 4` for every primitive binary boundary word of
length `1..5` and every one of the `2^4 = 16` initial raw states. The exact
phase-augmented walk stops at the first repeated `(raw_state, input_phase)`
pair and counts predictive classes on that eventual cycle.

There are `2 + 2 + 6 + 12 + 30 = 52` primitive words, for `832` finite
observations. The current `6/7` envelope was rerun with lengths `1..4` for
comparison (`22` words, `352` observations).

## Result

The maximum eventual phase-lifted coverage remains **`6/7`**. Adding primitive
length-5 words produces no improvement over the current envelope.

| Boundary length | Best eventual coverage |
|---:|---:|
| 1 | 1/7 |
| 2 | 6/7 |
| 3 | 6/7 |
| 4 | 5/7 |
| 5 | 6/7 |

A canonical new length-5 witness is boundary word `00001`, initial state `0`:
it has no transient, macro-cycle length `3`, phase-lifted period `15`, and
eventual classes `{0, 1, 2, 3, 4, 5}`. Class `6` remains absent. Fifteen of
the thirty primitive length-5 words attain `6/7`:
`00001`, `00010`, `00011`, `00100`, `00110`, `01000`, `01100`, `01111`,
`10000`, `10001`, `10111`, `11000`, `11011`, `11101`, and `11110`.

An independent direct phase-walk implementation agreed with the existing
machinery on all `832` observations and the same `6/7` maximum. The combined
comparison run completed in `0.07s` wall time on the development machine.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is an exact, regression-tested finite
envelope result. It does not establish coverage failure at larger horizons or
periods, prove an asymptotic bound, or make a claim about the Rule 30 center
column or an infinite-horizon quotient.

The regression is in `tests/test_periodic_input_coverage.py` and checks the
`832`-case count, the per-length maxima, and the canonical length-5 witness.
