# AI-owned project documentation

Use this folder for concise, reviewable notes maintained by coding agents: verified setup, architecture, validation commands, and bounded cleanup plans.

The project README and any document marked `human-owned` remain authoritative. Do not overwrite human-owned material or make unsupported claims.

Never store credentials, private data, generated output, logs, datasets, or build artifacts here. Preserve unrelated local work and keep each change focused.

## Negative-results entry point

The concise cross-report note
[`research/negative-results-limits.md`](../research/negative-results-limits.md)
is the current entry point for the Proposition 13 retraction, periodic-input
phase audits, and raw sibling-fiber evidence through `h=13`. The detailed
reports below remain provenance records; none makes a center-column or
infinite-horizon claim.

## Verified finite-width check

Run `python3 experiments/bitwise_successor_check.py` from the repository root;
use `--max-horizon 13` to reproduce the latest bounded check.
It exhaustively checks tuple/integer round-trips and both boundary transitions for
finite widths `h=0..13` in the latest record, with bit 0 representing the leftmost,
boundary-adjacent cell. This is an implementation check only; it does not prove
the successor identity at widths above `h=13`, infinite Rule 30 behavior, or
any center-column periodicity claim.

## Repository-local package facade

The bounded transition and predictive-partition helpers are also available from
the documented `rule30` facade:

```python
from rule30 import predictive_partition, response_signature
```

The integer transition and observation helpers validate their finite-domain
contract before doing work, including when a boundary iterable is empty. See
[`agent-wave-2026-08-25-api-contract-guardrails.md`](agent-wave-2026-08-25-api-contract-guardrails.md)
for the bounded regression and limits.

See [`agent-wave-2026-08-25-package-facade.md`](agent-wave-2026-08-25-package-facade.md)
for the compatibility checks and explicit finite-horizon limits. The facade
does not include the exploratory scripts or generated results. The
`PredictivePartition.right_truncation_map` method exposes the adjacent-horizon
projection described in the [cross-horizon report](agent-wave-2026-08-25-cross-horizon-map.md).
`class_members` and `right_truncation_fibers` provide immutable class members
and source-class fibers for the same finite partitions, with class-ID and
adjacent-horizon validation. `nested_transition_map` provides the separately
checked boundary-driven map from `S_h` to `S_{h-1}` after one update and right
truncation; it does not assert same-horizon determinism or an infinite
quotient. `same_horizon_transition_relation` provides the missing finite
set-valued same-horizon relation, preserving the observed nondeterminism rather
than presenting a false transition function. `PredictivePartition.class_trace`
records one finite class ID before each supplied boundary-driven update, so
`set(partition.class_trace(...))` is a bounded coverage calculation only. The
`PredictivePartition.coverage_profile(state, boundary_bits)` method, or the
equivalent `rule30.coverage_profile(partition, state, boundary_bits)` function,
returns class-ID-indexed first-visit steps for the initial state and each state
after a supplied boundary bit. It is a finite profile of the supplied word;
it does not generate or load center-column data and makes no eventual-coverage
or infinite-horizon claim. The [coverage-profile report](agent-wave-2026-08-25-coverage-profile.md)
records its bounded evidence and limits. The
[same-horizon relation report](agent-wave-2026-08-25-same-horizon-relation.md)
records its bounded evidence and limits. The partition builder uses a finite
recursive lower-horizon key while
still enumerating every bounded state; it remains an exponential small-check
tool, not an infinite-horizon construction.

## Periodic boundary macro-cycles

[`agent-wave-2026-08-25-periodic-input-coverage.md`](agent-wave-2026-08-25-periodic-input-coverage.md)
documents the exact finite experiment in
`experiments/periodic_input_coverage.py`. It computes transient and eventual
cycles for primitive periodic boundary words and counts both macro-boundary
classes and phase-lifted machine-cycle classes. The default h=6, periods 1..3
run checks 640 finite observations; the h=6 word `10` has machine period 8 and
visits 7 of 16 phase-lifted classes. This is bounded implementation evidence,
not a center-column or infinite-horizon result. An independent phase-augmented
audit found the minimal h=1, word `1` period-lift witness and corrected a
mid-word phase-alignment error in pre-cycle class counting; see the linked
report for the bounded check envelope.

The [phase-coverage compatibility report](agent-wave-2026-08-25-phase-coverage-compatibility.md)
records a bounded nonconstant periodic-driver witness whose phase-lifted cycle
visits every class at `h=3`; it is an incremental finite consistency result,
not a center-column claim.

The [h=4 phase-coverage report](agent-wave-2026-08-25-h4-phase-coverage.md)
records the documented extension through primitive word length `5` and all
initial states. The best eventual phase-lifted coverage remains `6/7` across
`832` observations; this is a bounded envelope result with a focused
regression, not an asymptotic or center-column claim.

The [raw sibling-fiber audit report](agent-wave-2026-08-25-raw-sibling-fiber-audit.md)
records an exact raw tuple-state check of the finite `rho_h` fibers and
`tau_0`/`tau_1` child maps through `h = 13`. It empirically checks the even/odd
child-sharing pattern in that envelope and records the degenerate `h = 1`
exception. The script has an explicit raw-state cap and makes no
infinite-horizon, center-column, or eventual-coverage claim.
