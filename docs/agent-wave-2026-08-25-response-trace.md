# Response-trace API wave — 2026-08-25

## Result

Added `response_trace(state, boundary_bits, horizon)` to
`experiments/rule30_successor.py`. It emits the encoded state’s leftmost bit
before each boundary-driven update, then applies that boundary bit. This is
the integer counterpart of the observation trace used by the predictive-state
experiments, while leaving those exploratory scripts unchanged.

The helper consumes a boundary iterable once and returns an immutable tuple.
It intentionally keeps the existing validation-free contract of
`integer_successor` and `evolve_integer_state`.

## Bounded evidence

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_successor
Ran 10 tests ...
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked

git diff --check
```

The new finite regression enumerates every encoded state at horizons `h=0..6`
and every boundary word of length `h`. It compares the response signatures
produced by the integer API with the tuple reference and checks the observed
class counts `1, 2, 3, 5, 7, 11, 16` at those finite horizons.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This creates a small reusable observation seam and
guards a finite predictive-state partition. It does not prove the class-count
sequence beyond `h=6`, establish quotient behavior at infinite horizon, or
make any claim about Rule 30 center-column periodicity.

## Changed paths

- `experiments/rule30_successor.py` — added `response_trace`.
- `tests/test_rule30_successor.py` — added response-order, iterator-consumption,
  and finite quotient-partition regressions.
- `ROADMAP.md` — recorded the bounded quotient-facing API step.
- `docs/agent-wave-2026-08-25-response-trace.md` — this evidence report.
