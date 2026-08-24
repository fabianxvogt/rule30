# Roadmap

Living plan for the rule30 workspace. Claims are labeled per the research honesty protocol
(FORMAL / EMPIRICAL / REPORTED / SPECULATIVE).

## Now

- Publish this repository publicly (`fabianxvogt/rule30`) with curated experiments, results,
  and honest labeling of proved vs. empirical claims.
- Keep `research/partial-results.md` as the authoritative record of proved statements and the
  Proposition 13 retraction.

## Next

- Promote the remaining predictive-state quotient machinery (`predictive_state_growth.py`,
  `right_half_response_classes.py`, `fast_class_coverage2.py`) beyond the bounded transition,
  partition, and cross-horizon truncation facade into a small, documented, tested package with
  a clean API instead of standalone scripts.
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
- 2026-08-24: extended the integer-successor validation through h=13 (16,383 encodings and 32,766 transitions), with a bounded `--max-horizon` CLI option. [EMPIRICAL implementation check]
- 2026-08-25: added a dependency-free multi-step integer evolution helper, with bounded regression coverage against the tuple reference. [EMPIRICAL implementation check]
- 2026-08-25: added an integer response-trace API and finite quotient-partition regression through h = 6. [EMPIRICAL implementation check]
- 2026-08-25: added a deterministic finite-horizon predictive partition API built from response signatures, with exhaustive regression through h = 6. [EMPIRICAL implementation check]
- 2026-08-25: added the repository-local `rule30` facade for the bounded transition and predictive-partition helpers; existing experiment imports remain supported. [EMPIRICAL integration check]
- 2026-08-25: added a finite cross-horizon right-truncation map on predictive partitions, exhaustively checked through h = 6; no infinite-horizon quotient claim. [EMPIRICAL implementation check]
- 2026-08-25: added validated finite class-member and right-truncation-fiber introspection, exhaustively checked through h = 6; no infinite-horizon quotient claim. [EMPIRICAL implementation check]
- 2026-08-25: added the finite boundary-driven nested transition map from `S_h` to `S_{h-1}`, exhaustively checked for both boundary bits through h = 6; no same-horizon or infinite-horizon transition claim. [EMPIRICAL implementation check]
- 2026-08-25: moved the recursive finite predictive-partition construction into the reusable API, with exhaustive state coverage and the known class-count table reproduced through h = 11; no infinite-horizon quotient claim. [EMPIRICAL implementation check]
- 2026-08-25: added a finite `PredictivePartition.class_trace` helper for reproducible class-coverage traces from bounded boundary words, exhaustively checked through h = 6 and word lengths 0..4; no eventual-coverage or infinite-horizon claim. [EMPIRICAL implementation check]
