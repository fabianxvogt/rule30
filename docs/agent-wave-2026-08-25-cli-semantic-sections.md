# Finite CLI semantic section audit

The sibling-fiber CLI was audited at the explicit finite boundaries `h=0`,
`h=3`, and `h=13`, with and without `--report-distances`. The audit went
beyond byte snapshots and section-shape checks by parsing every emitted row
and comparing it with the corresponding bounded `AuditResult` produced by the
raw tuple-state implementation.

## Verified contract

- Every invocation reports the requested bound and the fixed implementation
  cap `h=13` in the bounds line and the same finite-limits line.
- Summary rows are complete, ordered, and field-for-field identical to the
  finite audit result: no rows at `h=0`, three rows at `h=3`, and all thirteen
  rows at `h=13`.
- Without distance reporting, the report contains no blank separator, pair
  title, pair header, or pair rows.
- With distance reporting, the report has exactly one blank separator, one
  pair title/header, and every doubleton-fiber pair row in canonical audit
  order: zero rows at `h=0`, four at `h=3`, and 202 at `h=13`.
- The summary prefix and limits metadata are identical between the two modes
  for each explicit bound.

No runtime defect was reproduced; this is a precise serialization regression.
It remains **EMPIRICAL / INCREMENTAL; bounded**: it computes only through the
existing `h<=13` cap and makes no claim about an infinite quotient,
center-column coverage, or periodicity.

## Reproduction

From the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_sibling_fiber_parity.SiblingFiberParityTests.test_cli_explicit_boundary_reports_match_finite_audit_sections
```
