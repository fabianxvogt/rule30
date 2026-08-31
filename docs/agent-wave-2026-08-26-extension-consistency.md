# Wave 10 Rule30 extension consistency

**Classification:** `DERIVED / INCREMENTAL_NEGATIVE_CONTROL`.

The definition is now explicit: `d=1` is one CA update, `k=1` is one fixed
right-extension bit (not a sibling count), and compatibility requires the
complete visible pre-update bit and post-update state to agree with the finite
zero-padded reference trajectory. One extension must match every time in each
contiguous block (`exists e: forall t`), not a separately chosen extension per
visit.

The exact 64-bit canonical center-column prefix was split into 32 training and
32 holdout steps. At the first step, extensions 0 and 1 produce visible
responses `(0,1)` and `(0,0)`, so the fixture has separating power. Training
selects only extension 0; extension 0 remains compatible throughout holdout,
while extension 1 does not. The production integer successor and independent
tuple oracle agree at every step.

This is a no-go for the intended Rule30 bridge: the unique surviving extension
is the known zero-padding convention, not recovered semi-infinite hidden
information. It establishes no superconstant lower bound, center-column
aperiodicity, eventual coverage, or infinite-trajectory theorem. Do not expand
to larger `k`, horizons, coverage runs, or a recurrence without a new
non-artifactual compatibility model.

Reproduce from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -S experiments/trajectory_extension_consistency.py
PYTHONDONTWRITEBYTECODE=1 python3 -S experiments/audit_trajectory_extension_consistency.py
```
