# Status

## Target Statement

Prove that the center column of Rule 30, started from a single black cell, never repeats.

## Precision Needed

Before any proof attempt, we need to pin down the exact statement.

Candidate formalizations:

1. The center-column binary sequence is not eventually periodic.
2. No finite block can serve as a repeating period from some point onward.
3. No two distinct offsets produce the same infinite tail.

These are closely related but should not be conflated without proof.

## Working Caveat

This workspace starts from the conservative assumption that a complete proof is not currently established here. Experimental evidence is useful for steering proof attempts, but it does not prove the theorem.

Current external evidence now supports a stronger statement: the standard formulation of this question is explicitly presented by Stephen Wolfram as an open prize problem.

## Verified Facts

- Rule 30 is the elementary cellular automaton with local update rule `00011110` in Wolfram's numbering convention.
- We are using the standard initial condition with one black cell at the origin and white elsewhere.
- The natural formal target is eventual nonperiodicity: there do not exist integers `p, i` such that for all `t > i`, `c[t + p] = c[t]`.
- Wolfram's 2019 Rule 30 prize statement treats that target as open, while citing Erica Jen's 1986 result that no two columns can both become periodic.
- **Erica Jen (1986)**: Proved that no two adjacent columns of Rule 30 can both be eventually periodic. Extending this from two columns to one column is the open problem.

### Proved results (unconditional)

- **|S_h| → ∞** (Attempt 11): The number of predictive-state equivalence classes grows without bound. Growth rate ~exp(C·h^{2/3}).
- **Theorem 11**: Every width-h binary state is reachable from all-zeros via exactly h Rule 30 boundary steps, for all h ≥ 1. Proved by induction using backward reconstruction and left-permutativity.
- **Universal Bijectivity (Theorem 11+)**: For ANY starting state s₀, the map Φ_{s₀}: (b₀,...,b_{h-1}) → s_h is a bijection. Proved via GF(2) Jacobian + Front Propagation Lemma.
- **Joint Surjectivity**: img(f₀) ∪ img(f₁) = {0,1}^h for all h.
- **Left-edge property**: a_{-t}(t) = 1 for all t ≥ 1.
- **Recursive class characterization** (Props 11c–11h): Classes in S_h are uniquely determined by (ℓ(c), τ₀(c), τ₁(c)); right-truncation ρ_h is surjective with fibers of size 1 or 2; commuting square ρ∘τ = τ∘ρ holds.
- **Parity structure** (Obs 11i–11k): Even/odd alternation in fiber siblings' child-sharing; growth decomposition |S_h| − |S_{h−1}| = n₂(h).

### Verified empirically (not proved for all h)

- Full class coverage: center-column trajectory visits ALL |S_h| classes for h ≤ 23.
- Saturation ratios grow (sat_step / |S_h|): ~200× at h=16, ~1400× at h=22.
- min_p(h) grows much faster than |S_h|.
- No fixed column ±1 through ±19 has temporal period ≤ 500 in 2000 steps.

### Retracted results

- **Proposition 13 [RETRACTED]**: The counting argument ("period p implies ≤ p classes visited") is wrong. The correct machine period is L·p where L (macro-cycle length) can be as large as 2^h, making the bound vacuous. Concrete counterexample: h=6, p=2, word "10" → machine period=8, visits 7 classes.

## The Fundamental Gap

The project has reached the boundary of the known-open problem. The central barrier is:

**One periodic column ↛ two adjacent periodic columns.**

- If we could show that periodicity of a₀ implies periodicity of a₁ (or any finite-state proxy for a₁), then Proposition 2 + left-edge property gives the contradiction.
- The right half is a semi-infinite system (NOT finite-state). Width-K truncations have periods that grow without bound as K → ∞ (verified: K=39 gives period 6258 for p=2).
- This gap is EXACTLY the Erica Jen 1986 barrier. "There is no known way to extend [the two-column result] from two columns to a single column" (Wolfram 2019).

## Open Items

- Find a finite-state "effective second column": an observable that is (a) a finite-state function of c(t) and (b) sufficient for leftward reconstruction.
- Explore speed-of-information arguments: periodic boundary provides O(1) bits/step but the light cone needs O(t) bits at time t.
- Investigate topological entropy incompatibility: Rule 30 has positive topological entropy vs periodic orbit's zero entropy.
- Study the linearized difference propagation system (dropping quadratic d_a·d_b terms).
- Prove the Coverage Hypothesis (all S_h classes visited) for all h — remains interesting even though the counting argument doesn't work.
- Explore whether the parity structure (Obs 11i–11k) or recursive class characterization can yield an inductive coverage proof.