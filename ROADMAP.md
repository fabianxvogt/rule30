# Roadmap

Living plan for the rule30 workspace. Claims are labeled per the research honesty protocol
(FORMAL / EMPIRICAL / REPORTED / SPECULATIVE).

## Now

- Publish this repository publicly (`fabianxvogt/rule30`) with curated experiments, results,
  and honest labeling of proved vs. empirical claims.
- Keep `research/partial-results.md` as the authoritative record of proved statements and the
  Proposition 13 retraction.

## Next

- Promote the predictive-state quotient machinery (`predictive_state_growth.py`,
  `right_half_response_classes.py`, `fast_class_coverage2.py`) into a small, documented,
  tested package with a clean API instead of standalone scripts.
- Push class coverage / quotient computations beyond h = 22 (needs longer generated columns;
  C generator makes ~10^8 bits feasible).
- Write up the negative results properly: the vacuity of coverage-based counting bounds after
  the Proposition 13 correction, and the non-stabilization of truncation periods.
- Prove or refute the Coverage Hypothesis (all S_h classes visited) — now interesting in its
  own right, independent of the counting argument.
- Investigate the even/odd parity pattern in ρ-fiber sibling structure (Obs 11i–11k): look for
  an inductive coverage proof via τ_b/ρ_h cross-horizon maps.

## Later

- Formalize candidate "bridge criteria" from `research/bridge-criteria.md` into checkable
  conditions on finite-state observers.
- Explore the speed-of-information argument: periodic boundary supplies O(1) bits/step while
  the light cone appears to require O(t) bits at time t. [SPECULATIVE direction]
- Explore topological-entropy incompatibility arguments (positive entropy vs. zero-entropy
  periodic orbit). [SPECULATIVE direction]
- Connect the exp(C·h^{2/3}) growth law to any known complexity results. [SPECULATIVE]

## Done

- Verified open status of Wolfram Prize Problem 1 against primary sources (2019 announcement,
  prize site). [REPORTED]
- Self-contained proof of the two-column barrier (Prop 2 + Cor 3 + left-edge property). [FORMAL]
- |S_h| → ∞ proved; growth ≈ exp(C·h^{2/3}) measured through h = 21. [FORMAL divergence /
  EMPIRICAL law]
- Theorem 11: full reachability from all-zeros (proof + BFS to h = 20). [FORMAL]
- Theorem 11+: universal bijectivity via Front Propagation Lemma and GF(2) Jacobian. [FORMAL]
- Recursive characterization of predictive classes; commuting squares; fiber structure to
  h = 21. [FORMAL structure, EMPIRICAL tables]
- Eventual periodicity survives finite-state observation (Prop 7). [FORMAL]
- Center column uniquely determines right half-plane (Prop 9); gap is memory, not information.
  [FORMAL]
- Full class coverage verified for h ≤ 22. [EMPIRICAL]
- Proposition 13 retracted with concrete counterexamples; error fully characterized.
- Periodicity sweeps: no periods ≤ 2048 on 1M bits (raw, xor-shift, running-parity); no fixed
  column ±1…±19 with period ≤ 500. [EMPIRICAL]

- 2026-08-22: added `experiments/bitwise_successor_check.py`; exhaustive finite-width validation passed for h=0..12 (8,191 encodings and 16,382 transitions). [EMPIRICAL implementation check]
