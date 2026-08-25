# Negative lower-horizon CLI contract

## Gap and change

The sibling-fiber CLI already validated its finite horizon through the
existing `_validate_horizon` boundary, and its subprocess tests covered the
valid lower endpoint `h = 0`, the representative report `h = 3`, the accepted
cap `h = 13`, and the over-cap rejection `h = 14`. The negative side of the
same lower boundary had no command-level regression.

`tests/test_sibling_fiber_parity.py` now invokes the documented CLI with
`--max-horizon -1` and distance reporting enabled. It requires status 2,
empty stdout, and the explicit `[0, 13]` validation message. Because the
validator runs before the report is printed, this confirms that a negative
horizon cannot start a finite audit or produce a misleading partial report.
The implementation cap remains `h <= 13`; no negative or over-cap horizon is
computed.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_rejects_negative_horizon_contract
```

The existing h=0, h=3, h=13, and h=14 subprocess checks remain unchanged.

## Limits and classification

This is **EMPIRICAL / INCREMENTAL**, bounded to the raw tuple-state CLI
contract. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
