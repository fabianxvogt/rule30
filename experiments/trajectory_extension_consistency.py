#!/usr/bin/env python3
"""Check one fixed right-extension bit against a bounded trajectory.

The gate deliberately distinguishes a visible post-update successor from the
existing pre-update response_trace API. It is a finite consistency check, not
an infinite-horizon or center-column theorem.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rule30 import integer_successor  # noqa: E402

D = 1
K = 1
TRAIN_STEPS = 32
HOLDOUT_STEPS = 32


def parse_prefix(text: str) -> tuple[int, ...]:
    try:
        bits = tuple(int(bit) for bit in text)
    except (TypeError, ValueError) as exc:
        raise ValueError("canonical prefix must contain only binary digits") from exc
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("canonical prefix must contain only binary digits")
    return bits


CENTER_PREFIX = parse_prefix(
    "1101110011000101100100111010111001110101011000011001010110101011"
)


def tuple_successor(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(len(state)))


def encoded_state(bits: tuple[int, ...]) -> int:
    return sum(bit << index for index, bit in enumerate(bits))


def projected_successor(state: int, extension: int, boundary_bit: int) -> int:
    extended = state | (extension << D)
    return integer_successor(extended, boundary_bit, D + K) & ((1 << D) - 1)


def response(state: int, successor: int) -> tuple[int, int]:
    """Record pre-update visible bit and complete visible post-update state."""
    return state & 1, successor


def evaluate() -> dict[str, object]:
    if len(CENTER_PREFIX) != TRAIN_STEPS + HOLDOUT_STEPS:
        raise ValueError("canonical trajectory prefix has the wrong length")

    state_bits = (0,) * D
    state = encoded_state(state_bits)
    extension_matches = {extension: [] for extension in (0, 1)}
    oracle_matches = []
    rows = []
    for time, boundary_bit in enumerate(CENTER_PREFIX):
        observed_bits = tuple_successor(state_bits, boundary_bit)
        observed_successor = encoded_state(observed_bits)
        production_successor = integer_successor(state, boundary_bit, D)
        if production_successor != observed_successor:
            raise AssertionError(f"production/tuple mismatch at t={time}")
        for extension in (0, 1):
            candidate = projected_successor(state, extension, boundary_bit)
            extension_matches[extension].append(candidate == observed_successor)
        if time == 0:
            rows.append(
                {
                    "time": time,
                    "boundary_bit": boundary_bit,
                    "state": state,
                    "observed_response": list(response(state, observed_successor)),
                    "extension_responses": {
                        str(extension): list(
                            response(
                                state,
                                projected_successor(state, extension, boundary_bit),
                            )
                        )
                        for extension in (0, 1)
                    },
                }
            )
        oracle_matches.append(
            {
                "time": time,
                "tuple_successor": observed_successor,
                "integer_successor": production_successor,
            }
        )
        state_bits = observed_bits
        state = observed_successor

    train_end = TRAIN_STEPS
    holdout_end = TRAIN_STEPS + HOLDOUT_STEPS
    train_compatible = [
        extension
        for extension in (0, 1)
        if all(extension_matches[extension][:train_end])
    ]
    holdout_compatible = {
        str(extension): all(extension_matches[extension][train_end:holdout_end])
        for extension in (0, 1)
    }
    surviving_holdout = {
        str(extension): holdout_compatible[str(extension)]
        for extension in train_compatible
    }
    information_bits = (
        None if not train_compatible else K - math.log2(len(train_compatible))
    )
    return {
        "evidence": "DERIVED",
        "classification": "INCREMENTAL_NEGATIVE_CONTROL",
        "definition": {
            "d": D,
            "k": K,
            "k_meaning": "one fixed right-extension bit",
            "trajectory": "zero-initialized finite width-d state driven by center prefix",
            "compatibility": "complete visible pre-update bit and post-update state agree with the zero-padded trajectory",
            "quantifier": "one extension must match every time in the contiguous block",
            "response": "(visible pre-update bit, complete visible post-update state)",
        },
        "input": {
            "kind": "canonical_center_column_prefix",
            "bits": list(CENTER_PREFIX),
            "length": len(CENTER_PREFIX),
            "train_steps": TRAIN_STEPS,
            "holdout_steps": HOLDOUT_STEPS,
        },
        "first_step": rows,
        "train_compatible_extensions": train_compatible,
        "holdout_compatible_extensions": holdout_compatible,
        "surviving_holdout": surviving_holdout,
        "information_bits": information_bits,
        "oracle_agreement": all(
            row["tuple_successor"] == row["integer_successor"] for row in oracle_matches
        ),
        "separating_power": rows[0]["extension_responses"]["0"]
        != rows[0]["extension_responses"]["1"],
        "decision": (
            "NO_GO_ZERO_PADDED_REFERENCE_ARTIFACT"
            if train_compatible == [0] and surviving_holdout == {"0": True}
            else "REVIEW_REQUIRED"
        ),
        "limitations": [
            "one fixed extension bit and one finite 64-step prefix",
            "the trajectory is the finite zero-padded reference model, not the unknown semi-infinite right half",
            "a unique extension can be a boundary convention artifact rather than hidden-information recovery",
            "no superconstant lower bound, aperiodicity result, or infinite-trajectory theorem",
        ],
    }


def main() -> None:
    results = evaluate()
    target = Path(__file__).parent / "trajectory-extension-consistency.json"  # nosec
    target.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")  # nosec
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
