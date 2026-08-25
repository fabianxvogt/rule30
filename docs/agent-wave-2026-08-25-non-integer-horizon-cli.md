# Non-integer horizon CLI contract

## Gap and change

The sibling-fiber CLI already rejected negative, over-cap, and otherwise
out-of-range integer horizons, but its subprocess contract did not cover a
malformed horizon token. `tests/test_sibling_fiber_parity.py` now invokes the
documented command with `--max-horizon not-an-integer` and distance reporting
enabled. It locks status 2, empty stdout, and the exact `argparse` usage and
diagnostic output.

This exercises the parser boundary before `audit()` receives a value, so a
malformed token cannot start a finite computation or emit a partial report.
The accepted finite range and implementation cap remain `0 <= h <= 13`.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_rejects_non_integer_horizon_contract
```

The existing h=-1, h=0, h=3, h=13, and h=14 subprocess checks remain
unchanged.

## Limits and classification

This is **EMPIRICAL / INCREMENTAL**, bounded to the raw tuple-state CLI
contract. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
