# Default sibling-fiber CLI contract — 2026-08-25

## Gap and result

The sibling-fiber audit had exact subprocess coverage for explicit horizons and
for malformed or out-of-range `--max-horizon` values, but not for the
documented command with all flags omitted. The new regression invokes
`experiments/sibling_fiber_parity.py` with no arguments and locks the key
finite-output contract.

The omitted-flag command uses the existing default `h=13`, succeeds with an
empty stderr stream, emits the full bounded summary through h=13, and does not
print pairwise distance rows because `--report-distances` was not supplied.
This is a regression-only contract clarification; no computation above h=13
was added.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_omitted_flags_use_bounded_default_without_distances
```

The existing explicit h=0, h=3, h=13, h=14, negative, and non-integer CLI
checks remain unchanged.

## Limits and classification

This is **EMPIRICAL / INCREMENTAL**, bounded to the raw tuple-state audit. It
makes no claim for larger horizons, an infinite quotient, center-column
coverage, or periodicity.
