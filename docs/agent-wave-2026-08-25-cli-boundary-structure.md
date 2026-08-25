# Lower-boundary finite CLI report structure

The sibling-fiber CLI was audited at the two small finite report boundaries,
`h=0` and `h=3`, with and without `--report-distances`. This complements the
existing byte snapshots and hash-seed/invocation matrix by checking the report
as a structured finite document.

## Observed contract

- Both modes begin with the requested horizon and `implementation hard cap=13`
  wording, followed by the same summary header and separator.
- At `h=0`, the summary table has no rows. Without distance reporting the limits
  line follows the separator directly; with distance reporting there is exactly
  one blank line, an empty pair section, and its header before the limits line.
- At `h=3`, summary rows are ordered `1, 2, 3` in both modes. Distance rows are
  ordered by `(horizon, first_state, second_state)` as `1, 2, 3, 3`; omitting
  distance reporting omits the pair section entirely.
- Every mode ends with the same explicit `h=13` implementation cap and wording
  that makes no claim for larger horizons, an infinite quotient, center-column
  coverage, or periodicity.

## Regression and limits

`tests/test_sibling_fiber_parity.py` now runs all four bounded combinations and
checks section boundaries, row ordering, empty-section behavior, shared summary
rows, and exact cap/limits wording. The check computes only `h=0` or `h=3`; it
does not extend the `h<=13` cap or make an asymptotic claim.

Classification: **EMPIRICAL / INCREMENTAL; bounded**.
