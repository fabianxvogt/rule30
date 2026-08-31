#!/usr/bin/env python3
"""Verify the all-zero-baseline-relative Rule 30 path-compatibility witness.

This is deliberately fixed at two updates.  It compares a shrinking causal-cone
oracle, which never supplies a right exterior cell, with the production finite
response and predictive-class APIs.
"""

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rule30 import predictive_partition, response_trace  # noqa: E402

UPDATES = 2
OBSERVER_HORIZON = UPDATES + 1
BASE_EXTENSION = (0, 0)
NONZERO_EXTENSION = (0, 1)
# Literal Rule 30 truth table indexed by the binary neighborhood lcr.
RULE30_OUTPUT = (0, 1, 1, 1, 1, 0, 0, 0)


def raw_rule30(left: int, center: int, right: int) -> int:
    """Evaluate Rule 30 from an explicit truth table, independently of production."""
    return RULE30_OUTPUT[(left << 2) | (center << 1) | right]


def encode(state: tuple[int, ...]) -> int:
    """Encode the boundary-adjacent cell as bit zero."""
    return sum(bit << index for index, bit in enumerate(state))


def shrinking_successor(
    row: tuple[int, ...], boundary_bit: int
) -> tuple[int, ...]:
    """Advance only cells whose complete causal neighborhoods are present."""
    causal_row = (boundary_bit,) + row
    return tuple(
        raw_rule30(causal_row[index], causal_row[index + 1], causal_row[index + 2])
        for index in range(len(row) - 1)
    )


def shrinking_cone_trace(
    extension: tuple[int, int], boundary: tuple[int, int]
) -> tuple[int, int, int]:
    """Return three observations without appending an exterior state value."""
    row = (0,) + extension
    observations = [row[0]]
    for boundary_bit in boundary:
        row = shrinking_successor(row, boundary_bit)
        observations.append(row[0])
    return tuple(observations)  # type: ignore[return-value]


def production_trace(
    extension: tuple[int, int], boundary: tuple[int, int]
) -> tuple[int, ...]:
    """Return the matching production trace at its three-sample convention."""
    state = encode((0,) + extension)
    # response_trace samples before updating.  Its final input is consequently
    # unobserved; zero fixes that irrelevant argument without defining an
    # exterior state cell.
    return response_trace(state, boundary + (0,), OBSERVER_HORIZON)


def expected_extensions(boundary: tuple[int, int]) -> set[tuple[int, int]]:
    """Return the theorem's exact compatibility fiber for this boundary."""
    compatible = {BASE_EXTENSION}
    if boundary[0] == 1:
        compatible.add(NONZERO_EXTENSION)
    return compatible


def evaluate() -> dict[str, object]:
    """Evaluate all 16 frozen cases and fail closed on any disagreement."""
    rows: list[dict[str, object]] = []
    observed_fibers: dict[str, list[str]] = {}
    for boundary in product((0, 1), repeat=UPDATES):
        baseline = shrinking_cone_trace(BASE_EXTENSION, boundary)
        compatible: set[tuple[int, int]] = set()
        for extension in product((0, 1), repeat=UPDATES):
            direct = shrinking_cone_trace(extension, boundary)
            production = production_trace(extension, boundary)
            if direct != production:
                raise AssertionError(
                    "raw-state/production mismatch: "
                    f"boundary={boundary}, extension={extension}, "
                    f"raw={direct}, production={production}"
                )
            is_compatible = direct == baseline
            if is_compatible:
                compatible.add(extension)
            rows.append(
                {
                    "boundary": "".join(map(str, boundary)),
                    "extension": "".join(map(str, extension)),
                    "raw_trace": "".join(map(str, direct)),
                    "production_trace": "".join(map(str, production)),
                    "compatible": is_compatible,
                }
            )

        expected = expected_extensions(boundary)
        if compatible != expected:
            raise AssertionError(
                "symbolic compatibility mismatch: "
                f"boundary={boundary}, observed={sorted(compatible)}, "
                f"expected={sorted(expected)}"
            )
        observed_fibers["".join(map(str, boundary))] = [
            "".join(map(str, extension)) for extension in sorted(compatible)
        ]

    partition = predictive_partition(OBSERVER_HORIZON)
    zero_state = encode((0, 0, 0))
    nonzero_state = encode((0, 0, 1))
    zero_class = partition.class_id(zero_state)
    nonzero_class = partition.class_id(nonzero_state)
    if zero_class == nonzero_class:
        raise AssertionError(
            "predictive-class control failed: minimized states were not separated"
        )

    compatible_control = (1, 1)
    separating_control = (0, 0)
    compatible_traces = (
        production_trace(BASE_EXTENSION, compatible_control),
        production_trace(NONZERO_EXTENSION, compatible_control),
    )
    separating_traces = (
        production_trace(BASE_EXTENSION, separating_control),
        production_trace(NONZERO_EXTENSION, separating_control),
    )
    if compatible_traces != ((0, 1, 0), (0, 1, 0)):
        raise AssertionError(f"minimized witness mismatch: {compatible_traces}")
    if separating_traces != ((0, 0, 0), (0, 0, 1)):
        raise AssertionError(f"all-input class control mismatch: {separating_traces}")

    return {
        "evidence": ["FORMAL", "EMPIRICAL"],
        "classification": "INCREMENTAL",
        "definition": {
            "updates": UPDATES,
            "samples": OBSERVER_HORIZON,
            "compatibility": (
                "for given initial right halves X != Y and boundary word b, "
                "every observed time agrees"
            ),
            "quantifier": "exists X != Y and fixed b; for all t in {0,1,2}",
            "right_exterior": "never supplied by the shrinking-cone oracle",
        },
        "symbolic_constraint": "e1 = 0 and ((not b0) and e2) = 0",
        "case_count": len(rows),
        "cases": rows,
        "compatibility_fibers": observed_fibers,
        "minimized_witness": {
            "raw_states": ["000", "001"],
            "encoded_states": [zero_state, nonzero_state],
            "boundary": "11",
            "traces": ["010", "010"],
            "nonzero_bit_in_causal_cone": True,
            "minimal": "relative to X=0^infinity and initial observed zero",
        },
        "matched_control": {
            "boundary": "00",
            "traces": ["000", "001"],
            "predictive_horizon": OBSERVER_HORIZON,
            "class_ids": [zero_class, nonzero_class],
            "classes_distinct": True,
        },
        "oracle_agreement": True,
        "decision": "BOUNDED_PADDING_FREE_COMPATIBILITY_COUNTEREXAMPLE",
        "limitations": [
            "two updates only",
            "no infinite compatible pair",
            "no compatibility-fiber growth bound",
            "no coverage, recurrence, or aperiodicity claim",
        ],
    }


def main() -> None:
    print(json.dumps(evaluate(), sort_keys=True))


if __name__ == "__main__":
    main()
