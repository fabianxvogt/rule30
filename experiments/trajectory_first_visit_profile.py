#!/usr/bin/env python3
"""Record exact first-visit profiles for a retained Rule 30 center trace.

The finite trajectory is ``s_h(0)=0^h`` and
``s_h(t+1)=F_{c[t]}(s_h(t))``.  For every finite predictive class ID this
script records the first state index at which the trajectory observes that
class.  It is deliberately a profile extractor, not an eventual-coverage
test: ``None`` means only that the supplied finite input did not reach a
class.

The predeclared falsifier checked by the report is ``B(h)=2**(h+1)``.  A
complete profile with a maximum first visit above that bound is a finite
counterexample to that bound; an incomplete profile cannot establish either
coverage or a bound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.rule30_center_column import generate_center_column_slow
from rule30 import integer_successor, predictive_partition


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bits(path: Path) -> tuple[list[int], str]:
    raw = path.read_bytes()
    text = raw.decode("ascii")
    bits = [int(ch) for ch in text if ch in "01"]
    if len(bits) < 2:
        raise ValueError("input must contain at least two binary bits")
    return bits, _sha256("".join(map(str, bits)).encode("ascii"))


def _profile_digest(profile: tuple[int | None, ...]) -> str:
    encoded = json.dumps(profile, separators=(",", ":")).encode("ascii")
    return _sha256(encoded)


def measure(bits: list[int], max_horizon: int, reference_steps: int = 256) -> dict[str, object]:
    if max_horizon < 0:
        raise ValueError("max_horizon must be non-negative")
    checked = min(len(bits), reference_steps)
    if bits[:checked] != generate_center_column_slow(checked - 1):
        raise AssertionError("input prefix disagrees with the slow row reference")

    rows: list[dict[str, object]] = []
    profiles: dict[str, list[int | None]] = {}
    states = [0] * (max_horizon + 1)
    partitions = [predictive_partition(h) for h in range(max_horizon + 1)]
    first: list[list[int | None]] = [
        [None] * len(partition.classes) for partition in partitions
    ]
    for horizon, partition in enumerate(partitions):
        first[horizon][partition.class_id(0)] = 0

    # A report with N states consumes exactly N-1 boundary bits.  This matches
    # the observer-audit indexing and never records a post-final transition.
    for step, boundary_bit in enumerate(bits[:-1], start=1):
        for horizon, partition in enumerate(partitions):
            states[horizon] = integer_successor(
                states[horizon], boundary_bit, horizon
            )
            class_id = partition.class_id(states[horizon])
            if first[horizon][class_id] is None:
                first[horizon][class_id] = step

    for horizon, (partition, profile) in enumerate(zip(partitions, first)):
        observed = [value for value in profile if value is not None]
        missing = len(profile) - len(observed)
        maximum = max(observed) if observed else None
        bound = 1 << (horizon + 1)
        complete = missing == 0
        if not complete:
            status = "INCOMPLETE_INPUT"
        elif maximum is not None and maximum > bound:
            status = "FAIL_BOUND"
        else:
            status = "PASS_BOUND"
        profiles[str(horizon)] = profile
        rows.append(
            {
                "horizon": horizon,
                "full_predictive_classes": len(partition.classes),
                "observed_classes": len(observed),
                "missing_classes": missing,
                "max_first_visit": maximum,
                "bound_B_2_pow_h_plus_1": bound,
                "bound_status": status,
                "profile_sha256": _profile_digest(tuple(profile)),
            }
        )

    return {
        "schema": "rule30.trajectory_first_visit_profile.v1",
        "definition": {
            "trajectory": "s_h(0)=0^h; s_h(t+1)=F_{c[t]}(s_h(t)); states t=0..N-1",
            "profile": "first_visit[class_id] = least observed state index, or null",
            "bound": "B(h)=2^(h+1), checked only when the profile is complete",
            "class_ids": "deterministic first-seen IDs from predictive_partition(h)",
        },
        "input": {
            "kind": "center_column_single_seed",
            "length": len(bits),
            "sha256": _sha256("".join(map(str, bits)).encode("ascii")),
            "prefix": "".join(map(str, bits[:32])),
            "slow_reference_checked": checked,
        },
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "script_sha256": _sha256(Path(__file__).read_bytes()),
        },
        "rows": rows,
        "profiles": profiles,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--max-horizon", type=int, default=20)
    parser.add_argument("--reference-steps", type=int, default=256)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.reference_steps < 1:
        parser.error("--reference-steps must be positive")
    bits, _ = _read_bits(args.input)
    report = measure(bits, args.max_horizon, args.reference_steps)
    report["input"]["path"] = str(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
