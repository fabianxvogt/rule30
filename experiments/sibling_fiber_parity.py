#!/usr/bin/env python3
"""Run an exact, raw-state, hard-bounded sibling-fiber audit.

The audit deliberately does not import the repository's predictive-partition
helpers. It builds finite response signatures from tuple-state Rule 30
simulation, then derives the truncation and one-step child maps from those raw
states. The cap is explicit so this remains a small finite check rather than
an unbounded computation.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from itertools import product


MAX_HORIZON = 12
MAX_RAW_STATES = 1 << MAX_HORIZON


RawState = tuple[int, ...]
RawSignature = bytes


@dataclass(frozen=True)
class HorizonSummary:
    """Finite counts for one source horizon."""

    horizon: int
    class_count: int
    singleton_fibers: int
    doubleton_fibers: int
    same_leading_bit_pairs: int
    share_tau0: int
    share_tau1: int
    share_both: int
    share_neither: int
    rho_tau0_collisions: int
    rho_tau1_collisions: int


def _validate_horizon(horizon: int) -> None:
    """Reject invalid or over-cap finite computations before doing work."""

    if (
        not isinstance(horizon, int)
        or isinstance(horizon, bool)
        or not 0 <= horizon <= MAX_HORIZON
    ):
        raise ValueError(f"horizon must be an integer in [0, {MAX_HORIZON}]")


def _raw_successor(state: RawState, boundary_bit: int) -> RawState:
    """Apply one finite raw Rule 30 update with a zero right sentinel."""

    if boundary_bit not in (0, 1):
        raise ValueError(f"boundary_bit must be 0 or 1; got {boundary_bit}")

    row = (0, *state, 0)
    next_row = [0] * (len(state) + 2)
    if state:
        next_row[1] = boundary_bit ^ (row[1] | row[2])
        for position in range(2, len(state) + 1):
            next_row[position] = row[position - 1] ^ (
                row[position] | row[position + 1]
            )
    return tuple(next_row[1 : len(state) + 1])


def _raw_trace(state: RawState, boundary_word: tuple[int, ...]) -> tuple[int, ...]:
    """Return the observed leftmost bits for one explicit boundary word."""

    current = state
    output: list[int] = []
    for boundary_bit in boundary_word:
        output.append(current[0] if current else 0)
        current = _raw_successor(current, boundary_bit)
    return tuple(output)


def raw_signature(state: RawState, horizon: int) -> tuple[tuple[int, ...], ...]:
    """Return the raw tuple-state signature in lexicographic word order."""

    _validate_horizon(horizon)
    if len(state) != horizon:
        raise ValueError(
            f"state width must equal horizon {horizon}; got {len(state)}"
        )
    return tuple(
        _raw_trace(state, boundary_word)
        for boundary_word in product((0, 1), repeat=horizon)
    )


def _packed_signatures(
    states: tuple[RawState, ...], horizon: int
) -> dict[RawState, RawSignature]:
    """Build exact signatures compactly, preserving lexicographic word order.

    A trace is encoded as a fixed-width integer and concatenated in boundary
    word order. The construction is recursive only as a storage optimization:
    every child is still obtained from the raw tuple-state successor, and the
    explicit ``raw_signature`` function is used by the regression for small
    horizons.
    """

    if horizon == 0:
        return {(): b""}

    lower_states = tuple(state[:-1] for state in states)
    lower_signatures = _packed_signatures(lower_states, horizon - 1)
    trace_bytes = max(1, (horizon + 7) // 8)
    child_trace_bytes = max(1, (horizon - 1 + 7) // 8)
    child_trace_count = 1 << (horizon - 1)

    signatures: dict[RawState, RawSignature] = {}
    for state in states:
        output_bit = state[0]
        chunks: list[bytes] = []
        for boundary_bit in (0, 1):
            child = _raw_successor(state, boundary_bit)[:-1]
            child_signature = lower_signatures[child]
            for index in range(child_trace_count):
                start = index * child_trace_bytes
                child_code = int.from_bytes(
                    child_signature[start : start + child_trace_bytes], "big"
                )
                full_code = (output_bit << (horizon - 1)) | child_code
                chunks.append(full_code.to_bytes(trace_bytes, "big"))
        signatures[state] = b"".join(chunks)
    return signatures


def _raw_partition(horizon: int) -> tuple[tuple[RawState, ...], ...]:
    """Partition every raw width-horizon state by its exact finite signature."""

    _validate_horizon(horizon)
    states = tuple(product((0, 1), repeat=horizon))
    signatures = _packed_signatures(states, horizon)
    classes_by_signature: dict[RawSignature, list[RawState]] = {}
    for state in states:
        classes_by_signature.setdefault(signatures[state], []).append(state)
    return tuple(tuple(members) for members in classes_by_signature.values())


def _class_ids(
    classes: tuple[tuple[RawState, ...], ...],
) -> dict[RawState, int]:
    return {
        state: class_id
        for class_id, members in enumerate(classes)
        for state in members
    }


def _leading_bit(members: tuple[RawState, ...]) -> int:
    return members[0][0]


def _collision_count(keys: list[tuple[int, int]]) -> int:
    """Count redundant entries in a finite key map."""

    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, key in enumerate(keys):
        groups[key].append(index)
    return sum(len(group) - 1 for group in groups.values() if len(group) > 1)


def _summarize(
    higher: tuple[tuple[RawState, ...], ...],
    lower: tuple[tuple[RawState, ...], ...],
    lower_lower: tuple[tuple[RawState, ...], ...] | None,
) -> HorizonSummary:
    """Check one finite adjacent-horizon square from raw states."""

    horizon = len(higher[0][0])
    lower_ids = _class_ids(lower)
    lower_lower_ids = _class_ids(lower_lower) if lower_lower is not None else None

    rho: list[int] = []
    tau: list[tuple[int, int]] = []
    for members in higher:
        rho_targets = {lower_ids[state[:-1]] for state in members}
        if len(rho_targets) != 1:
            raise AssertionError(f"raw rho is not well-defined at h={horizon}")
        rho.append(rho_targets.pop())

        child_targets: list[int] = []
        for boundary_bit in (0, 1):
            targets = {
                lower_ids[_raw_successor(state, boundary_bit)[:-1]]
                for state in members
            }
            if len(targets) != 1:
                raise AssertionError(
                    "raw tau is not well-defined at "
                    f"h={horizon}, boundary={boundary_bit}"
                )
            child_targets.append(targets.pop())
        tau.append((child_targets[0], child_targets[1]))

    fibers: list[list[int]] = [[] for _ in lower]
    for source_class_id, target_class_id in enumerate(rho):
        fibers[target_class_id].append(source_class_id)
    if any(len(fiber) > 2 for fiber in fibers):
        raise AssertionError(f"raw rho fiber larger than two at h={horizon}")

    if lower_lower_ids is not None:
        lower_lower_rho: dict[int, int] = {}
        lower_lower_tau: dict[tuple[int, int], int] = {}
        for class_id, members in enumerate(lower):
            rho_targets = {lower_lower_ids[state[:-1]] for state in members}
            if len(rho_targets) != 1:
                raise AssertionError(
                    f"raw lower rho is not well-defined at h={horizon - 1}"
                )
            lower_lower_rho[class_id] = rho_targets.pop()
            for boundary_bit in (0, 1):
                targets = {
                    lower_lower_ids[_raw_successor(state, boundary_bit)[:-1]]
                    for state in members
                }
                if len(targets) != 1:
                    raise AssertionError(
                        "raw lower tau is not well-defined at "
                        f"h={horizon - 1}, boundary={boundary_bit}"
                    )
                lower_lower_tau[(class_id, boundary_bit)] = targets.pop()

        for source_rho, children in zip(rho, tau):
            for boundary_bit in (0, 1):
                left = lower_lower_rho[children[boundary_bit]]
                right = lower_lower_tau[(source_rho, boundary_bit)]
                if left != right:
                    raise AssertionError(
                        "raw rho/tau commuting square failed at "
                        f"h={horizon}, boundary={boundary_bit}"
                    )

    same_leading_bit_pairs = 0
    share_tau0 = 0
    share_tau1 = 0
    share_both = 0
    share_neither = 0
    for fiber in fibers:
        if len(fiber) != 2:
            continue
        first, second = fiber
        if _leading_bit(higher[first]) == _leading_bit(higher[second]):
            same_leading_bit_pairs += 1

        share0 = tau[first][0] == tau[second][0]
        share1 = tau[first][1] == tau[second][1]
        share_tau0 += share0
        share_tau1 += share1
        share_both += share0 and share1
        share_neither += not share0 and not share1

        if lower_lower_ids is not None:
            for boundary_bit in (0, 1):
                if lower_lower_rho[tau[first][boundary_bit]] != lower_lower_rho[
                    tau[second][boundary_bit]
                ]:
                    raise AssertionError(
                        "raw sibling children leave the same lower rho-fiber "
                        f"at h={horizon}, boundary={boundary_bit}"
                    )

    rho_tau0_collisions = _collision_count(
        [(source_rho, children[0]) for source_rho, children in zip(rho, tau)]
    )
    rho_tau1_collisions = _collision_count(
        [(source_rho, children[1]) for source_rho, children in zip(rho, tau)]
    )

    summary = HorizonSummary(
        horizon=horizon,
        class_count=len(higher),
        singleton_fibers=sum(len(fiber) == 1 for fiber in fibers),
        doubleton_fibers=sum(len(fiber) == 2 for fiber in fibers),
        same_leading_bit_pairs=same_leading_bit_pairs,
        share_tau0=share_tau0,
        share_tau1=share_tau1,
        share_both=share_both,
        share_neither=share_neither,
        rho_tau0_collisions=rho_tau0_collisions,
        rho_tau1_collisions=rho_tau1_collisions,
    )

    if horizon == 1:
        if (share_both, share_neither) != (1, 0):
            raise AssertionError(f"unexpected h=1 boundary row: {summary}")
    elif horizon % 2 == 0:
        if (share_both, share_neither) != (0, summary.doubleton_fibers):
            raise AssertionError(f"even-horizon parity failed: {summary}")
        if (rho_tau0_collisions, rho_tau1_collisions) != (0, 0):
            raise AssertionError(f"even-horizon injectivity failed: {summary}")
    else:
        if (share_both, share_neither) != (0, 0):
            raise AssertionError(f"odd-horizon parity failed: {summary}")
        if share_tau0 + share_tau1 != summary.doubleton_fibers:
            raise AssertionError(f"odd-horizon sharing count failed: {summary}")
        if not share_tau0 or not share_tau1:
            raise AssertionError(
                f"odd-horizon collision direction missing: {summary}"
            )
        if (rho_tau0_collisions, rho_tau1_collisions) != (
            share_tau0,
            share_tau1,
        ):
            raise AssertionError(f"collision accounting failed: {summary}")

    if horizon >= 2 and same_leading_bit_pairs != summary.doubleton_fibers:
        raise AssertionError(f"sibling leading-bit check failed: {summary}")

    return summary


def analyze(max_horizon: int = MAX_HORIZON) -> tuple[HorizonSummary, ...]:
    """Exhaustively analyze finite horizons 1 through the explicit cap."""

    _validate_horizon(max_horizon)
    if (1 << max_horizon) > MAX_RAW_STATES:
        raise ValueError(f"raw state cap exceeded at h={max_horizon}")

    partitions = [_raw_partition(horizon) for horizon in range(max_horizon + 1)]
    return tuple(
        _summarize(
            partitions[horizon],
            partitions[horizon - 1],
            partitions[horizon - 2] if horizon >= 2 else None,
        )
        for horizon in range(1, max_horizon + 1)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-horizon",
        type=int,
        default=MAX_HORIZON,
        help=f"inclusive source horizon, capped at {MAX_HORIZON}",
    )
    args = parser.parse_args()
    try:
        summaries = analyze(args.max_horizon)
    except ValueError as error:
        parser.error(str(error))

    print("Raw sibling-fiber parity check (EMPIRICAL; exact within bound)")
    print(
        "h |S_h| n1 n2 same-ell share-tau0 share-tau1 "
        "share-both share-neither coll0 coll1"
    )
    print(
        "-- ----- -- -- --------- ---------- ---------- "
        "---------- ------------ ----- -----"
    )
    for summary in summaries:
        print(
            f"{summary.horizon:2d} {summary.class_count:5d} "
            f"{summary.singleton_fibers:2d} {summary.doubleton_fibers:2d} "
            f"{summary.same_leading_bit_pairs:9d} "
            f"{summary.share_tau0:10d} {summary.share_tau1:10d} "
            f"{summary.share_both:10d} {summary.share_neither:12d} "
            f"{summary.rho_tau0_collisions:5d} {summary.rho_tau1_collisions:5d}"
        )
    print(
        "Limits: raw tuple-state partitions only; hard cap h=12; no claim "
        "for larger horizons, an infinite quotient, center-column coverage, "
        "or periodicity."
    )


if __name__ == "__main__":
    main()
