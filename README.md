# Rule 30 Center Column Research

This workspace is for investigating the claim that the center column of Stephen Wolfram's Rule 30 cellular automaton never repeats.

The current working standard is strict: do not treat this as a solved theorem unless we can produce a defensible proof or identify an established proof in the literature.

## Layout

- `research/` holds notes, conjectures, proof attempts, and experiment logs.
- `experiments/` holds reproducible scripts.
- `results/` holds generated output from runs.

## First Questions

1. What exactly counts as repetition for the center column: eventual periodicity, repeated finite blocks, or exact recurrence of an infinite tail?
2. What initial condition are we fixing? This workspace assumes the standard single black cell in an all-white background.
3. What is already known in the literature about Rule 30 center-column periodicity and randomness?

At present, the main theorem target should be treated as open until disproved by newer literature. See `research/literature.md`.

## Immediate Use

Run the experiment script with Python to generate the center column and test simple periodicity hypotheses.

```bash
python3 experiments/rule30_center_column.py --steps 2000 --report-prefix 128 --max-period 256 --min-repetitions 4
```

Generated files can be written under `results/`.

The same script can also analyze simple local transforms of the center column. For example, this checks the XOR of adjacent bits:

```bash
python3 experiments/rule30_center_column.py --steps 2000 --transform xor-shift --transform-shift 1
```

For a simple stateful transform, this computes the running parity of the sequence:

```bash
python3 experiments/rule30_center_column.py --input results/center-column-1000000.txt --transform running-parity
```

It can also analyze an already saved bit string without recomputing Rule 30:

```bash
python3 experiments/rule30_center_column.py --input results/center-column-1000000.txt --max-period 2048 --min-repetitions 8
```

For exploratory search over tiny finite-state observers applied to a saved bit string:

```bash
python3 experiments/search_finite_state_observers.py --input results/center-column-1000000.txt --states 2 --prefix-length 200000
```

For a reconstruction-aware family of observers, compare finite-width right-half simulations driven by the center column against the exact adjacent right column:

```bash
python3 experiments/truncated_right_half_observer.py --input results/center-column-1000000.txt --prefix-length 4000 --max-width 12
```

For a quotient-style compression test, compute behavioral equivalence classes of width-`h` right-half states under all boundary words of length `h`:

```bash
python3 experiments/right_half_response_classes.py --horizon 8
```

To check whether those quotient classes update coherently across horizons under the next boundary bit:

```bash
python3 experiments/predictive_state_automaton.py --max-horizon 9
```

To see how many predictive classes are actually visited along the real center-column trajectory:

```bash
python3 experiments/predictive_state_trace.py --input results/center-column-1000000.txt --horizon 10 --steps 5000
```