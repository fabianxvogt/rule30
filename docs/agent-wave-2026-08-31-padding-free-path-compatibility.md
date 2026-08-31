# Padding-free Rule 30 path compatibility (2026-08-31)

**Classification:** `FORMAL` finite theorem / `EMPIRICAL` oracle agreement; `INCREMENTAL`.

## Exact bounded claim

Use the repository convention

\[
f(l,c,r)=l\mathbin{\mathrm{xor}}(c\mathbin{\mathrm{or}}r).
\]

For given fixed semi-infinite right halves \(X\ne Y\) and a fixed boundary
word \(b=(b_0,b_1)\) driving both, write \(X\sim_bY\) when their
boundary-adjacent cells agree before the first update and after each of two
updates:

\[
X\sim_bY\iff\forall t\in\{0,1,2\}: X_0^b(t)=Y_0^b(t).
\]

The counterexample claim is \(\exists X\ne Y,b: X\sim_bY\).

The witnesses are fixed across time; this is not a separately chosen hidden
extension at every observation. The independent oracle updates only cells whose
complete causal neighborhoods remain in the supplied initial prefix and shortens
the tuple after each update. It never appends a right exterior cell, so the
claim does not use finite zero padding.

Against \(X=0^\infty\), write the two hidden causal bits of \(Y\) as
\(e=(e_1,e_2)\), with \(Y_0=0\). Exact compatibility through two updates is

\[
e_1=0\quad\text{and}\quad (\neg b_0)\land e_2=0.
\]

Consequently,

\[
\operatorname{Comp}_2(b_0,b_1)=
\begin{cases}
\{00\}, & b_0=0,\\
\{00,01\}, & b_0=1.
\end{cases}
\]

The non-zero all-zero-baseline-relative witness is the raw-state pair `000`
and `001`. With
boundary `11`, both give the observed trace `010`. The differing final initial
bit is on the two-update backward light-cone boundary: it changes the adjacent
hidden cell after the first update, but the common observed one masks that
change through Rule 30's OR gate. This is not an out-of-cone difference.

The witness is minimal relative to \(X=0^\infty\) with initial observed
cell zero. At one update, matching that baseline forces the only causal hidden
bit to zero. At two updates, the first boundary bit being one makes the second
constraint insensitive to `e2`; `b1` does not change the compatibility fiber.

## Independent oracle and production control

`experiments/padding_free_path_compatibility.py` freezes all four two-bit
boundary words and all four two-bit hidden prefixes: exactly 16 cases. Its raw
oracle uses a literal eight-row Rule 30 truth table and shrinking tuples. Every
raw trace is compared with the production `response_trace` result, and any
mismatch raises immediately rather than emitting a result.

The all-input predictive-class control uses horizon 3, whose response convention
has the same three samples. Encoded raw states `0` (`000`) and `4` (`001`) are
in distinct production \(q_3\) classes. Boundary `00` separates their traces as
`000` and `001`, while boundary `11` gives the compatible `010`/`010` pair.
Thus fixed-path compatibility is strictly coarser than the existing finite
observer equivalence, which quantifies over every boundary word. Finite class
coverage cannot establish hidden-state identifiability along one realized path.

The bounded run reports:

- 16/16 raw-state traces agreeing with production;
- exact fibers `00:{00}`, `01:{00}`, `10:{00,01}`, `11:{00,01}`;
- the all-zero-baseline-relative compatible `000`/`001` witness under `11`;
- the separating `000`/`001` control traces under `00`;
- distinct production predictive classes for encoded states 0 and 4.

Reproduce from the project root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -S experiments/padding_free_path_compatibility.py
```

The focused contract is in
`tests/test_padding_free_path_compatibility.py`.

## Interpretation and stop condition

This is a finite counterexample to hidden-cone identifiability from a single
realized adjacent-cell path. It is not an infinite compatible pair, a growing
compatibility-fiber bound, an extension-rank table, a recurrence, a class
coverage result, an aperiodicity result, or a novelty claim. The local masking
mechanism is already latent in Rule 30's truth table, so `INCREMENTAL` is the
strongest warranted classification.

Stop on any raw/production disagreement, any failure of the 16 symbolic cases,
or failure of the predictive-class separating control. Do not expand the
horizon or enumerate more trajectories. Reopen only for a proved construction
valid for every finite horizon under one explicitly quantified boundary
sequence, or a parameterized theorem bounding the compatibility-fiber size.
