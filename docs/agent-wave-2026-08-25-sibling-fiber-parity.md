# Sibling-fiber parity and cross-horizon maps — 2026-08-25

## Result

Extended `experiments/sibling_fiber_parity.py` by exactly one bounded step. It
now provides a dependency-free exact check of the finite predictive partitions
`S_h` through a hard-coded maximum horizon of `h = 11`. It computes the
right-truncation map `rho_h`, the two nested child
maps `tau_0` and `tau_1`, their commuting square across adjacent horizons, and
the full doubleton-fiber sibling statistics.

Before extending the cap, a preflight build of the h=10 and h=11 partitions
completed in 0.04 seconds wall time with 10.9 MiB maximum resident memory on
the audit machine; h=11 contains 2,048 encoded states and 104 classes. This is
an empirical resource observation, not a portability guarantee.

The finite check found the following bounded pattern:

| h | `|S_h|` | singleton fibers | doubleton fibers | share `tau_0` | share `tau_1` | share both | share neither |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 0 | 1 | 1 | 1 | 1 | 0 |
| 2 | 3 | 1 | 1 | 0 | 0 | 0 | 1 |
| 3 | 5 | 1 | 2 | 1 | 1 | 0 | 0 |
| 4 | 7 | 3 | 2 | 0 | 0 | 0 | 2 |
| 5 | 11 | 3 | 4 | 1 | 3 | 0 | 0 |
| 6 | 16 | 6 | 5 | 0 | 0 | 0 | 5 |
| 7 | 25 | 7 | 9 | 5 | 4 | 0 | 0 |
| 8 | 35 | 15 | 10 | 0 | 0 | 0 | 10 |
| 9 | 52 | 18 | 17 | 8 | 9 | 0 | 0 |
| 10 | 71 | 33 | 19 | 0 | 0 | 0 | 19 |
| 11 | 104 | 38 | 33 | 15 | 18 | 0 | 0 |

For every checked `2 <= h <= 11`, all `rho_h` fibers are singletons or
doubletons, and every doubleton sibling pair has the same leading bit. For
every checked `3 <= h <= 11`:

- even `h` siblings share neither child;
- odd `h` siblings share exactly one child;
- the sibling children remain in the same lower `rho`-fiber for each boundary
  bit; and
- both maps `c -> (rho_h(c), tau_b(c))` have collisions at odd `h`, while both
  are injective at even `h`.

The `h = 1` row is an explicit degenerate counterexample to an unqualified
odd-horizon statement: the two `S_1` classes have opposite leading bits, and
both children collapse to the unique `S_0` class. This corrects the indexing of
the older observations: the same-leading-bit sibling statement starts at
`h >= 2`, and the “share exactly one child” statement starts at `h >= 3`.

## Evidence and limits

**EMPIRICAL / bounded.** The script exhaustively enumerates all encoded states
in every partition `S_h` for `0 <= h <= 11`, checks both boundary bits, and
uses no third-party dependencies. The regression table is exact for this
finite envelope. The commuting-square identity is checked computationally for
each available adjacent square.

This does not prove the parity pattern for `h > 11`, establish an
infinite-horizon quotient, imply center-column coverage, or say anything about
eventual periodicity. The computation concerns the repository’s finite,
zero-padded response system only.

Reproduce with:

```text
python3 experiments/sibling_fiber_parity.py --max-horizon 11
python3 -m unittest tests/test_sibling_fiber_parity.py
```

## Classification

**INCREMENTAL / EMPIRICAL.** This is a reproducible finite-pattern check and a
boundary correction to the older observation wording. Every result here is
empirical and bounded; no infinite result or novelty claim is made.
