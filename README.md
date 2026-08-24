# Rule 30 Center Column: An Open-Problem Research Workspace

This repository contains an ongoing attack on one of the simplest statements in mathematics
that nobody knows how to prove:

> **Does the center column of Rule 30 ever become periodic?**

Rule 30 is the elementary cellular automaton with local update

```
a_x(t + 1) = a_{x-1}(t) XOR (a_x(t) OR a_x(t+1))
```

started from a single black cell on a white background. The question — Wolfram's Rule 30
Prize Problem 1 (2019) — is whether the center column `c(t) = a_0(t)` is eventually periodic,
i.e. whether there exist integers `p, i` with `c(t+p) = c(t)` for all `t > i`.
The sequence is known to be non-periodic for the first billion steps [REPORTED], and Erica Jen
proved in 1986 that no **two** adjacent columns can both be eventually periodic [FORMAL, Jen 1986].
Extending "two columns" to "one column" is explicitly cited as the open barrier [REPORTED, Wolfram 2019].

## Status

**Open.** This workspace does not solve the problem. What it contains:

- Self-contained proofs of new structural theorems about Rule 30's predictive-state quotient.
- A large experimental apparatus (~117 scripts): periodicity tests, finite-state observers,
  quotient / predictive-state automata, coverage censuses.
- One honestly retracted proof attempt, with a concrete counterexample to the flawed step.
- A precise map of why the known two-column argument stops short of one column.

Claims throughout are labeled: `FORMAL` (proved here), `EMPIRICAL` (verified computationally),
`REPORTED` (literature), `SPECULATIVE`.

## Headline findings

### Proved here (FORMAL)

1. **Predictive-state classes grow without bound.** Let `S_h` be the equivalence classes of
   width-`h` right-half states under exact future-response to boundary words. Then `|S_h| → ∞`,
   empirically as `|S_h| ≈ exp(C · h^(2/3))` through h = 21 [EMPIRICAL growth law; FORMAL that it
   diverges]. Consequence: no finite-state machine built this way can act as an infinite-horizon
   "bridge" observer.
   (`research/partial-results.md`, `experiments/predictive_state_growth.py`)

2. **Theorem 11 — full reachability from all-zeros.** Every width-`h` binary state is reachable
   from all-zeros in exactly `h` driven steps; verified by BFS for h ≤ 20 [EMPIRICAL] and proved
   for all h by induction using backward reconstruction and left-permutativity [FORMAL].
   (`research/partial-results.md`, `experiments/quotient_connectivity.py`)

3. **Theorem 11+ — universal bijectivity.** For *any* starting state, the map from `h` boundary
   bits to the width-`h` state after `h` steps is a bijection of `{0,1}^h`. Proved via a Front
   Propagation Lemma plus GF(2)-Jacobian triangularity; exhaustively verified h ≤ 11, sampled
   h ≤ 15. Notable because the *single-step* map is not bijective.
   (`experiments/bijectivity_test.py`, `experiments/jacobian_test.py`)

4. **Recursive characterization of the quotient.** Classes are uniquely determined by
   `(ℓ(c), τ₀(c), τ₁(c))`; right-truncation descends to the quotient with fibers of size 1 or 2;
   the truncation/child maps form a commuting square. Verified exactly for h ≤ 21.
   (`research/partial-results.md`, Props 11c–11h)

5. **Self-contained proof of the two-column barrier.** If any two adjacent columns are eventually
   periodic, left-permutativity propagates periodicity indefinitely leftward, forcing a far-left
   column permanently zero — contradicting the light-cone identity `a_{-t}(t) = 1`. A clean,
   reproducible version of the Jen 1986 mechanism. [FORMAL]

6. **Eventual periodicity survives finite-state observation.** Any finite-state transducer applied
   to an eventually periodic sequence stays eventually periodic — which makes the workspace's
   transform experiments (XOR-shift, running parity, window observers) theoretically relevant
   rather than heuristic. [FORMAL] (Proposition 7)

### Empirical results (EMPIRICAL)

7. **Full class coverage.** The actual center-column trajectory visits *every* predictive class
   in `S_h` for h ≤ 22 (saturation at ~4.6M steps for h=22). Saturation ratio grows but appears
   polynomial. This is a deep property of the center column: Theorem 11 shows all classes are
   reachable by *some* input; the center column actually visits them all.

8. **Coverage is dynamical, not string-theoretic.** At h=20, six visited classes have member
   tuples that never appear as subwords of the center column (within 1M bits); only ~9% of
   trajectory states are subwords at each step. Subword-complexity arguments cannot prove coverage.

9. **No small periods anywhere.** No eventual period up to 2048 (8-repeat criterion) on the 1M-bit
   prefix; same for XOR-shift and running-parity transforms; no fixed column ±1…±19 has temporal
   period ≤ 500 within 2000 steps.

10. **Truncation periods do not stabilize.** Width-K right-half simulations under a period-2
    boundary give machine periods 138 (K=20), 510 (K=30), 6258 (K=39), 2722 (K=40) — growing
    without bound, strongly suggesting the true adjacent column is not eventually periodic even
    for generic periodic boundaries.

### Retracted

11. **Proposition 13 (period lower bound from coverage) — RETRACTED.** The counting argument
    ("period p implies ≤ p classes visited") fails because a periodically-driven finite machine
    has period L·p where the macro-cycle length L can be as large as 2^h; the corrected bound is
    vacuous. Concrete counterexample at h=6, word "10": machine period 8, visits 7 classes.
    The full error analysis and counterexamples are preserved in
    `research/partial-results.md` and `experiments/verify_period_bug.py`.

## The fundamental gap

The reason this remains open, made precise in `research/partial-results.md`:

- Two adjacent periodic columns ⇒ everything left of them periodic ⇒ contradiction. (Proved.)
- One periodic column gives *no* known second periodic object. The adjacent right column is a
  semi-infinite system — not finite-state — and its unique determination by the center column
  (also proved here, Prop 9) is about information content, not bounded-memory extraction.

Any successful proof must either find a finite-state "effective second column" or derive a
contradiction from one column alone. Candidate bridge criteria are written down in
`research/bridge-criteria.md`.

## Repository layout

```
research/     notes, literature review, proofs and proof attempts, journal
experiments/  reproducible scripts (Python; one C generator)
results/      generated outputs: bit columns (regenerable) and small check summaries
docs/         agent-maintained project documentation
```

## Running experiments

Requirements: Python 3 (standard library only); optionally a C compiler with GMP for fast
column generation.

Generate a center-column prefix (14M bits takes minutes via the C generator):

```bash
cc -O3 -o experiments/rule30gen experiments/rule30gen.c -lgmp
./experiments/rule30gen 1000000 > results/center-column-1000000.txt
```

or in pure Python:

```bash
python3 experiments/generate_bits.py 1000000 > results/center-column-1000000.txt
python3 experiments/generate_bits_numpy.py 1000000 > results/center-column-1000000.txt
```

Basic generation and periodicity testing:

```bash
python3 experiments/rule30_center_column.py --steps 2000 --report-prefix 128 --max-period 256 --min-repetitions 4
python3 experiments/rule30_center_column.py --input results/center-column-1000000.txt --max-period 2048 --min-repetitions 8
```

Finite-state observers and the predictive-state machinery:

```bash
python3 experiments/search_finite_state_observers.py --input results/center-column-1000000.txt --states 2 --prefix-length 200000
python3 experiments/right_half_response_classes.py --horizon 8
python3 experiments/predictive_state_automaton.py --max-horizon 9
python3 experiments/predictive_state_trace.py --input results/center-column-1000000.txt --horizon 10 --steps 5000
python3 experiments/predictive_state_growth.py            # |S_h| through h≈21 in minutes
python3 experiments/fast_class_coverage2.py               # full coverage census, h ≤ 22
```

## Bounded Python API

The repository-local `rule30` package exposes the small, finite-width
transition and predictive-partition surface without changing the existing
experiment modules:

```python
from rule30 import predictive_partition, response_signature

partition = predictive_partition(6)
signature = response_signature(0b010101, 6)
```

The facade also exports `integer_successor`, `evolve_integer_state`,
`response_trace`, and `PredictivePartition`. `predictive_partition` exhaustively
enumerates width-`horizon` states and is intended for small bounded checks; it
does not assert an infinite-horizon quotient or any theorem about Rule 30. For
adjacent finite horizons, `PredictivePartition.right_truncation_map(lower)`
checks and returns the class map induced by dropping the highest encoded bit.
`PredictivePartition.class_members(class_id)` exposes one immutable finite
class, while `right_truncation_fibers(lower)` groups source class IDs by their
lower-horizon target after repeating the map's finite well-definedness checks.
`nested_transition_map(lower)` exposes the checked boundary-driven map from
each `S_h` class to its `S_{h-1}` target after one update and right truncation;
each source entry contains targets for boundary bits `0` and `1`. This is a
finite nested map, not a same-horizon transition function or an
infinite-horizon quotient.

## Curated experiment index

Highlights (see `experiments/` for the full set of ~117 scripts):

| Script | What it tests | Result |
| --- | --- | --- |
| `rule30_center_column.py` | Center-column generation; eventual-period detection; local transforms (xor-shift, running-parity) | No period ≤ 2048 (8 reps) on 1M bits; transforms clean too |
| `generate_bits*.py`, `rule30gen.c` | Fast exact column generation (bigint / numpy / GMP) | Reference implementations agree |
| `predictive_state_growth.py` | Exact \|S_h\| via recursive quotient algorithm, O(2^h·h) | \|S_h\| = 1792 at h=20; growth ≈ exp(C·h^{2/3}); divergence proved |
| `fast_class_coverage2.py` | When every S_h class is first visited by the real trajectory | All classes visited for h ≤ 22 |
| `coverage_vs_subwords.py` | Is coverage a subword property? | No — 6 visited classes at h=20 are non-subword |
| `bijectivity_test.py`, `jacobian_test.py` | Universal bijectivity of the h-step driven map | Bijective from every start state (proof + verification) |
| `front_propagation_proof.py` | Front Propagation Lemma behind Theorem 11+ | Verified h ≤ 10 exhaustive, h ≤ 14 sampled |
| `quotient_connectivity.py` | BFS reachability of all raw states from zeros | All 2^h states reached in exactly h steps, h ≤ 20 |
| `right_half_response_classes.py` | Response-equivalence compression of right-half states | Strong compression through horizon 11 |
| `predictive_state_automaton.py` | Coherence of quotient transitions across horizons | Deterministic next-class map holds through horizon 10+ |
| `predictive_state_trace.py` | Which classes the real trajectory visits | All classes at horizon 10 within 5000 steps |
| `truncation_period_stability.py` | Do width-K truncation periods converge? | No: 138→510→6258→2722 for K=20..40, p=2 |
| `search_finite_state_observers.py` | Sweep of tiny finite-state observers of c(t) | Only trivial low-complexity candidates |
| `truncated_right_half_observer.py` | Reconstruction-aware width-limited observers | Raw truncation does not approximate column 1 well enough |
| `fiber_growth_table.py`, `child_relationship.py` | Fiber structure of ρ_h: S_h → S_{h−1} | Fibers size ≤ 2; even/odd parity pattern in sibling children |
| `verify_period_bug.py`, `prop13_counterexample.py` | Tests of the retracted Proposition 13 counting bound | Confirmed vacuous: macro-cycle L up to 2^h |
| `column_periodicity.py` | Temporal periods of fixed columns ±1…±19 | None ≤ 500 within 2000 steps |
| `edge_structure.py` | Periodicity of light-cone diagonals | Right diagonals double periods; left diagonals small |

## Literature

Key sources summarized in `research/literature.md`:

- S. Wolfram, *Announcing the Rule 30 Prizes* (2019) — Problem 1: "Does the center column always
  remain non-periodic?" [REPORTED]
- E. Jen, *Journal of Statistical Physics* 43 (1986) — no two adjacent columns both eventually
  periodic. [REPORTED]
- Official prize site lists Problem 1 as unresolved. [REPORTED, checked 2026]

## License

MIT — see [LICENSE](LICENSE).
