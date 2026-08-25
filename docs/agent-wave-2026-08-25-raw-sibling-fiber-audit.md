# Raw response-signature audit of sibling-fiber parity

## Result

**No implementation-coupling discrepancy found.** An independent audit
reconstructed the finite response-equivalence classes from raw tuple-state
simulation, then derived `rho_h` by dropping the rightmost state bit and
`tau_0`, `tau_1` by applying one raw Rule 30 update before dropping that bit.
The main audit did not call the package's nested-map, fiber, or partition
helpers.

The hard cap was `h = 11`. Every checked truncation fiber had size at most two;
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

Here `n1`/`n2` count singleton/doubleton `rho` fibers, and `coll0`/`coll1`
count redundant entries in `(rho, tau_0)` / `(rho, tau_1)`.

## Exact cross-check and limits

For all 31 encoded states at `h = 0..4`, the raw signatures matched the tuple
reference in `experiments/right_half_response_classes.py`. The same traces also
matched the package's single-word `response_trace` primitive when compared by
boundary word. Comparing flattened signature arrays without aligning boundary
words produced one false alarm at `h=2`: the two implementations enumerate
boundary words in different orders. This was an audit-harness ordering issue,
not a Rule 30 or package discrepancy.

The result is **EMPIRICAL / INCREMENTAL** and exact only for the finite envelope
`0 <= h <= 11`. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
