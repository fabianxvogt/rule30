# Bounded package facade — 2026-08-25

## Result

Added a repository-local `rule30` package facade for the cohesive bounded
transition and predictive-partition helpers:

```python
from rule30 import predictive_partition, response_signature

partition = predictive_partition(6)
signature = response_signature(0b010101, 6)
```

The facade re-exports `integer_successor`, `evolve_integer_state`,
`response_trace`, `response_signature`, `predictive_partition`, and
`PredictivePartition`.  Their implementation remains in
`experiments/rule30_successor.py`, so existing experiment imports and scripts
are unchanged.  The larger exploratory experiment collection remains outside
the facade.

## Bounded evidence

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_facade
Ran 4 tests ...
OK

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_successor
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked
```

The facade tests verify the public export list, object identity with the
existing module, a bounded partition workflow, and compatibility of the old
import path.  `git diff --check` also passes.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is an import-path and integration change. It
does not move or delete experiments, make the finite partition infinite, prove
any theorem, or make a claim about center-column periodicity. The exhaustive
partition remains exponential in `horizon` and is intended for small finite
checks.
