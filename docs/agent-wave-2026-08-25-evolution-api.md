# Evolution API wave — 2026-08-25

## Result

Added `evolve_integer_state(state, boundary_bits, horizon)` beside the extracted
`integer_successor` API. It consumes a boundary word once from left to right,
delegates each update to the existing one-step function, and returns the final
width-limited encoded state. An empty boundary word preserves the supplied
valid state.

The helper is intentionally small and dependency-light: it uses only the
standard-library `Iterable` type and adds no input validation or package
metadata. The existing checker CLI and its exact output remain unchanged.

## Bounded evidence

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_successor
Ran 7 tests ...
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked

git diff --check
```

The new regression enumerates horizons `h=0..6`, every encoded state, and
boundary words of lengths `0..4`, comparing repeated integer evolution with the
existing tuple reference. Separate tests cover empty words and direct
agreement with repeated one-step calls.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This improves reuse and finite implementation
coverage. It does not prove the successor identity beyond the tested finite
bounds, establish a public package API, or make any claim about infinite Rule
30 behavior or center-column periodicity.

## Changed paths

- `experiments/rule30_successor.py` — added `evolve_integer_state`.
- `tests/test_rule30_successor.py` — added empty-word, delegation, and bounded
  multi-step regression coverage.
- `ROADMAP.md` — recorded the completed incremental API step.
- `docs/agent-wave-2026-08-25-evolution-api.md` — this evidence report.
