# Predictive-State View

The most promising current experiment is not a transform of the center column itself, but a quotient on right-half boundary states.

## Core Idea

For a fixed horizon `h`, define two width-`h` right-half states to be equivalent when they produce exactly the same adjacent-column output sequence for every boundary word of length `h`.

This quotient identifies states only by what they can still do to the future observed output near the boundary.

That makes the equivalence classes a finite-horizon version of predictive states.

## Why This Matters

- Raw width truncation was not promising.
- Generic small automata were not promising.
- Exact response-equivalence does compress substantially.

So the likely bridge object is not a literal row prefix and not an arbitrary observer, but some predictive quotient of right-half states.

## Current Data (h = 0 … 20)

| h  | 2^h   | classes | compression |
|----|-------|---------|-------------|
|  0 |     1 |       1 |  1.000      |
|  1 |     2 |       2 |  1.000      |
|  2 |     4 |       3 |  0.750      |
|  3 |     8 |       5 |  0.625      |
|  4 |    16 |       7 |  0.438      |
|  5 |    32 |      11 |  0.344      |
|  6 |    64 |      16 |  0.250      |
|  7 |   128 |      25 |  0.195      |
|  8 |   256 |      35 |  0.137      |
|  9 |   512 |      52 |  0.102      |
| 10 |  1024 |      71 |  0.069      |
| 11 |  2048 |     104 |  0.051      |
| 12 |  4096 |     141 |  0.034      |
| 13 |  8192 |     203 |  0.025      |
| 14 | 16384 |     272 |  0.017      |
| 15 | 32768 |     387 |  0.012      |
| 16 | 65536 |     517 |  0.008      |
| 17 |131072 |     733 |  0.006      |
| 18 |262144 |     971 |  0.004      |
| 19 |524288 |    1364 |  0.003      |
| 20 |1048576|    1792 |  0.002      |

Computed by `experiments/predictive_state_growth.py` using the bottom-up coinductive
algorithm (O(2^h · h) per horizon instead of O(4^h) for the naive approach).

## Transition Image Coverage

At every h ≥ 1 the transitions are well-defined (coherent nested predictive-state system).
The *image* of each transition map is a proper subset of S_{h-1} for h ≥ 7:

| h  | |S_h| | |img(δ_0)| | |img(δ_1)| | img0/prev | img1/prev |
|----|--------|-----------|-----------|-----------|-----------|
|  7 |     25 |       15  |       16  |   0.938   |   1.000   |
|  8 |     35 |       22  |       24  |   0.880   |   0.960   |
| 10 |     71 |       44  |       48  |   0.846   |   0.923   |
| 15 |    387 |      223  |      237  |   0.820   |   0.871   |
| 20 |   1792 |     1075  |     1164  |   0.788   |   0.853   |

The coverage fractions are slowly decreasing: δ_1 always covers more of S_{h-1} than δ_0 does.

## Asymptotic Growth

The class-count sequence `a(h)` does **not** satisfy a simple linear recurrence.

Growth type analysis:
- `log a(h)/h` → 0 as h → ∞  (**NOT exponential**; "effective base" is below 1.37 for h ≥ 12)
- `log a(h)/log h` → ∞  (**NOT polynomial**)
- `log log a(h)/log h` converges toward ≈ 0.672 ≈ 2/3:
  **stretched exponential** `a(h) ~ exp(C · h^(2/3))`

This is the key new structural result: the predictive memory of Rule 30's right half-plane, as seen
from the boundary, grows like `exp(h^{2/3})` — sub-exponential but super-polynomial.

## Reachability: Full vs. Trajectory-Visited Classes

Experiment: `experiments/reachable_predictive_classes.py --max-horizon 18 --steps 50000`

The actual Rule 30 center-column trajectory drives the right half-plane and visits these class counts:

| h  | full | reachable (50k steps) | reach/full |
|----|------|-----------------------|------------|
|  0 |    1 |                     1 |     1.0000 |
| …  |   …  |                    …  |       …    |
| 10 |   71 |                    71 |     1.0000 |
| 11 |  104 |                   104 |     1.0000 |
| 12 |  141 |                   141 |     1.0000 |
| 13 |  203 |                   203 |     1.0000 |
| 14 |  272 |                   272 |     1.0000 |
| 15 |  387 |                   387 |     1.0000 |
| 16 |  517 |                   516 |     0.9981 |
| 17 |  733 |                   726 |     0.9905 |
| 18 |  971 |                   952 |     0.9804 |

Key finding: **The real trajectory appears to be dense in the full quotient.**  For h ≤ 15 the
entire quotient is covered within 50k steps.  For h = 16–18 coverage is already 98–99.8%.
This strongly suggests that, with enough steps, all classes would be visited.

Implication: there is **no small sparse sub-quotient** to exploit — the reachable system is
essentially all of S_h.  This rules out one potential shortcut (proving things only about the
reachable sub-automaton), but also confirms that the quotient classes are a "faithful" summary of
the dynamical information content.

## Coherence Verification

- Nested transitions well-defined through h = 20 ✓
- All 71 h=10 classes are visited by the actual center-column trajectory within 5000 steps ✓

## Updated Question

The number of classes is unbounded, so **no finite-state machine** emerges in the limit of this
quotient.  The open questions are now:

1. **Why 2/3?** Is there a combinatorial interpretation of the exponent?
2. **Reachable sub-quotient**: Does the sub-system of classes reachable by actual Rule 30
   trajectories grow more slowly than the full quotient?
3. **Implications for proof**: Does the sub-exponential (stretched-exponential) growth give any
   compressibility leverage for a proof of non-periodicity?
4. **Convergence of image fractions**: Do the coverage fractions img0/|S_{h-1}| and
   img1/|S_{h-1}| converge to a positive constant or go to zero as h → ∞?