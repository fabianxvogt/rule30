# Roadmap

Living plan for the rule30 workspace. Claims are labeled per the research honesty protocol
(FORMAL / EMPIRICAL / REPORTED / SPECULATIVE).

## Now

- [x] Publish this repository publicly (`fabianxvogt/rule30`) with curated experiments, results,
  and honest labeling of proved vs. empirical claims. (Public remote and push-clean
  state verified 2026-08-25.)
- Keep `research/partial-results.md` as the authoritative record of proved statements and the
  Proposition 13 retraction.

## Next

- Evaluate any future distinct bounded API seams in `right_half_response_classes.py` and
  `predictive_state_growth.py`; their finite response-signature and recursive-partition cores
  are already represented by the package. Do not package CLI-only reports without a separate,
  dependency-free finite contract.
- Push class coverage / quotient computations beyond h = 22 (needs longer generated columns;
  C generator makes ~10^8 bits feasible).
- [x] Write up the negative results and limits: the vacuity of coverage-based counting bounds
  after the Proposition 13 correction, periodic-input phase audits, and raw sibling-fiber
  evidence through `h=13` (`research/negative-results-limits.md`).
- Prove or refute the Coverage Hypothesis (all S_h classes visited) — now interesting in its
  own right, independent of the counting argument.
- Keep the bounded raw sibling-fiber parity check at its explicit h=13 cap; no infinite claim is
  implied.

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
- 2026-08-25: added the finite same-horizon set-valued transition relation, exhaustively checked for every state and boundary bit through h = 6; preserves observed class nondeterminism and makes no infinite-horizon or deterministic-automaton claim. [EMPIRICAL implementation check]
- 2026-08-25: promoted the finite first-visit coverage profile from `fast_class_coverage2.py`, exhaustively checked for every state and boundary word through h = 6 and word lengths 0..4; it reports only the supplied finite trajectory and makes no center-column or eventual-coverage claim. [EMPIRICAL implementation check]
- 2026-08-25: closed a finite API contract gap by validating horizons, encoded
  states, and boundary bits in the public transition/observation helpers,
  including empty boundary words; valid outputs and the checker CLI remain
  unchanged. [EMPIRICAL, INCREMENTAL]
- 2026-08-25: reconciled the public-publication checkbox with the verified GitHub
  remote and push-clean state. [EMPIRICAL publication check]
- 2026-08-25: added an exact finite macro-cycle coverage experiment for primitive
  periodic boundary words. The default h=6, periods 1..3 run covers 640
  initial-state/word pairs and reports phase-lifted machine-cycle classes;
  word `10` has machine period 8 and visits 7 of 16 classes. [EMPIRICAL,
  bounded; no center-column or infinite-horizon claim]
- 2026-08-25: independently audited the phase-lifted cycle decomposition through
  h=7 and primitive word lengths 1..4 (5,610 cases), corrected a mid-word
  phase-alignment error in pre-cycle class counts, and recorded the minimal
  h=1 constant-input counterexample to Proposition 13. [EMPIRICAL,
  INCREMENTAL; bounded]
- 2026-08-25: bounded phase-coverage consistency probe found a primitive
  period-2 word (`01`) whose h=3 phase-lifted eventual cycle visits all five
  finite predictive classes, while macro-boundary samples see four. This is
  incremental empirical evidence against repairing Proposition 13 by requiring
  periodic drivers to miss a class; no center-column claim. [EMPIRICAL,
  INCREMENTAL; bounded]
- 2026-08-25: completed the documented h=4 extension through primitive boundary
  lengths 1..5 and all 16 initial states. Across 832 exact phase-lifted cycle
  observations, the best coverage remained 6/7; the length-5 slice also tops
  out at 6/7. Added a focused regression and concise bounded report. [EMPIRICAL,
  INCREMENTAL; bounded]
- 2026-08-25: replaced the package-coupled sibling-fiber parity check with a raw tuple-state
  audit and extended its explicit cap by one step through h=12. The compact exact-signature run
  enumerates at most 4096 raw states, preserves the h≤11 table, and adds a tuple-reference
  regression through h=4; no infinite-horizon or center-column claim is implied.
  [EMPIRICAL, bounded]
- 2026-08-25: extended the independent raw sibling-fiber audit by exactly one bounded step to
  h=13 after a 55.63-second / 252,231,680-byte peak-RSS preflight. The new row has 203 classes,
  79 singleton and 62 doubleton fibers, and preserves the odd-horizon one-child-sharing parity;
  no qualitative parity change or infinite-horizon claim is implied. [EMPIRICAL, bounded]
- 2026-08-25: corrected the public fast-coverage reproduction command to pass an explicit h=13
  bound and the tracked 100,001-bit fixture; the bounded run covered all 203 classes at step
  9,742. [EMPIRICAL, INCREMENTAL]
- 2026-08-25: recorded a bounded raw-signature distance observation: each doubleton pair
  differs on exactly `2^(floor(h/2)+1)` boundary words through h=13, with a regression over
  the compact audit result; the direct tuple-state cross-check remains smaller and no theorem
  or independent second h=13 recomputation is claimed. [EMPIRICAL, bounded]
- 2026-08-25: reviewed the finite signature-distance observation. The existing child-sharing
  data gives a conditional block-decomposition explanation through h=13, but no counterexample,
  asymptotic claim, or center-column bridge; this review motivated the subsequent pairwise
  child-distance check. [EMPIRICAL review, bounded]
- 2026-08-25: added the bounded pairwise child-distance regression and exact CLI report. All 202
  doubleton pairs through h=13 are compared; the h=1 unequal-leading-bit case is preserved as an
  explicit exception, and all 201 pairs for h>=2 satisfy the finite decomposition. [EMPIRICAL,
  INCREMENTAL; bounded]
- 2026-08-25: added a subprocess regression for the documented sibling-fiber CLI: a bounded
  distance report must include the explicit h=13 limit, while h=14 is rejected before the audit
  starts. This closes command-boundary reproducibility coverage without computing beyond h=13.
  [EMPIRICAL, INCREMENTAL; bounded]
- 2026-08-25: tightened the sibling-fiber CLI boundary contract by exercising the exact accepted
  h=13 cap through a subprocess, checking the h=13 `203 / 79 / 62` row, and making the output
  identify both the requested run bound and the implementation hard cap. h=14 remains rejected
  before computation; no horizon above h=13 is run. [EMPIRICAL, INCREMENTAL; bounded]
