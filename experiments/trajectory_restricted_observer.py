#!/usr/bin/env python3
"""Exact finite probe for trajectory-restricted predictive classes.

For a width ``h`` right-half state ``s``, let ``q_h(s)`` be the existing
finite response-equivalence class: two states are equal under ``q_h`` iff
their adjacent-column response agrees for every binary boundary word of
length ``h``.  Given a center-column prefix ``c[0:N]``, the driven state is

    s_h(0) = 0^h,       s_h(t+1) = F_{c[t]}(s_h(t)).

The trajectory-restricted class set is therefore

    R_{h,N} = { q_h(s_h(t)) : 0 <= t < N }.

This is a restriction of the exact finite quotient, not a new surrogate
quotient.  ``factor_classes`` is reported separately as a deliberately
weaker control: it counts distinct length-h windows of the observed center
column, and must not be confused with counterfactual predictive classes.

The JSON report records hashes, generator cross-checks, and class-partition
digests so a retained result can be regenerated and audited without trusting
an unlabelled bit stream.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rule30 import PredictivePartition, integer_successor, predictive_partition
from experiments.rule30_center_column import (
    generate_center_column_bitwise,
    generate_center_column_slow,
)


def _bits_from_text(text: str) -> list[int]:
    bits = [int(ch) for ch in text if ch in "01"]
    if not bits:
        raise ValueError("input contains no binary digits")
    return bits


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _partition_digest(partition: PredictivePartition) -> str:
    encoded = json.dumps(partition.classes, separators=(",", ":")).encode("ascii")
    return _sha256_bytes(encoded)


def _state_path(bits: list[int], horizon: int) -> list[int]:
    """Return states at times 0..N-1 for the exact finite strip."""

    state = 0
    path = [state]
    for boundary_bit in bits[:-1]:
        state = integer_successor(state, boundary_bit, horizon)
        path.append(state)
    return path


def _factor_count(bits: list[int], horizon: int) -> int:
    if horizon == 0:
        return 1
    return len({tuple(bits[i : i + horizon]) for i in range(len(bits) - horizon + 1)})


def _check_tuple_reference(bits: list[int], horizon: int, limit: int) -> int:
    """Cross-check integer evolution against an independent tuple update."""

    state_int = 0
    state_tuple = (0,) * horizon
    checked = 0
    for boundary_bit in bits[:-1]:
        row = (boundary_bit,) + state_tuple + (0,)
        next_tuple = tuple(
            row[i] ^ (row[i + 1] | row[i + 2]) for i in range(horizon)
        )
        state_int = integer_successor(state_int, boundary_bit, horizon)
        encoded = sum(bit << index for index, bit in enumerate(next_tuple))
        if state_int != encoded:
            raise AssertionError(
                f"integer/tuple mismatch at step {checked + 1}: "
                f"h={horizon}, int={state_int}, tuple={encoded}"
            )
        state_tuple = next_tuple
        checked += 1
        if checked >= limit:
            break
    return checked


def measure(
    bits: list[int], max_horizon: int, *, reference_steps: int = 256
) -> dict[str, object]:
    if max_horizon < 0:
        raise ValueError("max_horizon must be non-negative")
    if len(bits) < 2:
        raise ValueError("at least two center-column bits are required")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("center-column input must be binary")

    check_len = min(len(bits), reference_steps)
    slow = generate_center_column_slow(check_len - 1)
    if bits[:check_len] != slow:
        raise AssertionError("bitwise/input prefix disagrees with slow row reference")

    rows: list[dict[str, object]] = []
    for horizon in range(max_horizon + 1):
        partition = predictive_partition(horizon)
        path = _state_path(bits, horizon)
        class_path = [partition.class_id(state) for state in path]
        rows.append(
            {
                "horizon": horizon,
                "raw_states": 1 << horizon,
                "full_predictive_classes": len(partition.classes),
                "trajectory_raw_states": len(set(path)),
                "trajectory_predictive_classes": len(set(class_path)),
                "trajectory_factor_classes": _factor_count(bits, horizon),
                "trajectory_first_class": class_path[0],
                "trajectory_last_class": class_path[-1],
                "partition_sha256": _partition_digest(partition),
            }
        )

    return {
        "schema": "rule30.trajectory_restricted_observer.v1",
        "definition": {
            "state": "s_h(t)=F_{c[t-1]}...F_{c[0]}(0^h)",
            "full_class": "same adjacent-column response for every binary boundary word of length h",
            "trajectory_class_set": "{q_h(s_h(t)): 0 <= t < N}",
            "factor_control": "distinct observed center-column windows c[t:t+h]",
        },
        "input": {
            "kind": "center_column_single_seed",
            "length": len(bits),
            "sha256": _sha256_bytes("".join(map(str, bits)).encode("ascii")),
            "prefix": "".join(map(str, bits[:32])),
            "slow_reference_checked": check_len,
        },
        "controls": {
            "integer_tuple_reference_checked": {
                str(h): _check_tuple_reference(bits, h, reference_steps)
                for h in range(max_horizon + 1)
            },
            "right_boundary": "zero_padded_exact_for_h_steps",
            "partition_builder": "rule30.predictive_partition recursive exhaustive finite states",
        },
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "script_sha256": _sha256_bytes(Path(__file__).read_bytes()),
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--steps", type=int, help="Generate this many center-column bits.")
    source.add_argument("--input", type=Path, help="Read a center-column bit file.")
    parser.add_argument("--max-horizon", type=int, default=16)
    parser.add_argument("--reference-steps", type=int, default=256)
    parser.add_argument("--output", type=Path, help="Write machine-readable JSON here.")
    args = parser.parse_args()
    if args.steps is not None:
        if args.steps < 2:
            parser.error("--steps must be at least 2")
        bits = generate_center_column_bitwise(args.steps - 1)
        source_label = "generated:generate_center_column_bitwise"
    else:
        bits = _bits_from_text(args.input.read_text(encoding="ascii"))
        source_label = "file:validated_against_generate_center_column_slow"

    if args.reference_steps < 1:
        parser.error("--reference-steps must be positive")

    report = measure(bits, args.max_horizon, reference_steps=args.reference_steps)
    report["input"]["source"] = source_label
    if args.input is not None:
        report["input"]["path"] = str(args.input)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
