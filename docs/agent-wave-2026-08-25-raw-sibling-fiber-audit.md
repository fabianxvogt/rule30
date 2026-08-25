# Raw response-signature audit of sibling-fiber parity

## Result

**No implementation-coupling discrepancy found.** The checked-in audit
reconstructs the finite response-equivalence classes from raw tuple-state
simulation, then derives `rho_h` by dropping the rightmost state bit and
`tau_0`, `tau_1` by applying one raw Rule 30 update before dropping that bit.
It does not call the package's nested-map, fiber, or partition helpers.

The explicit hard cap is now `h = 13`; at any one source horizon the run
enumerates at most `2^13 = 8192` raw states. A preflight at the new cap completed in 55.63 seconds with a peak
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

A finite regression now asserts the compact raw audit's complete-signature
distance for every reported doubleton pair. For every checked horizon
`1 <= h <= 13`, each pair differs on exactly
`2^(floor(h/2) + 1)` words. Thus at `h = 13`, all 62 pairs differ on 128 of
8192 words; the disagreements occupy both first-bit halves at even horizons
and one first-bit half at odd horizons. The regression consumes the
`AuditResult` produced by this same raw implementation; it is not an
independent direct-signature recomputation at every horizon, and it remains a
finite empirical observation rather than a parity theorem.

## Bounded review of the distance observation

Let `d_h(c, c')` be the Hamming distance between the complete raw response
signatures of a doubleton sibling pair at horizon `h`. The signature
construction splits into two blocks according to the first boundary bit. When
the siblings have the same leading bit, their common first output contributes
no disagreement, so the raw construction gives the finite decomposition

```text
d_h(c, c') = d_{h-1}(tau_0(c), tau_0(c'))
           + d_{h-1}(tau_1(c), tau_1(c')).
```

The already-recorded sibling audit then supplies a conditional explanation of
the observed sequence. At even `h`, both child pairs are distinct members of
the same lower `rho`-fiber, so both terms are lower sibling distances. At odd
`h >= 3`, exactly one child is shared and the other distinct child pair is a
lower sibling pair, so one term is zero. With the explicit `h=1` base distance
`d_1 = 2`, these finite recurrences yield
`d_h = 2^(floor(h/2) + 1)` for the horizons already checked.

This is a proof sketch of why the finite table is compatible with the existing
child-sharing data, not a proof that the child-sharing premises continue past
`h=13`. No counterexample appears in the checked envelope, and the argument
does not provide a center-column bridge or an infinite-horizon conclusion.

The follow-up pairwise check is now implemented in the same bounded raw audit.
It records each doubleton pair's full distance and both child distances, while
preserving the `h=1` leading-bit exception explicitly. See the
[pairwise child-distance report](agent-wave-2026-08-25-child-distance-decomposition.md)
for the exact table and reproduction command.

## Exact cross-check and limits

For all 31 encoded states at `h = 0..4`, the raw signatures matched the tuple
reference in `experiments/right_half_response_classes.py`; the regression keeps
this explicit cross-check. A separate focused regression also compares the
compact raw signatures with the direct tuple-state signatures through `h = 5`.
The distance-law assertion through `h = 13` is intentionally a consistency
check over the compact audit output, not evidence of a second implementation
of all h=13 signatures.
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
