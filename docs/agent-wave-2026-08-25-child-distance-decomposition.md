# Bounded pairwise child-distance decomposition

## Result

The raw sibling-fiber audit now compares every doubleton pair's complete
signature distance with the distances of its two raw children. The computation
uses the same tuple-state Rule 30 update and explicit `h <= 13` cap as the
existing audit; it does not import the repository's predictive-partition
helpers.

| source h | doubleton pairs | full distance | child-distance patterns |
|---:|---:|---:|---|
| 1 | 1 | 2 | `(0, 0)`; leading bits differ |
| 2 | 1 | 4 | `(2, 2)` |
| 3 | 2 | 4 | `(4, 0)`, `(0, 4)` |
| 4 | 2 | 8 | `(4, 4)` |
| 5 | 4 | 8 | `(8, 0)`, `(0, 8)` |
| 6 | 5 | 16 | `(8, 8)` |
| 7 | 9 | 16 | `(16, 0)`, `(0, 16)` |
| 8 | 10 | 32 | `(16, 16)` |
| 9 | 17 | 32 | `(32, 0)`, `(0, 32)` |
| 10 | 19 | 64 | `(32, 32)` |
| 11 | 33 | 64 | `(64, 0)`, `(0, 64)` |
| 12 | 37 | 128 | `(64, 64)` |
| 13 | 62 | 128 | `(128, 0)`, `(0, 128)` |

For `h >= 2`, all 201 checked pairs have equal leading bits and satisfy the
exact finite equality

```text
d_h(c, c') = d_{h-1}(tau_0(c), tau_0(c'))
           + d_{h-1}(tau_1(c), tau_1(c')).
```

Here each `d_{h-1}` is the Hamming distance between the complete raw
signatures of the corresponding two raw child states; `tau_0` and `tau_1`
identify their finite child classes. The equality is asserted only for the
finite raw states and horizons in this audit.

The `h = 1` pair is intentionally reported as an exception: its leading bits
differ, so the first observed output contributes two disagreements across the
two response blocks and the child sum is zero. This is a finite boundary case,
not a failure of the equal-leading-bit decomposition.

At `h = 13`, the exact report contains all 62 doubleton pairs. Thirty-one
have child distances `(128, 0)` and thirty-one have `(0, 128)`; no pair is
omitted or sampled.

## Reproduction and verification

Run from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 experiments/sibling_fiber_parity.py \
  --max-horizon 13 --report-distances
```

The focused regression in
`tests/test_sibling_fiber_parity.py` checks the complete bounded table,
all 202 pair records, the explicit `h = 1` exception, and the `h = 13`
distance split (31 pairs in each direction). It also recomputes the direct
tuple-state signatures for every reported pair and both children through
`h = 5`, using a separate direct tuple-state code path to cross-check the
compact raw-signature distance path at the lower envelope. The audit is exact
only for raw finite horizons through 13;
it makes no asymptotic, infinite-horizon, center-column, or periodicity claim.

Classification: **EMPIRICAL / INCREMENTAL**, bounded.
