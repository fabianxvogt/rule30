# Raw response-signature audit of sibling-fiber parity

## Result

**No implementation-coupling discrepancy found.** The checked-in audit
reconstructs the finite response-equivalence classes from raw tuple-state
simulation, then derives `rho_h` by dropping the rightmost state bit and
`tau_0`, `tau_1` by applying one raw Rule 30 update before dropping that bit.
It does not call the package's nested-map, fiber, or partition helpers.

The explicit hard cap is now `h = 12`; the run enumerates at most `2^12 = 4096`
raw states and completed in 13.25 seconds in the recorded run. Every checked
truncation fiber had size at most two;
the commuting squares, same-leading-bit sibling check, and parity assertions
also held throughout the bound.

| h | `|S_h|` | n1 | n2 | same leading | share `tau_0` | share `tau_1` | share both | share neither | coll0 | coll1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 1 |
| 2 | 3 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| 3 | 5 | 1 | 2 | 2 | 1 | 1 | 0 | 0 | 1 | 1 |
| 4 | 7 | 3 | 2 | 2 | 0 | 0 | 0 | 2 | 0 | 0 |
| 5 | 11 | 3 | 4 | 4 | 1 | 3 | 0 | 0 | 1 | 3 |
| 6 | 16 | 6 | 5 | 5 | 0 | 0 | 0 | 5 | 0 | 0 |
| 7 | 25 | 7 | 9 | 9 | 5 | 4 | 0 | 0 | 5 | 4 |
| 8 | 35 | 15 | 10 | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| 9 | 52 | 18 | 17 | 17 | 8 | 9 | 0 | 0 | 8 | 9 |
| 10 | 71 | 33 | 19 | 19 | 0 | 0 | 0 | 19 | 0 | 0 |
| 11 | 104 | 38 | 33 | 33 | 15 | 18 | 0 | 0 | 15 | 18 |
| 12 | 141 | 67 | 37 | 37 | 0 | 0 | 0 | 37 | 0 | 0 |

Here `n1`/`n2` count singleton/doubleton `rho` fibers, and `coll0`/`coll1`
count redundant entries in `(rho, tau_0)` / `(rho, tau_1)`.

## Exact cross-check and limits

For all 31 encoded states at `h = 0..4`, the raw signatures matched the tuple
reference in `experiments/right_half_response_classes.py`; the regression keeps
this explicit cross-check. The compact h=12 signatures preserve lexicographic
boundary-word order, while the package's integer helper uses a different order.
Comparing flattened arrays without aligning words therefore remains an invalid
cross-check and previously produced a false alarm at `h=2`.

Reproduce the audit with:

```text
PYTHONDONTWRITEBYTECODE=1 python3 experiments/sibling_fiber_parity.py --max-horizon 12
```

The result is **EMPIRICAL / INCREMENTAL** and exact only for the finite envelope
`0 <= h <= 12`. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
