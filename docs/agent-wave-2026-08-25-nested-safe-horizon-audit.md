# Nested safe-horizon audit

## Result

The finite response classes are coherent across wider right-half prefixes, but
only as a **horizon-consuming** predictive system. Exhaustive checks at response
depths `d=1..14` and widths `w=d..18` found:

- zero mismatches when a width-`w` class was compared with the class determined
  by its first `d` cells;
- zero class-conditioned conflicts in the transition from depth `d` before an
  update to depth `d-1` after it: every `(class, boundary bit)` has one lower-
  horizon target; and
- ambiguous right-extension-quantified same-depth `(class, boundary bit)`
  successors at every tested depth.

The same-depth failure is not only an artifact of enumerating unreachable raw
prefixes. On the exact single-seed center trajectory, conflicts occur at every
depth `1..14`, independently inside each of three disjoint 4,096-state intervals
(4,095 transitions each):
`[0,4096)`, `[7000,11096)`, and `[15000,19096)`.

Classification: **INCREMENTAL / EMPIRICAL bounded negative result**.

## Reproduction

From the project root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=. \
  python3 experiments/nested_safe_horizon_audit.py
```

The deterministic audit uses the first 20,001 bits of
`results/center-column-100000.txt`. It independently regenerates that prefix,
checks the inactive far-edge invariant for the exact right half, compares the
direct integer update with `rule30.integer_successor`, and prints the complete
depth table. Its terminal invariants are:

```text
center_reference_mismatches=0
safe_width_extension_mismatches=0
safe_lower_target_extension_mismatches=0
safe_nested_transition_conflict_keys=0
global_same_depth_deterministic_all=False
trajectory_same_depth_deterministic_all=False
first_global_same_depth_failure=1
first_trajectory_same_depth_failure=1
```

Finite class counts at depths 1 through 14 are
`2, 3, 5, 7, 11, 16, 25, 35, 52, 71, 104, 141, 203, 272`.

## Interpretation and limits

Increasing the finite width removes the artificial right-boundary objection
for response depth `d`: cells farther than `d` cannot enter the relevant light
cone. The audit directly groups lower-horizon targets by `(depth-d class,
boundary bit)` at every tested width and finds singleton target sets. The
coherent update therefore lands deterministically in the next smaller response
horizon.

Resetting to the original horizon requires one more right-half cell. The audit's
**right-extension-quantified same-depth relation** allows both values of that
newly exposed cell. This is not the same object as
`PredictivePartition.same_horizon_transition_relation()`, whose width-`d`
successor fixes the unrepresented outer cell to zero. The public zero-padded
relation is a subset and has no conflict at `d=1`; the extension-quantified
relation has conflicts at every tested depth.

This rejects a reusable same-depth deterministic-factor interpretation for the
tested quotient family and intervals. It does not rule out another encoding or
refinement, establish an asymptotic result, or prove anything about eventual
periodicity of the center column. The all-state enumeration stops at depth 14
and width 18; the trajectory check stops at 20,001 bits.
