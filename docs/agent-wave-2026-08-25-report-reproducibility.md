# Bounded CLI report reproducibility

The sibling-fiber report was audited at the documented implementation cap,
`h = 13`, in both supported invocation forms:

```text
python3 experiments/sibling_fiber_parity.py
python3 -m experiments.sibling_fiber_parity
```

For each form, both the omitted-reporting default and
`--report-distances` were run with `PYTHONHASHSEED=0` and
`PYTHONHASHSEED=42`. The output bytes were identical across seeds and
invocation forms:

| mode | SHA-256 |
| --- | --- |
| default, h=13 | `01e9507387266101ebce5922341be01b3210edb4c80e6b680dd0661eda1d485c` |
| `--report-distances`, h=13 | `1c2e5f3ec1cb6f7de7de55a2d167ef4912128f3da0bc9135f6646dc0631981d4` |

The regression in `tests/test_sibling_fiber_parity.py` uses the smaller
`h=3` envelope to check all four combinations of script/module invocation
and default/distance-reporting mode under both seeds. It pins the complete
output lengths and SHA-256 digests, so ordering changes fail at the CLI
boundary without repeating the slower h=13 audit for every test case.

This is **EMPIRICAL / INCREMENTAL; bounded** evidence about finite report
serialization. It makes no claim beyond `h=13`, about an infinite quotient,
center-column coverage, or periodicity.
