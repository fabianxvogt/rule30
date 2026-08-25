# Raw response-signature audit of sibling-fiber parity

## Result

**No implementation-coupling discrepancy found.** The checked-in audit
reconstructs the finite response-equivalence classes from raw tuple-state
simulation, then derives `rho_h` by dropping the rightmost state bit and
`tau_0`, `tau_1` by applying one raw Rule 30 update before dropping that bit.
It does not call the package's nested-map, fiber, or partition helpers.

The explicit hard cap is now `h = 13`; the run enumerates at most `2^13 = 8192`
raw states. A preflight at the new cap completed in 55.63 seconds with a peak
resident set size of 252,231,680 bytes on the audit machine. Every checked
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
| 13 | 203 | 79 | 62 | 62 | 31 | 31 | 0 | 0 | 31 | 31 |

Here `n1`/`n2` count singleton/doubleton `rho` fibers, and `coll0`/`coll1`
count redundant entries in `(rho, tau_0)` / `(rho, tau_1)`.

The h=13 row shows no qualitative parity change: as at the earlier odd
horizons, every doubleton sibling pair shares exactly one child, with 31 pairs
sharing `tau_0` and 31 sharing `tau_1`; no pair shares both or neither, and the
two collision counts match those directions. The same-leading-bit condition
also continues to hold for all 62 doubleton pairs.

An independent raw cross-check also compared each doubleton pair's complete
response signatures over all `2^h` boundary words. For every checked horizon
`1 <= h <= 13`, each pair differed on exactly
`2^(floor(h/2) + 1)` words. Thus at `h = 13`, all 62 pairs differed on 128 of
8192 words; the disagreements occupy both first-bit halves at even horizons
and one first-bit half at odd horizons. This is an additional finite empirical
observation, not an automated regression or a parity theorem.

## Exact cross-check and limits

For all 31 encoded states at `h = 0..4`, the raw signatures matched the tuple
reference in `experiments/right_half_response_classes.py`; the regression keeps
this explicit cross-check. A separate focused regression also compares the
compact raw signatures with the direct tuple-state signatures through `h = 5`.
The compact h=13 signatures preserve lexicographic
boundary-word order, while the package's integer helper uses a different order.
Comparing flattened arrays without aligning words therefore remains an invalid
cross-check and previously produced a false alarm at `h=2`.

Reproduce the audit with:

```text
PYTHONDONTWRITEBYTECODE=1 python3 experiments/sibling_fiber_parity.py --max-horizon 13
```

The result is **EMPIRICAL / INCREMENTAL** and exact only for the finite envelope
`0 <= h <= 13`. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
