#!/usr/bin/env python3
"""Independently verify the fixed-extension consistency artifact."""

from __future__ import annotations

import json
from pathlib import Path

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


def step(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(len(state)))


def encode(state: tuple[int, ...]) -> int:
    return sum(bit << index for index, bit in enumerate(state))


def check(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"audit_failed: {message}")


def main() -> None:
    try:
        artifact = json.loads(
            (
                Path(__file__).parent / "trajectory-extension-consistency.json"
            ).read_text()
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"could not load consistency artifact: {exc}") from exc

    check(len(CENTER_PREFIX) == TRAIN_STEPS + HOLDOUT_STEPS, "prefix length")
    state = (0,) * D
    matches = {0: [], 1: []}
    first_step = artifact.get("first_step")
    check(isinstance(first_step, list) and len(first_step) == 1, "first-step schema")
    for time, boundary_bit in enumerate(CENTER_PREFIX):
        successor = step(state, boundary_bit)
        state_int = encode(state)
        successor_int = encode(successor)
        for extension in (0, 1):
            extended = state + (extension,)
            candidate = encode(step(extended, boundary_bit)[:D])
            matches[extension].append(candidate == successor_int)
        if time == 0:
            row = first_step[0]
            check(row["time"] == 0, "first-step time")
            check(row["state"] == state_int, "first-step state")
            check(
                row["observed_response"] == [state_int & 1, successor_int],
                "observed response",
            )
            check(
                row["extension_responses"]["0"] == [state_int & 1, successor_int],
                "zero response",
            )
            check(row["extension_responses"]["1"] == [state_int & 1, 0], "one response")
        state = successor

    train = [extension for extension in (0, 1) if all(matches[extension][:TRAIN_STEPS])]
    holdout = {
        str(extension): all(matches[extension][TRAIN_STEPS:]) for extension in (0, 1)
    }
    check(train == artifact.get("train_compatible_extensions"), "training extensions")
    check(
        holdout == artifact.get("holdout_compatible_extensions"), "holdout extensions"
    )
    check(
        isinstance(artifact.get("oracle_agreement"), bool)
        and artifact["oracle_agreement"],
        "oracle agreement",
    )
    check(
        isinstance(artifact.get("separating_power"), bool)
        and artifact["separating_power"],
        "separating power",
    )
    check(
        artifact.get("decision") == "NO_GO_ZERO_PADDED_REFERENCE_ARTIFACT", "decision"
    )
    print("audit_ok", {"d": D, "k": K, "train": train, "holdout": holdout})


if __name__ == "__main__":
    main()
