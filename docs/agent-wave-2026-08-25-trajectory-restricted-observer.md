# Trajectory-restricted observer probe (2026-08-25)

Classification: **INCREMENTAL, EMPIRICAL, bounded**. This probe does not
prove unbounded observer memory or center-column non-periodicity.

## Exact finite question

For width `h`, let `q_h` be the existing finite predictive quotient: two
encoded right-half states are equivalent when the adjacent-column response is
identical for every binary boundary word of length `h`. For a center prefix
`c[0:N]`, define the exact driven strip by

```
s_h(0) = 0^h
s_h(t+1) = F_{c[t]}(s_h(t))
R_{h,N} = { q_h(s_h(t)) : 0 <= t < N }
```

The primary trajectory-restricted count is `|R_{h,N}|`; the baseline is the
full finite quotient count `|S_h|`. The report also includes the number of
distinct raw states on the same trajectory and a weaker control,
`factor_classes`, counting distinct observed center-column windows of length
`h`. The latter is not a predictive equivalence and is intentionally not used
as evidence for observer memory.

The right boundary is zero-padded only after width `h`; this is exact for the
`h`-step response because information outside that strip cannot reach the
observed adjacent cell within `h` updates. The probe therefore does not infer
an infinite right half-plane from a truncated state.

## Reproduction and provenance

From the project root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
python3 experiments/trajectory_restricted_observer.py \
  --input results/center-column-300000.txt --max-horizon 20 \
  --reference-steps 256 \
  --output results/trajectory-restricted-observer-300001-h20.json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
python3 experiments/trajectory_restricted_observer.py \
  --steps 1000001 --max-horizon 20 --reference-steps 256 \
  --output results/trajectory-restricted-observer-generated-1000001-h20.json
```

Each JSON artifact records its input SHA-256, first 32 bits, generator/source,
script SHA-256, Python runtime, finite partition digest per horizon, and two
independent checks: the first 256 bits against the expanding-row generator,
and the first 256 integer transitions against a tuple reference.

## Results

The retained fixture's raw file SHA-256 is
`d6bed1d0526bd8cdf014d13b3c2a473d5ff0e343c60d283b3c42bd89728401f6`;
the normalized 300,001-bit sequence recorded as `input.sha256` in the JSON is
`e96390915ef4fb2e694fb6adf606474bf700205f0143cc0161b041d4074c327d`.

| h | `|S_h|` | trajectory classes (300k) | trajectory classes (1M) |
|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 |
| 1 | 2 | 2 | 2 |
| 2 | 3 | 3 | 3 |
| 3 | 5 | 5 | 5 |
| 4 | 7 | 7 | 7 |
| 5 | 11 | 11 | 11 |
| 6 | 16 | 16 | 16 |
| 7 | 25 | 25 | 25 |
| 8 | 35 | 35 | 35 |
| 9 | 52 | 52 | 52 |
| 10 | 71 | 71 | 71 |
| 11 | 104 | 104 | 104 |
| 12 | 141 | 141 | 141 |
| 13 | 203 | 203 | 203 |
| 14 | 272 | 272 | 272 |
| 15 | 387 | 387 | 387 |
| 16 | 517 | 517 | 517 |
| 17 | 733 | 733 | 733 |
| 18 | 971 | 969 | 971 |
| 19 | 1364 | 1362 | 1364 |
| 20 | 1792 | 1782 | 1792 |

The generated 1,000,001-bit run has input SHA-256
`4113d4e32ea28b88650275495c8d762a5293212b0affa32046ad46627a656912`.
Its trajectory visits every finite predictive class through `h=20`. The
shorter retained fixture misses 2, 2, and 10 classes at `h=18,19,20`, which
is consistent with finite-prefix saturation rather than a stable sparse
trajectory subquotient. At `h<=14`, the trajectory raw states and center
factor counts are already all `2^h`; above that they remain useful controls but
are not predictive-state evidence.

## Interpretation and limits

This is positive evidence against the proposed shortcut “the actual center
trajectory occupies a small bounded predictive subquotient.” It is not a lower
bound on a single online observer unless that observer is required to preserve
the all-boundary counterfactual response semantics of `q_h`. It also does not
show that every `h` is eventually covered, and it cannot rule out an eventual
period with an arbitrarily long transient. The finite results offer no sharper
theorem or falsifier for the open problem; the next useful step would require a
proof of coverage or a different observer criterion.

## Prior-art check (2026-08-25)

- The official [Wolfram Rule 30 Prize page](https://www.rule30prize.org/)
  still lists “Does the center column always remain non-periodic?” as Problem
  1 and requests a full proof. No accepted resolution was found.
- Rowland, *Local Nested Structure in Rule 30* (Complex Systems 16, 2006),
  [paper PDF](https://ericrowland.github.io/papers/Local_nested_structure_in_rule_30.pdf),
  proves/uses periodic right diagonals and nested local structure. It does not
  define this trajectory-restricted predictive quotient or settle the
  center-column question.
- Kopra, *Rapid left expansivity, a commonality between Wolfram's Rule 30 and
  powers of p/q* (Theoretical Computer Science 946, 2023),
  [open paper](https://arxiv.org/abs/2202.13809), places Rule 30 in a class
  where Jen-style width-2 trace aperiodicity follows, while explicitly leaving
  the width-1 single-seed trace as Problem 4.8. This is the closest prior-art
  boundary check for the present observer question; it does not define the
  finite predictive quotient measured here.
- Cervelle, Formenti, and Guillon, *Sofic Trace of a Cellular Automaton*
  ([arXiv:math/0703241](https://arxiv.org/abs/math/0703241)), develops generic
  trace-subshift terminology. It is relevant background for “trace” but is not
  a Rule-30 observer-memory result.
- Search hits claiming a Rule-30 solution (for example Das, 2022,
  [arXiv:2207.13237](https://arxiv.org/abs/2207.13237)) were not treated as
  accepted prior art: the official prize page remains open and these works do
  not establish a recognized proof of the target statement.
