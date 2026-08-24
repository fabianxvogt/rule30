# Predictive-partition API wave — 2026-08-25

## Result

Added `response_signature(state, horizon)` and `predictive_partition(horizon)`
to `experiments/rule30_successor.py`. The signature enumerates every binary
boundary word of the finite length `horizon` and delegates each observation to
the existing `response_trace` API. The partition then groups every encoded
width-`horizon` state by equal signatures and exposes deterministic class
membership through `PredictivePartition.class_id`.

The class ordering is only an implementation convenience: states are scanned
in ascending integer order, so the first state in each class determines its
identifier. The identifiers are not mathematical labels.

## Bounded evidence

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_successor
Ran 13 tests ...
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked

git diff --check
```

The new tests enumerate all states and all state pairs for horizons `h=0..6`.
They verify class counts `1, 2, 3, 5, 7, 11, 16`, that the classes form a
partition of the encoded state space, and that equal class IDs are exactly
equivalent to equal finite response signatures.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a reusable finite-width quotient seam. It
does not establish an infinite-horizon equivalence relation, prove the class
counts beyond `h=6`, establish a coherent transition API between horizons, or
make any claim about Rule 30 center-column periodicity. The exhaustive
implementation is exponential in `horizon` and is intended for small checks.

## Changed paths

- `experiments/rule30_successor.py` — added response signatures and the finite partition object.
- `tests/test_rule30_successor.py` — added partition exactness and validation regressions.
- `ROADMAP.md` — recorded the bounded API step.
- `docs/agent-wave-2026-08-25-predictive-partition-api.md` — this evidence report.
