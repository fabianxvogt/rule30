# Bounded sibling-fiber CLI contract

## Gap and change

The Python regression already exercised the raw audit through `h = 13`, but
the documented command boundary was not covered: a change to argument parsing,
the distance-report switch, or the over-cap error path could have broken
reproduction while leaving the API tests green.

`tests/test_sibling_fiber_parity.py` now invokes the script in a subprocess at
`h = 0` with distance reporting enabled and checks the complete stdout
byte-for-byte. This locks the lower finite boundary: the empty audit produces
no horizon rows or pair rows, but still emits the bounds, section headers, and
finite-limit statement without writing to stderr. The regression also runs at
`h = 3` and checks the complete stdout byte-for-byte, including the table,
pairwise rows, and finite-limit statement. Pairwise rows are explicitly sorted
by `(horizon, first_state, second_state)` before they enter the public
`AuditResult`, so the textual order does not depend on dictionary insertion
order inside the bounded grouping implementation. It exercises the exact
public boundary `h = 13`, checking that the omitted default and explicit
`--max-horizon 13` distance-report invocations are byte-identical, reproduce
the `203 / 79 / 62` row, and identify both the requested run bound and the
implementation hard cap in their output. Finally, it invokes the script with
`h = 14` and checks for status 2, an empty stdout stream, and the explicit
`[0, 13]` validation message. The over-cap case is rejected before the audit
starts, so it computes no horizon above 13.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_report_and_cap_contract
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_zero_horizon_contract
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_distance_report_default_and_explicit_cap_are_identical
```

The full h=13 table and pairwise values remain covered by the existing Python
audit regression. The subprocess boundary check now verifies the exact cap as
well as byte-stable zero- and three-horizon report runs; it is still not a
second h=13 implementation. Independent bounded probes found identical output
across different Python hash seeds and script/module invocation forms; the
explicit sort and snapshots make that stability an intentional finite
contract.

The default and explicit-cap distance-report interaction is now pinned as
well. With `PYTHONHASHSEED=0`, both the omitted `--max-horizon` form and the
explicit `--max-horizon 13` form produce the same 20,758-byte UTF-8 report with
SHA-256
`1c2e5f3ec1cb6f7de7de55a2d167ef4912128f3da0bc9135f6646dc0631981d4`:
13 summary rows, 202 pair rows, and 62 pair rows at h=13. The regression
compares those bytes directly. The over-cap subprocess now supplies
`--report-distances` too, so
the distance switch is verified to fail with empty stdout before any h=14
work can begin.

## Limits and classification

This is **EMPIRICAL / INCREMENTAL**, bounded to the existing raw tuple-state
audit. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
