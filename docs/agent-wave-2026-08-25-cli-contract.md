# Bounded sibling-fiber CLI contract

## Gap and change

The Python regression already exercised the raw audit through `h = 13`, but
the documented command boundary was not covered: a change to argument parsing,
the distance-report switch, or the over-cap error path could have broken
reproduction while leaving the API tests green.

`tests/test_sibling_fiber_parity.py` now invokes the script in a subprocess at
`h = 3` and checks the complete stdout byte-for-byte, including the table,
pairwise rows, and finite-limit statement. Pairwise rows are explicitly sorted
by `(horizon, first_state, second_state)` before they enter the public
`AuditResult`, so the textual order does not depend on dictionary insertion
order inside the bounded grouping implementation. The test also checks that
stderr is empty. It exercises the exact public boundary `h = 13`, checking that
the run succeeds, reproduces the `203 / 79 / 62` row, and identifies both the
requested run bound and the implementation hard cap in its output. Finally, it
invokes the script with `h = 14` and checks for status 2, an empty stdout
stream, and the explicit `[0, 13]` validation message. The over-cap case is
rejected before the audit starts, so it computes no horizon above 13.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_report_and_cap_contract
```

The full h=13 table and pairwise values remain covered by the existing Python
audit regression. The subprocess boundary check now verifies the exact cap as
well as a byte-stable smaller report run; it is still not a second h=13
implementation. Independent bounded probes found identical output across
different Python hash seeds and script/module invocation forms; the explicit
sort and snapshot make that stability an intentional finite contract.

## Limits and classification

This is **EMPIRICAL / INCREMENTAL**, bounded to the existing raw tuple-state
audit. It makes no claim for larger horizons, an infinite quotient,
center-column coverage, or periodicity.
