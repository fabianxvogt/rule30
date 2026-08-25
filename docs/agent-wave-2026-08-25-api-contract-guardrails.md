# Finite API contract guardrails — 2026-08-25

## Result

The repository-local `rule30` facade exposed finite transition and observation
helpers whose documented preconditions were not enforced consistently. An
out-of-range encoded state was silently truncated by `integer_successor`, a
non-binary boundary value could alter the transition, and empty boundary words
allowed `evolve_integer_state` and `response_trace` to skip all validation.

The shared finite-domain checks now require a non-negative integer horizon, an
integer state in `0 <= state < 2**horizon`, and an actual integer boundary bit
equal to `0` or `1` (booleans are rejected). The checks run before consuming an
iterable, so invalid initial inputs cannot be hidden behind an empty word.
Valid transitions are unchanged; the existing checker and the independent raw
h=13 audit retain their contracts.

## Bounded evidence

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test*.py'
Ran ...
OK

PYTHONDONTWRITEBYTECODE=1 python3 experiments/bitwise_successor_check.py --max-horizon 13
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked

PYTHONDONTWRITEBYTECODE=1 python3 experiments/sibling_fiber_parity.py --max-horizon 13
... h=13 ...

git diff --check
```

The unit regression covers negative, non-integral, and boolean horizons;
negative and out-of-range states; non-binary boundary bits; and empty-word
validation. The separate raw sibling-fiber audit remains package-independent
and bounded at `h=13`.

## Classification and limits

**INCREMENTAL / EMPIRICAL.** This is a finite input-contract correction, not a
change to the Rule 30 transition for valid inputs. It does not cap the public
partition builder, validate research claims beyond the tested finite cases, or
make an infinite-horizon, center-column, or periodicity claim.

## Changed paths

- `experiments/rule30_successor.py` — shared finite-domain validation.
- `tests/test_rule30_successor.py` — malformed-input and empty-word regressions.
- `README.md`, `docs/README.md`, `ROADMAP.md` — current contract and status.
