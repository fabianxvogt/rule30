# Finite-to-unbounded trajectory bridge (2026-08-25)

Classification: **INCREMENTAL / EMPIRICAL with FORMAL finite lemmas**. This
report attacks the precise candidate bridge

> for every `h`, the center-driven finite orbit from `0^h` visits every
> response class in `q_h`, with first-visit bound `B(h)=2^(h+1)`.

It does not claim eventual coverage, an infinite quotient, or center-column
aperiodicity.

## Exact profiles and the predeclared bound

`experiments/trajectory_first_visit_profile.py` extracts the complete
class-ID-indexed first-visit tuple from the retained center-column fixtures.
It records `null` for classes not seen, hashes the binary input and each
profile, checks the first 256 bits against the slow row generator, and consumes
exactly `N-1` boundary bits for `N` recorded states. The generated profile
artifacts are:

- `results/trajectory-first-visit-1000000-h20.json` — input length 1,000,001,
  input SHA-256 `4113d4e32ea28b88650275495c8d762a5293212b0affa32046ad46627a656912`;
- `results/trajectory-first-visit-300000-h20.json` — input length 300,001,
  input SHA-256 `e96390915ef4fb2e694fb6adf606474bf700205f0143cc0161b041d4074c327d`.

The profile extractor SHA-256 is
`db102d126b675449fdafc8598d440bfa031e5e9423e2196d03925f1107469036`.
The one-million-bit artifact SHA-256 is
`b3606130015e2825bfff14deeaaed4f3e3457517fb5a95bbf3739ad6c06a929b`.

For the 1,000,001-state run, every class through `h=20` is observed. The
maximum first visits (the saturation times) and bound status are:

| h | `|q_h|` | max first visit | `B(h)` | result |
|---:|---:|---:|---:|:---|
| 0 | 1 | 0 | 2 | pass |
| 1 | 2 | 1 | 4 | pass |
| 2 | 3 | 2 | 8 | pass |
| 3 | 5 | 14 | 16 | pass |
| 4 | 7 | 6 | 32 | pass |
| 5 | 11 | **80** | **64** | **FAIL** |
| 6 | 16 | 102 | 128 | pass |
| 7 | 25 | 211 | 256 | pass |
| 8 | 35 | 211 | 512 | pass |
| 9 | 52 | 274 | 1024 | pass |
| 10 | 71 | 729 | 2048 | pass |
| 11 | 104 | **5165** | **4096** | **FAIL** |
| 12 | 141 | 2155 | 8192 | pass |
| 13 | 203 | 9742 | 16384 | pass |
| 14 | 272 | 19171 | 32768 | pass |
| 15 | 387 | 26833 | 65536 | pass |
| 16 | 517 | 104527 | 131072 | pass |
| 17 | 733 | 203477 | 262144 | pass |
| 18 | 971 | 429241 | 524288 | pass |
| 19 | 1364 | 658581 | 1048576 | pass |
| 20 | 1792 | 877606 | 2097152 | pass |

The same `h=5` and `h=11` failures occur in the 300,001-state fixture. That
run is complete through `h=17`, while `h=18,19,20` remain incomplete by 2, 2,
and 10 classes respectively; those rows are correctly marked
`INCOMPLETE_INPUT`, not treated as bound tests.

The exact witnesses are class IDs in the deterministic partition ordering:

- At `h=5`, class `10` first appears at `t=80` as state `00001`. Its parent
  under right truncation is `q_4` class `0` (state `0000`), first seen at
  `t=0`. Thus `80 > B(5)=64` while all 11 classes are covered.
- At `h=11`, class `100` first appears at `t=5165` as state
  `01001001110`. Its parent is `q_10` class `56`, first seen at `t=727`;
  again all 104 classes are covered but `5165 > B(11)=4096`.

Therefore the proposed exponential bound is **refuted as a finite statement
about this exact center trace**. This does not refute the coverage conjecture.

## Formal cross-horizon lemma and its obstruction

Write `π_h(s)=s mod 2^(h-1)` for dropping the highest state bit. Directly from
the local successor formula,

`π_h(F_b^h(s)) = F_b^(h-1)(π_h(s))` for every state `s` and boundary bit `b`.

This is a **FORMAL finite projection lemma**, proved by observing that each
output coordinate `0..h-2` depends only on input coordinates `0..h-2` and the
boundary bit. Consequently, for the same center trace,

`π_h(s_h(t)) = s_(h-1)(t)` for every `t`.

The finite predictive class truncation map `ρ_h:q_h→q_(h-1)` is also
well-defined (exhaustively checked by the existing API), so
`ρ_h(q_h(s_h(t)))=q_(h-1)(s_(h-1)(t))`. This proves only the downward
implication: coverage at `h` implies coverage at `h-1`.

The converse “lift coverage from `h` to `h+1` at the same prefix length” is
false at the smallest nontrivial case. After center prefix `11`, the `h=2`
states at `t=0,1,2` are `00,10,01`, giving all three `q_2` classes. The
`h=3` states are `000,100,010`, giving only classes `0,1,2`; classes `3` and
`4` are absent. The `q_3→q_2` fibers are

```text
q2 class 0 <- q3 classes 0,4
q2 class 1 <- q3 classes 1,3
q2 class 2 <- q3 class 2
```

Class `3` has members `110,101,111`; class `4` has member `001`. Their
parents are already covered, but the child fibers need not be entered at the
same time. This is the sharp finite obstruction to a naive induction from
coverage at one horizon to coverage at the next. The first nontrivial lift
delay is already `q_3` class `4`, first reached at `t=14`, while its parent
`q_2` class `0` was reached at `t=0`.

More generally, every checked `ρ_h` fiber has size 1 or 2. On the one-million
state trace, the largest observed child-minus-parent first-visit delays for
`h=1..13` are:

| h | singleton fibers | doubleton fibers | largest delay | parent→child | times |
|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 1 | 1 | 0→1 | 0→1 |
| 2 | 1 | 1 | 2 | 0→2 | 0→2 |
| 3 | 1 | 2 | 14 | 0→4 | 0→14 |
| 4 | 3 | 2 | 4 | 0→6 | 0→4 |
| 5 | 3 | 4 | 80 | 0→10 | 0→80 |
| 6 | 6 | 5 | 102 | 0→15 | 0→102 |
| 7 | 7 | 9 | 211 | 0→24 | 0→211 |
| 8 | 15 | 10 | 211 | 0→34 | 0→211 |
| 9 | 18 | 17 | 267 | 25→49 | 7→274 |
| 10 | 33 | 19 | 729 | 0→70 | 0→729 |
| 11 | 38 | 33 | 4438 | 56→100 | 727→5165 |
| 12 | 67 | 37 | 2033 | 56→127 | 122→2155 |
| 13 | 79 | 62 | 9605 | 103→196 | 137→9742 |

The fiber structure is therefore compatible with downward projection but gives
no bounded child-selection or synchronized lift. This is the strongest
obstruction found without computing beyond the existing `h=20` trajectory
envelope.

## Verification and literature boundary

The new unit tests pass alongside the existing observer tests:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m unittest \
  tests.test_trajectory_first_visit_profile \
  tests.test_trajectory_restricted_observer
```

The retained first-visit artifacts are regenerated from the project root with:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 \
  experiments/trajectory_first_visit_profile.py \
  --input results/center-column-300000.txt --max-horizon 20 \
  --reference-steps 256 \
  --output results/trajectory-first-visit-300000-h20.json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 \
  experiments/trajectory_first_visit_profile.py \
  --input results/center-column-1000000.txt --max-horizon 20 \
  --reference-steps 256 \
  --output results/trajectory-first-visit-1000000-h20.json
```

Current primary-source checks still identify Problem 1 as open: the [Wolfram
Rule 30 Prizes page](https://rule30prize.org/) (accessed 2026-08-25) asks
whether the center column remains non-periodic. Kopra's primary paper
[A natural class of cellular automata containing fractional multiplication
automata, Wolfram's Rule 30, and many others](https://arxiv.org/abs/2202.13809)
uses rapid left expansivity to prove non-eventual periodicity of suitable
width-2 traces, but leaves the single-column question as the known barrier.
Rowland's primary paper [Local Nested Structure in Rule
30](https://ericrowland.github.io/papers/Local_nested_structure_in_rule_30.pdf)
studies periodic right diagonals and local nestedness, not this
trajectory-restricted predictive-class coverage. These sources provide no
finite-to-unbounded coverage theorem matching the present `q_h` bridge.

## Decision

Do not promote the coverage data to an all-`h` theorem. Retain the downward
projection lemma as a formal finite fact, record the same-prefix lift failure,
and retire `B(h)=2^(h+1)` as a candidate bound. Any next bridge must explain
how the center trace selects both members of every doubleton fiber, with a
quantitative delay bound that survives the explicit `h=5` and `h=11`
counterexamples.
