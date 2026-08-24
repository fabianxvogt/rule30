# Finite class and fiber introspection — 2026-08-25

## Result

Extended the repository-local `rule30` predictive-partition facade with two
finite inspection methods:

- `PredictivePartition.class_members(class_id)` returns the immutable encoded
  states in a validated class ID.
- `PredictivePartition.right_truncation_fibers(lower)` groups source class IDs
  by lower-horizon class ID after re-running the existing adjacent-horizon and
  finite well-definedness checks.

The existing `class_id` and `right_truncation_map` behavior is unchanged.

## Bounded evidence

The test suite exhaustively checked every class member and every truncation
fiber at horizons `h = 1..6`, and checked class-ID rejection for negative,
out-of-range, non-integer, null, and boolean inputs. The facade test exercises
both methods through `import rule30`.

The finite Rule 30 implementation checker also remains green through `h = 13`:

```text
PASS: h=0..13, 16383 state encodings and 32766 boundary transitions checked
```

## Classification and limits

**INCREMENTAL / EMPIRICAL.** These are finite API and implementation checks.
They do not establish an infinite-horizon quotient, prove a general fiber-size
bound, make same-horizon transitions deterministic, or say anything about
center-column periodicity. The partition and introspection remain exponential
in the horizon and are intended for small bounded checks.

## Changed paths

- `experiments/rule30_successor.py` — added validated class and fiber methods.
- `tests/test_rule30_successor.py` — exhaustive class, fiber, and validation regressions.
- `tests/test_rule30_facade.py` — facade introspection regression.
- `README.md`, `ROADMAP.md`, `docs/README.md` — documented the bounded surface.
- This report — evidence, classification, and explicit limits.
