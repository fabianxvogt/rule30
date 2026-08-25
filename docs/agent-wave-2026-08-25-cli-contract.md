# Bounded sibling-fiber CLI contract

## Gap and change

The Python regression already exercised the raw audit through `h = 13`, but
the documented command boundary was not covered: a change to argument parsing,
the distance-report switch, or the over-cap error path could have broken
reproduction while leaving the API tests green.

`tests/test_sibling_fiber_parity.py` now invokes the script in a subprocess at
`h = 3` and checks that the pairwise report is emitted, that the output states
the hard `h = 13` cap, and that stderr is empty. It also invokes the script
with `h = 14` and checks for status 2, an empty stdout stream, and the explicit
`[0, 13]` validation message. The over-cap case is rejected before the audit
starts, so it computes no horizon above 13.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_report_and_cap_contract
```

The full h=13 table and pairwise values remain covered by the existing Python
audit regression. This CLI check is a command-boundary regression at a small
horizon; it does not claim to be a second h=13 computation.

## Limits and classification

This is **EMPIRICAL / INCREMENTAL**, bounded to the existing raw tuple-state
audit. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
