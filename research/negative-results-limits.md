# Negative results and limits

**Date:** 2026-08-25
**Classification:** INCREMENTAL / EMPIRICAL unless stated otherwise

This note consolidates three related finite investigations. They constrain a
coverage-based proof strategy, but none of them proves or disproves eventual
periodicity of the Rule 30 center column.

## 1. Proposition 13 is retracted

The original Proposition 13 argument claimed that a periodic input of period
`p` could visit at most `p` predictive classes, so full class coverage would
force `p >= |S_h|`. The error is that the finite driven machine need not return
to the same state after one input period. If `L` is the cycle length of the
`p`-step macro-map, the phase-lifted machine period is `L * p`, not `p`.

With `T` pre-cycle microsteps, the corrected finite count is at most
`T + L * p` (up to the fixed phase-alignment convention). The generic bound
`L <= 2^h` gives `T + 2^h * p`, which is no smaller than the raw-state
envelope `|S_h| <= 2^h` for `p >= 1`. Thus coverage, even if established for
every `h`, yields no period lower bound by this argument.

The smallest counterexample is `h=1`, constant input word `1`, and initial
state `0`: the input has period `1`, while the machine alternates with period
`2` and visits both finite classes. The nonconstant witness `h=6`, word `10`,
has machine period `8 = 4 * 2` and visits `7` of `16` classes. See the
[authoritative retraction](partial-results.md#proposition-13-retracted-period-lower-bound-from-class-coverage)
and the [period bug experiment](../experiments/verify_period_bug.py).

What survives is only the finite-state fact that periodic input produces an
eventually periodic phase-lifted machine trajectory. The counting shortcut is
not valid.

## 2. Periodic-input phase audits

The exact phase-augmented audits test finite raw-state machines driven by
chosen periodic boundary words. They do not generate, assume, or constrain
the Rule 30 center column.

- At `h=3`, boundary word `01`, initial state `0`, and input period `2`, the
  phase-lifted eventual cycle has period `8` and visits all `5` predictive
  classes. Sampling only at complete-word boundaries sees `4`; the
  intermediate phase supplies the fifth class. This falsifies the bounded
  repair “periodic driving must miss a class.” See the
  [phase-compatibility audit](../docs/agent-wave-2026-08-25-phase-coverage-compatibility.md).
- The independent audit checked all initial states, `h=0..7`, and primitive
  word lengths `1..4` (`5,610` cases), and corrected a mid-word phase-alignment
  error in pre-cycle counting. At `h=4`, extending the exact sweep through
  primitive word length `5` and all `16` initial states gives `832` cases; the
  best eventual coverage remains `6/7` (per-length maxima `1/7`, `6/7`,
  `6/7`, `5/7`, `6/7`). See the [h=4 envelope](../docs/agent-wave-2026-08-25-h4-phase-coverage.md)
  and the [macro-cycle report](../docs/agent-wave-2026-08-25-periodic-input-coverage.md).

These results are finite compatibility and counterexample evidence. The
`h >= 4` coverage shortfall is an envelope observation, not an asymptotic
bound; the `h=3` witness prevents promoting “periodic inputs miss a class” to
a general finite rule.

## 3. Raw sibling-fiber evidence through `h=12`

The independent raw tuple-state audit exhaustively rebuilds the finite
response signatures and the maps `rho_h`, `tau_0`, and `tau_1` through the
explicit cap `h=12` (at most `2^12 = 4096` raw states). At `h=12`, it finds
`|S_12| = 141`, with `67` singleton and `37` doubleton truncation fibers.
Across the checked envelope:

- every truncation fiber has size at most two;
- for `h >= 2`, each doubleton sibling pair has the same leading bit;
- even `h` siblings share neither child, while odd `h >= 3` siblings share
  exactly one child; and
- the `h=1` row is a genuine degenerate exception: both children collapse to
  the unique `S_0` class and the two siblings have opposite leading bits.

The commuting-square and lower-fiber checks also hold throughout this finite
envelope. These observations describe a bounded zero-padded quotient; they do
not establish a parity theorem for larger `h`, an infinite-horizon quotient,
center-column coverage, or any periodicity result. The [raw audit report](../docs/agent-wave-2026-08-25-raw-sibling-fiber-audit.md)
contains the exact table and reproduction command.

## Current limit of the strategy

The coverage data through the current tested horizons remains interesting as a
dynamical property, but it is now logically separate from Proposition 13.
Phase-lift behavior removes the proposed counting obstruction, and the
sibling-fiber pattern supplies finite quotient structure without supplying a
one-column-to-two-column bridge. The established two-adjacent-column
left-reconstruction argument therefore remains the relevant boundary: no
result in these audits adds a second eventually periodic column or makes a
claim about the center column itself.

For the underlying formal statements and the open gap, see
[`partial-results.md`](partial-results.md) and
[`proof-attempts.md`](proof-attempts.md).
