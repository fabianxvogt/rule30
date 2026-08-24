# API cleanup wave — 2026-08-25

## Decision

Extract the integer successor formula into one small reusable module, while
leaving `experiments/bitwise_successor_check.py` as the owner of the existing
CLI, tuple reference, exhaustive enumeration, counters, and error handling.

This is a safe first seam for the roadmap’s package/API cleanup. It is not a
full package conversion. **Classification: INCREMENTAL.**

## Boundary

The new internal API is:

```python
from experiments.rule30_successor import integer_successor

next_state = integer_successor(state, boundary_bit, horizon)
```

Contract:

- `state` uses `state = sum(s[i] << i for i in range(horizon))`; bit 0 is the
  leftmost, boundary-adjacent cell.
- `boundary_bit` is 0 or 1.
- `horizon` is non-negative and `state` is in `0 <= state < 2**horizon`.
- The return value is the width-limited integer Rule 30 successor.
- The function is pure and has no imports beyond the standard language runtime.
- The function intentionally does not add input validation; callers own these
  preconditions. This preserves the checker’s behavior for all inputs it
  already supplies.

Only `integer_successor` crosses the boundary. Encoding/decoding helpers and
the tuple reference remain local to the checker because they are still part of
its validation procedure, not yet a stable package surface.

## Script contract check

The documented script entry point remains unchanged:

```text
python3 experiments/bitwise_successor_check.py
python3 experiments/bitwise_successor_check.py --max-horizon 13
```

The default remains h=12 and the bounded option remains available. The
post-extraction outputs are:

```text
PASS: h=0..12, 8191 state encodings and 16382 boundary transitions checked
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked
```

The checker still compares against `rule30_next_tuple`; only the location of
the integer formula changed. A focused subprocess test also asserts the exact
CLI summary for `--max-horizon 4`.

## Bounded evidence

Commands run from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_rule30_successor.py
....                                                                     [100%]
4 passed in 0.06s

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rule30_successor
Ran 4 tests in 0.047s
OK
```

The focused tests cover zero width, bit orientation, exhaustive agreement with
a tuple reference for h=0..8 (511 states and 1,022 transitions), and exact
CLI output. The existing exhaustive checker independently passes through h=13
(16,383 encodings and 32,766 boundary transitions). `git diff --check` also
passes. No bytecode or generated bulk output was added.

## Explicit non-claims

This change does not:

- prove the integer identity at widths above the checked bounds;
- prove anything about infinite-width Rule 30 behavior or center-column
  periodicity;
- validate predictive-state coverage, bijectivity, or any research theorem;
- establish a public distribution package or a stable external import path;
- complete the roadmap item to package the predictive-state quotient machinery;
- add runtime validation for malformed API inputs.

The tests are finite implementation checks. Agreement with the tuple reference
is evidence about this implementation at bounded widths, not a mathematical
proof about the open Rule 30 problem.

## Packaging recommendation

Keep `experiments/rule30_successor.py` as an internal reusable module for now.
Do not add package metadata or move the larger experiment collection in this
cleanup wave: the surrounding scripts still use direct sibling imports and do
not share a settled package namespace.

When the roadmap’s broader package work is authorized, use this boundary as a
seed and proceed only after these decisions are explicit:

1. Choose a canonical package name and public import path.
2. Decide whether public functions validate `horizon`, `state`, and
   `boundary_bit`, then test that policy deliberately.
3. Move the tuple transition and integer transition together into the package,
   keeping the current script as a compatibility CLI wrapper.
4. Preserve the exact summary format and `--max-horizon` behavior with a
   subprocess test, while testing the package functions directly.
5. Package only the cohesive transition/quotient primitives; leave exploratory
   scripts and generated results outside the public API.

That follow-up would be a separate, broader refactor. The present extraction
is the smallest reusable API boundary that preserves the existing script
contract.

## Changed paths

- `experiments/rule30_successor.py` — new one-function integer successor API.
- `experiments/bitwise_successor_check.py` — imports the extracted function;
  CLI behavior and validation loop remain in place.
- `tests/test_rule30_successor.py` — four bounded API and contract tests.
- `docs/agent-wave-2026-08-25-api.md` — this assessment and recommendation.
