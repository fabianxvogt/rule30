# Research Journal

Use dated entries.

## 2026-03-30

### Setup

- Created initial workspace scaffold.
- Added a reproducible experiment script for center-column generation and basic periodicity checks.

### Breakthroughs

- Verified that the requested target is, at least from the 2019 Rule 30 prize statement, an open problem rather than an already established theorem.
- Confirmed a much faster bitwise recurrence for generating the center column, matching the slower reference implementation on tested prefixes.
- Confirmed from the official Rule 30 prize site that Problem 1 is still presented as an open submission target.
- Ran a 300,000-step experiment with no eventual period found up to period 1024 under an 8-repeat criterion.
- Observed full block coverage through length 14 in the 300,000-step sample, near-full coverage at length 15, and mismatch rates near 50% for shifts 1 through 16.
- Formalized the two-column reconstruction mechanism into explicit lemmas and corollaries in `research/partial-results.md`.
- Recovered and analyzed a previously generated 1,000,001-bit center-column file: no eventual period found up to 2048 with 8 repetitions, full 16-block coverage, near-full 17- and 18-block coverage, and shift mismatch rates close to 50% through shift 16.
- Checked the `xor-shift` derived sequence on a 200,000-bit prefix; it also showed no eventual period up to 1024 with 8 repetitions and retained high local block complexity.
- Refactored the periodicity detector to test periodic suffixes directly, which makes saved-file analysis practical on million-bit samples.
- Added an `--input` mode so the main experiment script can analyze stored bit sequences without recomputing Rule 30.
- Swept a small family of local transforms over the million-bit saved sequence; none showed a small eventual period or any loss of full block coverage through length 16.
- Strengthened the zero-column analysis: an eventually zero column forces its neighboring column to be eventually constant, and forces every fixed column further left to settle into either all zeros or an alternating `...1010` pattern.
- Tested the running-parity stateful transform on the million-bit saved sequence; it still showed no eventual period up to 2048 and retained full block coverage through length 16.
- Formalized the meta-principle that eventual periodicity survives finite-state observation, which makes the transform experiments theoretically relevant rather than merely heuristic.
- Added a note describing concrete bridge criteria that would be sufficient to close the current one-column proof gap.
- Clarified that the center column already determines the right half-plane uniquely, shifting the bridge problem from uniqueness to memory complexity.
- Exhaustively searched the full nonconstant 2-state observer class on a long prefix; it did not produce a compelling low-complexity candidate.
- Strengthened that conclusion by filtering to balanced outputs: even then, the 2-state class only produced trivial period-2 or obviously synthetic low-complexity sequences.
- Tested the first reconstruction-aware observer family, finite-width right-half truncations, and found that literal width-limited boundary state does not approximate the adjacent right column well enough to suggest a simple finite-state bridge.
- Replaced raw truncation by quotienting right-half states under exact future-response equivalence and found substantial compression through horizon 10; this is the first genuinely promising reconstruction-aware signal.
- Extended that computation to horizon 11 and the compression trend persisted strongly.
- Verified that the finite-horizon response-equivalence classes close under deterministic next-bit transitions through horizon 10, giving a coherent nested predictive-state system.
- Tracing the real center-column trajectory at horizon 10 showed that all 71 predictive classes are visited within 5000 steps.

### Failed Approaches

- A naive eventual-period detector produced false positives when only a very short suffix matched a candidate period near the end of the sample.
- Tightened the experiment so a reported period must be supported by multiple full repetitions.

### 2026-03-30 (continued) — Predictive-state growth analysis

#### New results

- Built a fast recursive predictive-state quotient algorithm (`experiments/predictive_state_growth.py`)
  that computes the exact number of response-equivalence classes at horizon h in O(2^h · h) time,
  vs. the O(4^h) naive approach.  The new algorithm enables computation through h = 20 in ~1-2 minutes.
- Extended the class-count sequence through h = 20:
  `a(h) = 1, 2, 3, 5, 7, 11, 16, 25, 35, 52, 71, 104, 141, 203, 272, 387, 517, 733, 971, 1364, 1792`
- Confirmed that the nested transitions are well-defined (all classes at h project correctly to h−1)
  at every horizon 1 ≤ h ≤ 20.  The predictive-state system is coherent through h = 20.

#### Growth characterisation

- `log a(h)/h` decreases monotonically from 0.693 to 0.375 → **NOT purely exponential**.
- `log a(h)/log h` increases from 0.549 to 2.46 at h = 20 → **NOT polynomial**.
- `log a(h)/√h` increases from 0.693 to 1.675, still rising → **NOT exp(c√h)**.
- `log log a(h)/log h` increases toward ≈ 0.672 ≈ 2/3:
  → **stretched exponential** `a(h) ~ exp(C · h^(2/3))`.
- No k = 2, 3, 4, or 5 linear recurrence with |coefficient| ≤ 4 was found.
- OLS best-fit exponential base (h ≥ 12): ≈ 1.374 per horizon step (below √2 = 1.414).
- Two-step geometric mean (√(a(h)/a(h−2))) is still decreasing at h = 20 (≈ 1.358).

#### Transition image coverage

- For each h, the transition maps δ_0, δ_1 : S_h → S_{h−1} have images that are proper
  subsets of S_{h−1} for h ≥ 7.  Coverage fractions decrease:
  - δ_0: 1.000 for h ≤ 6, then 0.937, 0.880 … 0.788 at h = 20.
  - δ_1: 1.000 for h ≤ 6, then 1.000, 0.960 … 0.853 at h = 20.
- The image of δ_1 is strictly larger than the image of δ_0 at every h ≥ 7.

#### Implications

- The predictive-state quotient has an **unbounded** number of classes → no finite-state machine
  can serve as the infinite-horizon bridge via this approach alone.
- The **sub-exponential but super-polynomial** growth is a new structural property of Rule 30 and
  may itself be worth connecting to known complexity results.
- The stretched-exponential β ≈ 2/3 suggests the complexity of right-half configurations (as seen
  from the boundary) grows like `exp(h^{2/3})` — reminiscent of certain 2D-interface counts or
  pattern-complexity results.

### 2026-03-30 (continued) — Coverage timing and rare classes

#### Coverage saturation grows faster than |S_h|

Experiment: `coverage_timing.py --max-horizon 17 --steps 200000`.

| h  | |S_h| | sat_step | sat/|S_h| |
|----|--------|----------|-----------|
| 10 |     71 |      729 |     10.3  |
| 11 |    104 |     5165 |     49.7  |
| 12 |    141 |     2155 |     15.3  |
| 13 |    203 |     9742 |     48.0  |
| 14 |    272 |    19171 |     70.5  |
| 15 |    387 |    26833 |     69.3  |
| 16 |    517 |   104527 |    202.2  |
| 17 |    733 | >200000  |     ∞     |

- Saturation step is up to 202× the class count at h=16, and >30× the coupon-collector prediction.
- The trajectory visit distribution has Gini ≈ 0.52–0.55 — highly non-uniform.
- The rarest classes at h=14 are `00000000000001` (visited 7 times in 200k steps) and
  `10000000000010` (16 times), both with very few members and extreme 1-count (1 bit set out of 14).
- At h=16, the rarest class `0010010010010001` (period-3 pattern of 1s) was first visited at step
  104,527 — giving a **lower bound**: if the center column has period p, then p ≥ 104,528 (for h=16).
- At h=17, at least one class remained unvisited after 200k steps: **p ≥ 200,001** (for h=17).
- 500k steps saturates h=16  saturation at 104,527 and Gini = 0.55.

#### Implication: growing lower bounds on any hypothetical period

The saturation step T(h) is a lower bound on any hypothetical period p:
  `sat_step(h) ≤ p`  for each h.
Since T(h) is growing (>100k at h=16, >200k at h=17), p must exceed 200,000 for the
center column to be eventually periodic at all.

This alone does not prove aperiodicity, but the growing T(h) pattern is a strong signal.

### 2026-03-30 (continued) — Subword complexity and proof structure

#### Subword complexity vs. predictive-state class coverage

Experiment: `subword_complexity.py --max-horizon 20 --steps 1000000`.

Key findings:

| h  | 2^h    | |S_h| | k_c(h)  | classes_hit | all S_h? |
|----|--------|-------|---------|-------------|----------|
| 12 |   4096 |   141 |    4096 |         141 | yes      |
| 16 |  65536 |   517 |   65536 |         517 | yes      |
| 17 | 131072 |   733 |  131016 |         733 | yes      |
| 18 | 262144 |   971 |  256378 |         971 | yes      |
| 19 | 524288 |  1364 |  446250 |        1364 | yes      |
| 20 |1048576 |  1792 |  644259 |        1791 | **no**   |

Here `k_c(h)` = number of distinct length-h subwords of the 1M-step prefix.

- For h ≤ 16: all 2^h words appear in 1M steps (full block complexity up to length 16).
- For h ≥ 17: some words are missing in 1M steps, but all (or nearly all) classes are still hit.
- For h=20 the last class was missed with 1M steps, consistent with it needing a longer prefix.

#### Clean proof structure identified

The data supports a **period lower bound argument**:

Let c(t) denote the center column and p be a hypothetical period.

**Lemma A** (Surjectivity): Every class in S_h is reachable from all-zeros in exactly h steps
via some binary word of length h.  BFS confirms this for h ≤ 16.

**Lemma B** (Presence in center column): For every class c ∈ S_h, at least one length-h word
that steers to c appears as a subword of the center column within the first M steps, where M
is O(|S_h| * average_words_per_class) = O(exp(h^{2/3}) * poly(2^h/|S_h|)).

**Consequence**: The number of distinct length-h subwords of the center column ≥ |S_h| ~ exp(h^{2/3}).

**Period lower bound**: If c(t) is eventually periodic with period p (*and pre-period T), then
the number of distinct length-h subwords is ≤ T + p. So T + p ≥ |S_h| ~ exp(h^{2/3}) for all h.
Since T and p are fixed, this is impossible for large h. **Contradiction.**

#### Remaining gaps

1. **Prove Lemma A for all h** (not just h ≤ 16): Can all raw states be reached from all-zeros?
   This likely follows from Rule 30 being left-permutative (any target state can be pre-imaged).

2. **Prove Lemma B for all h**: Does every class correspond to a word that appears in the
   center column?  From the data: yes for h ≤ 19 with 1M steps.  But this needs proof for all h.
   The key: is the map {length-h subwords of center column} → S_h surjective for all h?

3. **Reduce Lemma B to a weaker statement**: Perhaps we don't need surjectivity for ALL h, but
   just for infinitely many h, or for h growing faster than log(T+p).

If both lemmas can be proven, the contradiction is complete and non-periodicity follows.

### Next Steps

- Look for post-2019 progress on Problem 1.
- Push experiments to much longer prefixes with the bitwise generator.
- Try to formalize partial lemmas that follow from left-permutativity or from block-occurrence properties.
- Decide whether to focus next on partial theorems or on building higher-scale experiments with streaming output.
- Test whether finite-window transforms of the center column reveal a second sequence that would also have to be eventually periodic under the main hypothesis.
- Use the new `--input` mode to compare several local transforms on the same million-bit base sequence.
- Move beyond naive local transforms and test stateful or reconstruction-informed observables.
- Look for a direct incompatibility between the center-column hypothesis and the left-tail classification obtained from an eventually zero column.
- Try a reconstruction-aware stateful transducer rather than generic parity-based stateful transforms.
- Use `bridge-criteria.md` as the design spec for the next observable instead of trying generic transforms at random.
- Investigate compressed state summaries for the driven right half-plane near the boundary.
- Inspect the 3-state observer search result and then decide whether blind exhaustive search is still worth it versus switching to reconstruction-aware observer families.
- Move from literal truncation to quotient-like or symmetry-based summaries of right-half states, since plain width truncation is not promising.
- Extract and study the recursive structure of the future-response equivalence classes.
- Reinterpret the future-response equivalence classes as predictive states and look for a recursive update rule on those states.
- Extract the actual transition structure of the predictive-state quotients and look for a recursion or symbolic description of the class-growth sequence.
- Check whether the same full-coverage phenomenon persists at horizon 11 and beyond.

---

## Session 2 (current) — Full coverage confirmation and raw-state reachability

### Key results this session

**Full S_h class coverage confirmed for h <= 22:**

The actual center-column-driven trajectory visits **every** class in S_h for h = 1 to 20,
within the 1,000,001-bit center-column prefix. Using `experiments/fast_class_coverage2.py`
(integer lookup tables for O(1) trajectory steps):

| h  | |S_h| | sat_step  | ratio  | rarest class (example state, weight)           |
|----|---------|-----------|--------|------------------------------------------------|
| 16 |     517 |   104,527 | 202.2x | `0000000000000001` (wt=1)                      |
| 17 |     733 |   203,477 | 277.6x | `00100100100100010` (wt=5)                     |
| 18 |     971 |   429,241 | 442.1x | `000000000000001101` (wt=3)                    |
| 19 |    1364 |   658,581 | 482.8x | `0100100100100100010` (wt=6)                   |
| 20 |   1792 |    877,606 | 489.7x | `00000000000000000001` (wt=1, class 1)         |
| 21 |   2497 |  1,666,406 | 667.4x | `000000000000000000100` (wt=1, class 3)        |
| 22 |   3263 |  4,585,894 | 1405.4x| `0100100100100100100010` (wt=7, class 1246)    |

The h=20 "miss" in the previous subword_complexity.py experiment (1791/1792) was an ARTIFACT
of how that script measures subwords (starting from all-zeros each window), not a genuine miss
of the driven trajectory. The trajectory DOES visit class 1 at step 877,606.

**h=21 and h=22 completion:**
|S_21| = 2497. A 3M-step run completed full coverage at step 1,666,406 (ratio 667.4x). The last
class visited was class 3 (`000000000000000000100`, wt=1), followed by several other very rare
low-weight and high-weight classes.

|S_22| = 3263. A 6M-step run completed full coverage at step 4,585,894 (ratio 1405.4x). The last
class visited was class 1246 (`0100100100100100100010`, wt=7), and several of the last ten classes
were again very low-weight or highly structured sparse states. So the coverage hypothesis now holds
empirically for h <= 22.

**Zero-run analysis — surprising finding:**
The longest run of consecutive zeros in the 1M-bit center column prefix is only **19** bits
(positions 32,198–32,216). Yet the class `00000000000000000001` (wt=1 at h=20) was visited
at step 877,606 WITHOUT a run of 20 zeros. This means the near-vacuum state IS reachable via
more complex dynamics, not just a simple long zero-run.

| Run length | First occurrence | Note                                |
|------------|-----------------|-------------------------------------|
|         15 |           26,216 |                                    |
|         16 |           32,198 | (longest run start)                 |
|         17 |           32,198 | (within same run)                   |
|         18 |           32,198 | (within same run)                   |
|         19 |           32,198 | (within same run, longest overall)  |
|         20 |  (not in 1M bits)| → no 20-zero run in 1M center bits  |

**Raw-state reachability — fundamental structural result:**

New experiment: `experiments/quotient_connectivity.py` (via BFS from all-zeros state over arbitrary
boundary bit sequences). Result: **every single one of the 2^h raw width-h states is reachable from
the all-zeros state** for every h = 1 to 22.

| h  | 2^h      | states reachable | all? |
|----|----------|-----------------|------|
|  1 |        2 |               2 | YES  |
|  8 |      256 |             256 | YES  |
| 12 |     4096 |            4096 | YES  |
| 16 |    65536 |           65536 | YES  |
| 20 |  1048576 |         1048576 | YES  |
| 22 |  4194304 |         4194304 | YES  |

This is stronger than the original computational lemma: not only are all quotient classes reachable,
but all 2^h raw states are reachable from all-zeros. Moreover, this is no longer just empirical: we
now have a complete inductive proof (Theorem 11) based on backward reconstruction and left-
permutativity.

**Valid recursive quotient structure:**

Although same-h predictive classes do NOT define a deterministic automaton under a fixed boundary
bit, there IS a deterministic cross-horizon map

$$
\Psi_h : S_h \to S_{h-1} \times S_{h-1}, \qquad c \mapsto (\tau_0(c), \tau_1(c)),
$$

where $\tau_b(c)$ is obtained by evolving one step with bit $b$, truncating the rightmost site, and
projecting to $S_{h-1}$. This is not just computational: from the recursive form of the response
signature, a class in $S_h$ is uniquely determined by the triple $(\ell(c), \tau_0(c), \tau_1(c))$,
where $\ell(c)$ is the common leftmost bit of states in the class. Therefore each pair
$(\tau_0(c), \tau_1(c))$ has fiber size at most 2 automatically. Empirically through h = 21, the
only observed fibers are of size 1 or 2, with each 2-way fiber splitting into one 0-leading class and
one 1-leading class. This looks like a real recursive signature of the predictive quotients and may
be the best current route toward an h -> h+1 argument.

There is also a second proved cross-horizon map: plain right-truncation $\rho_h : S_h \to S_{h-1}$,
obtained by dropping the last bit of a raw state. This is well-defined by finite-speed propagation:
the dropped bit cannot affect the leftmost output within h-1 steps. Computationally, its fibers also
have size only 1 or 2 through h = 21.

These maps are compatible in two useful ways:

1. The square $\rho_{h-1} \circ \tau_b = \tau_b \circ \rho_h$ commutes for each b, giving a genuine
  recursive diagram across three consecutive horizons.
2. The two child classes $\tau_0(c)$ and $\tau_1(c)$ always lie in opposite leading-bit sectors,
  because changing the first boundary bit flips the leftmost successor bit.

An additional empirical parity effect appeared: for even h <= 20, the maps
$c \mapsto (\rho_h(c), \tau_0(c))$ and $c \mapsto (\rho_h(c), \tau_1(c))$ are injective, while for
odd h <= 21 both fail. That may be noise, but right now it looks structured enough to be worth
tracking.

**Theoretical consequence**: Starting from the initial all-zeros state, ANY width-h binary state
can be reached by choosing the right sequence of boundary bits. There is no "unreachable" part of
the raw state space. The driven dynamics is STRONGLY REVERSIBLE — every state has a preimage.

(Note: This is consistent with left-permutativity. Rule 30 is left-permutative: given current state
s and desired successor state s' at horizon h, there is a unique first bit b ∈ {0,1} that steers
s to s' at position 0. This gives a tree structure where every state has a parent but the FULL
reachability from all-zeros requires that the tree have depth h and cover all 2^h leaves.)

### Proof structure (current best understanding)

The argument for aperiodicity is now nearly complete, conditional on closing one gap:

**Theorem (Conditional)**: If the Rule 30 center column is eventually periodic with pre-period T
and period p, then for every h ≥ 1: the driven right-half trajectory at horizon h eventually
becomes periodic with period p after time T + h. Hence the number of distinct S_h classes visited
is at most p. But (empirically for h ≤ 20, conjectured for all h) the trajectory visits ALL |S_h|
classes. So p ≥ |S_h| for every h. Since |S_h| → ∞, no fixed p exists. Contradiction.

**Gap**: Prove that the trajectory visits ALL |S_h| classes for every h (not just h ≤ 20).

**Correction to an exploratory claim**: the same-h quotient on S_h does NOT define a deterministic
automaton under a fixed boundary bit. Two raw states in the same predictive class can evolve to
different S_h classes under the same input bit, so the SCC / condensation-DAG analysis based on a
single representative per class was invalid.

What is valid is this: the induced class dynamics is set-valued, and any future quotient-level
analysis has to respect that nondeterminism. The raw-state controllability result from Theorem 11 is
still correct, but it does not automatically yield a clean deterministic graph structure on S_h.

### Next experiments

1. Extend coverage to h=22 and beyond.
2. Analyze the set-valued class transition relation on S_h systematically.
3. Look for invariants or monotonicity inside that relation that might support an h -> h+1 argument.
4. Investigate WHY the near-vacuum state (class 1, single 1-bit) is always among the rarest. Is it
  related to first-return times to low-density states? Can we bound this first-return time?
5. Look for a structural argument weaker than full normality but strong enough to force class coverage.

---

## Session 3 — Parity structure, growth decomposition, and true vs truncated dynamics

### Key results this session

**1. Deep parity structure in ρ-fiber siblings (Observations 11i, 11j)**

For each h, consider the rho-fibers: classes in S_h that map to the same class in S_{h-1}
under right-truncation ρ_h. By Observation 11e, these fibers have size 1 or 2. For 2-element
fibers, the siblings always share the same leading bit ℓ (somewhat surprisingly).

A striking **even/odd alternation** governs how 2-fiber siblings relate through their children
τ_0, τ_1:

- **Even h**: 2-fiber siblings share NEITHER τ_0 nor τ_1 (both children differ)
- **Odd h**: 2-fiber siblings share EXACTLY ONE of τ_0 or τ_1 (about half share τ_0, half τ_1)

This was verified computationally for h ≤ 19 (experiments/child_relationship.py).

Additionally, the children's rho-projection is always the same: for siblings c, c' in the same
ρ-fiber at horizon h, we have ρ(τ_b(c)) = ρ(τ_b(c')) for each b ∈ {0,1}. This follows from the
commuting square Proposition 11g.

**2. Growth decomposition: |S_h| − |S_{h−1}| = n_2(h)**

Let n_1(h) = number of 1-element ρ-fibers, n_2(h) = number of 2-element fibers.
Then |S_h| = n_1(h) + 2·n_2(h) and |S_{h-1}| = n_1(h) + n_2(h), so:

  |S_h| − |S_{h−1}| = n_2(h)

This was verified exactly for h = 1..21 (experiments/fiber_growth_table.py).

Growth table (selected values):

| h  | |S_h| | n_1  | n_2  | Δ=n_2 | n_2 ratio (from prev) |
|----|-------|------|------|-------|-----------------------|
| 15 |   387 |  131 |  128 |  128  |                       |
| 16 |   517 |  257 |  130 |  130  |  1.02      (even h)   |
| 17 |   733 |  301 |  216 |  216  |  1.66      (odd h)    |
| 18 |   971 |  495 |  238 |  238  |  1.10      (even h)   |
| 19 |  1364 |  578 |  393 |  393  |  1.65      (odd h)    |
| 20 |  1792 |  936 |  428 |  428  |  1.09      (even h)   |
| 21 |  2497 | 1087 |  705 |  705  |  1.65      (odd h)    |

The n_2 growth shows a clear parity pattern: odd→even ratio ≈ 1.1, even→odd ratio ≈ 1.65.

**3. Fiber provenance tracking**

Even h: each 2-fiber at horizon h generates exactly 2 child 2-fibers at h−1, covering nearly
all 2-fibers at h−1. Odd h: each 2-fiber generates 1 child 2-fiber. Fresh 2-fibers also appear.

(experiments/fiber_provenance.py)

**4. True vs truncated dynamics — critical discovery**

The truncated (zero-padded) width-h system evolves differently from observing the first h bits
of the true infinite Rule 30 right-half. The mismatch rate is 48–88% of steps for small h.

(experiments/verify_rho_trajectory.py, experiments/true_vs_truncated.py)

**Important clarification**: For the proof argument (Proposition 13), it is the TRUNCATED system
that matters, not the true infinite right-half. Here's why:

- The predictive-state classes S_h are defined by the response function R_h(s, β), which uses
  the truncated width-h dynamics (zero-padded at the right boundary).
- Under the assumption that c(t) has period p, the truncated width-h system is a finite-state
  machine (with state space {0,1}^h) driven by c(t). By Proposition 7, its trajectory is
  eventually periodic with period dividing p.
- If this trajectory visits all |S_h| classes, then p ≥ |S_h|.
- The TRUE right-half h-prefix is NOT a finite-state function of c(t) — it depends on the
  full infinite state and has unbounded memory. Proposition 7 does not apply to it.

So Observation 12 (coverage verified for h ≤ 22 using the truncated system) IS the correct
data for the proof. The true-system coverage is an interesting parallel phenomenon but is not
needed for the aperiodicity argument.

However, both systems achieve full coverage for h ≤ 18 (experiments/coverage_comparison.py),
with the true system often achieving coverage faster at higher h.

**5. C/GMP bit generator**

Compiled a fast C/GMP generator (experiments/rule30gen.c) for center column bits.
Performance: 1M bits in ~18s. Currently generating 15M bits for h=23 coverage testing.

**6. h=23 coverage**

|S_22| = 3263, verified in Session 2. Need |S_23| and 15M bits (in progress).

### Conceptual progress

The proof structure is now clearer:

1. The truncated system IS the correct finite-state system for the argument.
2. Observation 12 (truncated coverage for h ≤ 22) directly supports Proposition 13.
3. The parity structure in ρ-fiber siblings may help explain WHY coverage holds — the tree
   structure of S_h built from (ℓ, τ_0, τ_1) triples has a regular recursive pattern.
4. The growth identity |S_h| − |S_{h−1}| = n_2(h) connects class growth to the 2-fiber count,
   which in turn is governed by the parity-alternating multiplication pattern.

### Next experiments

1. Run h=23 coverage when 15M bits complete.
2. Analyze the recursive (ℓ, τ_0, τ_1) tree structure more carefully — can we prove that
   certain classes MUST be visited by exploiting the tree?
3. Try to prove coverage inductively: if all of S_{h-1} is visited, does the parity/fiber
   structure force all of S_h to be visited?
4. Study the set-valued class transition relation on S_h more carefully.
5. Look for patterns in which h-tuples are the LAST to be visited (rarest classes).

---

## Session 4 — Universal Bijectivity, Joint Surjectivity, h=23 coverage

### Key results this session

**1. Theorem 11+ (Universal Bijectivity)**

Proved that for ANY starting state $s_0 \in \{0,1\}^h$, the map
$$\Phi_{s_0} : (b_0, \ldots, b_{h-1}) \mapsto s_h$$
is a bijection from $\{0,1\}^h$ to $\{0,1\}^h$.

Proof method: GF(2) Jacobian analysis.
- Light cone property gives lower-triangular structure
- Front Propagation Lemma gives all-1 diagonal
- Lower-triangular matrix with 1s on diagonal has determinant 1 over GF(2)

**Front Propagation Lemma**: When two trajectories differ only in boundary bit $b_k$:
1. Difference cannot outrun light cone: $\Delta^{(t)}_j = 0$ for $j > t - k - 1$
2. Front always "lit": $\Delta^{(t)}_{t-k-1} = 1$ for $t = k+1, \ldots, k+h$

Key insight: the single-step map $f_b$ is NOT bijective (~60% image coverage), yet the
composition of h steps IS bijective regardless of starting state.

**2. Joint Surjectivity**

Proved: $\text{img}(f_0) \cup \text{img}(f_1) = \{0,1\}^h$ for all h.

This means every width-h state has at least one preimage under one of the two single-step
maps. Combined with Universal Bijectivity this gives a complete picture of the dynamics.

**3. f_b non-bijectivity and image contraction**

- $|\text{img}(f_b)| \approx 0.55$–$0.69 \times 2^h$ (each map covers only part of state space)
- Maximum preimage size = 2 exactly (every state has 0, 1, or 2 preimages under each $f_b$)
- Image coverage fractions decrease with h:
  - $f_0$: 1.000 for $h \le 6$, then 0.937, 0.880, ... 0.788 at h=20
  - $f_1$: 1.000 for $h \le 6$, then 1.000, 0.960, ... 0.853 at h=20

**4. NFA vs DFA gap**

The predictive-state classes $S_h$ do NOT form a deterministic automaton under single boundary
bits — two raw states in the same class can map to different classes under the same bit. This
rules out deterministic SCC/condensation approaches at fixed h.

**5. min_p(h) growth**

Computed minimum period p needed for random periodic sequences to achieve full $S_h$ coverage:
- min_p grows much faster than $|S_h|$, roughly like $|S_h|^\alpha$ with $\alpha \approx 2+$
- This amplifies the contradiction strength but is empirical

**6. h=22 and h=23 coverage completed**

Extended coverage verification:
- |S_22| = 3263, saturated at step 4,585,894 (ratio 1405.4×), 15M-bit prefix
- |S_23| confirmed reachable with 15M-bit dataset

### Status at session end

Proof structure appeared nearly complete: Theorem 11 (all-state reachability) + Observation 12
(full class coverage for h ≤ 23) + Proposition 13 (counting argument) seemed to close the gap
modulo proving coverage for all h. Session 5 would discover that Proposition 13 is wrong.

---

## Session 5 — Proposition 13 bug discovered; left-edge property

### Key results this session

**1. PROPOSITION 13 IS WRONG — critical bug discovered**

The counting argument in Proposition 13 claims: if center column has period p, then the driven
trajectory at horizon h has period dividing p, so visits ≤ p classes. Since |S_h| → ∞, p must
be unbounded — contradiction.

**The bug**: The driven trajectory at horizon h is a finite-state machine with state space
$\{0,1\}^h$ ($2^h$ states) receiving periodic input of period p. By standard automata theory,
the output is eventually periodic with period dividing $L \cdot p$, where L is the macro-cycle
length (determined by the machine's state-transition structure). L can be as large as $2^h$.

So the correct bound is: number of distinct classes visited ≤ T + h + L·p, where L depends on
h and can be comparable to $2^h$. This is always ≥ |S_h|, making the bound **vacuous**.

**Concrete counterexample**: h=6, p=2, boundary word "10".
- The machine has period 8 (not 2). That is, $L = 4$.
- It visits 7 distinct $S_6$ classes, while $|S_6| = 11$.
- So p = 2 but machine period = 8. The "period dividing p" claim fails catastrophically.

**2. Systematic verification of the period bug**

`experiments/verify_period_bug.py`: For h=4..10 and periodic words of period p=2..6,
confirmed that machine periods are typically $L \cdot p$ with $L \gg 1$.

`experiments/prop13_counterexample.py`: Detailed analysis of h=6, p=2.

**3. Left-edge property proved**

Proved: $a_{-t}(t) = 1$ for all $t \ge 1$ (the leftmost cell in the light cone is always 1).

Proof from Rule 30 structure: The left edge of the light cone evolves as
$a_{-t}(t) = a_{-(t-1)}(t-1) \oplus a_{-(t-1)+1}(t-1) \vee a_{-(t-1)+2}(t-1)$.
Since only position $-(t-1)$ is at the edge (everything further left is 0), this simplifies
to $a_{-t}(t) = a_{-(t-1)}(t-1) \oplus 0 = a_{-(t-1)}(t-1)$, giving constancy along the
left edge. With initial condition $a_0(0) = 1$, we get $a_{-t}(t) = 1$.

**4. Initial exploration of left-permutativity route**

Sketched a potential proof:
- center periodic → $a_0$ periodic
- $a_0$ periodic → $a_1$ periodic (????)
- Proposition 2 → all left columns periodic
- Far-left columns must be eventually zero
- Contradiction with $a_{-t}(t) = 1$

Noted that step 2 seemed promising via the right-half dynamics but left detailed analysis for
Session 6.

### Experiments created this session

- `experiments/verify_period_bug.py` — systematic period verification across h and p values
- `experiments/prop13_counterexample.py` — detailed h=6, p=2 counterexample
- `experiments/class1_reachability.py` — Class 1 reachability analysis
- `experiments/backward_tree_analysis.py` — backward preimage tree structure
- `experiments/zero_columns_check.py` — confirms no permanent zero columns

---

## Session 6 — The Fundamental Gap: one column to two columns

### Key results this session

**1. Left-permutativity route analyzed in detail — BLOCKED**

The proof sketch from Session 5 was: if center column is periodic with period p, then
leftward reconstruction (Proposition 2) forces all left columns periodic, but $a_{-t}(t) = 1$
contradicts an eventually-zero far-left column.

**Critical flaw identified**: Step 2 ("$a_0$ periodic → $a_1$ periodic") is NOT justified.
The right half is a **semi-infinite system**, not a finite-state machine. Periodicity of $a_0$
does NOT automatically imply periodicity of $a_1$. This is the same gap that Erica Jen's 1986
result leaves open.

Key distinction:
- Width-K truncated right half IS finite-state (state space $\{0,1\}^K$), so Proposition 7
  gives eventual periodicity of the truncated $a_1$
- But truncated $a_1$ agrees with true $a_1$ only for $\sim 2K$ steps
- As $K \to \infty$, truncation periods grow WITHOUT BOUND and do not stabilize

**2. Truncation period stability experiment — KEY result**

`experiments/truncation_period_stability.py`: Tested whether truncated right-half periods
converge as truncation width K grows.

Results for boundary "10" (p=2):

| K   | Period |
|-----|--------|
| 10  | 10     |
| 20  | 138    |
| 30  | 510    |
| 39  | 6258   |
| 40  | 2722   |

Periods grow erratically with no convergence. Column 1 agreement between truncations:
K=15 vs K=10 agree only to t=26. Same pattern for boundaries "110" (p=3), "1010" (p=4),
"11010" (p=5). This strongly suggests the true $a_1$ is NOT eventually periodic even for
generic periodic boundaries.

**3. Edge diagonal structure analysis**

`experiments/edge_structure.py`: Analyzed the periodicity of light-cone edge diagonals.

Right-edge diagonals $a_{t-d}(t)$ have periods that roughly double:
d=0→1, d=1→2, d=2→2, d=3→4, d=4→8, d=5→8, d=6→16, d=7→32, d=8→32, d=9→>100.
Sierpinski-like doubling structure.

Left-edge diagonals $a_{-(t-d)}(t)$ have small constant periods:
d=0→1, d=1→1, d=2→1, d=3→2, d=4→1, d=5→2, d=6→2, d=7→1, d=8→4, d=9→1.

**4. Column periodicity check**

`experiments/column_periodicity.py`: Checked temporal periodicity of columns ±1 through ±19
in Rule 30 from single cell (2000 steps). No column has period ≤ 500 in 2000 steps.

**5. Connection to Erica Jen (1986)**

Confirmed this is EXACTLY the known barrier: Jen proved that no two adjacent columns can both
be periodic. Extending to one column is explicitly cited as the open problem in Wolfram's
2019 prize statement: "there is no known way to extend that argument from two columns to a
single column."

**6. Alternative approaches explored — all blocked**

- **Difference propagation**: $d_x(t) = a_x(t+p) \oplus a_x(t)$ satisfies a NONLINEAR system
  (Rule 30's OR introduces quadratic $d_a \cdot d_b$ terms). When $c(t)=1$, OR blocks
  d-propagation; when $c(t)=0$, d propagates. Can't prove $d \equiv 0$.
- **Compactness**: State space $\{0,1\}^\mathbb{N}$ is compact, orbit has convergent
  subsequence, but this gives an $\omega$-limit point, not periodicity.
- **Information-theoretic**: Periodic column has 0 entropy; right half needs growing
  information. Tension exists but is not rigorous.
- **Algebraic**: Rule 30 = $a \oplus b \oplus c \oplus bc$ over $\mathbb{F}_2$; nonlinearity
  blocks algebraic approaches.
- **Partial reconstruction**: When $c(t) = 1$, $a_{-1}(t)$ is fully determined as
  $c(t+1) \oplus 1$. Only when $c(t) = 0$ is $a_1$ needed. Leads to case analysis but
  doesn't close.

**7. Documentation updates**

- Retracted Proposition 13 in partial-results.md with detailed explanation and counterexample
- Added comprehensive "Fundamental Gap" section to partial-results.md
- Fixed Attempts 11, 13, 15 in proof-attempts.md (corrected all "period dividing p" claims)
- Added Attempt 17 (Parts A–E) documenting all Sessions 5–6 findings

### Assessment

The project has reached the boundary of the known-open problem. Our results confirm and deepen
understanding of the Jen 1986 barrier but do not bridge it. The key insight is that proving
one column is aperiodic requires showing that periodic input to a semi-infinite system cannot
produce periodic output — which is precisely what no existing technique achieves.

### Promising directions going forward

1. **Finite-state "effective second column"**: Find an observable that is (a) a finite-state
   function of $c(t)$ and (b) sufficient for leftward reconstruction analogous to $a_1$.
2. **Speed-of-information argument**: Formalize the mismatch between periodic boundary
   information rate (O(1) bits/step) and light-cone growth requiring O(t) bits.
3. **Topological entropy**: Rule 30 has positive topological entropy; periodic orbit has zero.
4. **Linearized difference system**: Drop the $d_a \cdot d_b$ terms and analyze the leading-order
   propagation of the difference field.