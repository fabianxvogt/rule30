#!/usr/bin/env python3
"""Run an exact, hard-bounded check of the finite rho/tau fiber pattern.

The experiment builds the finite predictive partitions S_h, the right-
truncation maps rho_h, and the two nested child maps tau_0 and tau_1. It
checks the sibling-sharing pattern only through MAX_HORIZON; this is
deliberately not an unbounded search or an infinite-horizon construction.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rule30 import PredictivePartition, predictive_partition


MAX_HORIZON = 10


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


def _leading_bit(partition: PredictivePartition, class_id: int) -> int:
    """Return the leftmost bit of a finite class representative."""

    return partition.class_members(class_id)[0] & 1


def _collision_count(keys: list[tuple[int, int]]) -> int:
    """Count redundant entries in a finite key map."""

    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, key in enumerate(keys):
        groups[key].append(index)
    return sum(len(group) - 1 for group in groups.values() if len(group) > 1)


def _summarize(
    higher: PredictivePartition,
    lower: PredictivePartition,
    lower_lower: PredictivePartition | None,
) -> HorizonSummary:
    """Check one finite adjacent-horizon square and summarize its fibers."""

    horizon = higher.horizon
    rho = higher.right_truncation_map(lower)
    tau = higher.nested_transition_map(lower)
    fibers = higher.right_truncation_fibers(lower)

    if any(len(fiber) > 2 for fiber in fibers):
        raise AssertionError(
            f"rho fiber larger than two at h={horizon}: {fibers}"
        )

    # The commuting square is only meaningful once both sides have a child
    # map. Every comparison is still exhaustive over all finite classes and
    # both boundary bits.
    if lower_lower is not None:
        lower_rho = lower.right_truncation_map(lower_lower)
        lower_tau = lower.nested_transition_map(lower_lower)
        for source_class_id, source_rho in enumerate(rho):
            for boundary_bit in (0, 1):
                left = lower_rho[tau[source_class_id][boundary_bit]]
                right = lower_tau[source_rho][boundary_bit]
                if left != right:
                    raise AssertionError(
                        "rho/tau commuting square failed at "
                        f"h={horizon}, class={source_class_id}, "
                        f"boundary={boundary_bit}"
                    )

    # For h >= 2, the two finite children have a meaningful leading bit and
    # must lie in opposite leading-bit sectors. S_0 has no leading bit.
    if horizon >= 2:
        for source_class_id, children in enumerate(tau):
            if _leading_bit(lower, children[0]) == _leading_bit(
                lower, children[1]
            ):
                raise AssertionError(
                    "tau children share a leading-bit sector at "
                    f"h={horizon}, class={source_class_id}"
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
        if _leading_bit(higher, first) == _leading_bit(higher, second):
            same_leading_bit_pairs += 1

        share0 = tau[first][0] == tau[second][0]
        share1 = tau[first][1] == tau[second][1]
        if share0:
            share_tau0 += 1
        if share1:
            share_tau1 += 1
        if share0 and share1:
            share_both += 1
        if not share0 and not share1:
            share_neither += 1

        # The child pair remains in one lower rho-fiber. This is a direct
        # sibling-level check of the commuting square.
        if lower_lower is not None:
            lower_rho = lower.right_truncation_map(lower_lower)
            for boundary_bit in (0, 1):
                if lower_rho[tau[first][boundary_bit]] != lower_rho[
                    tau[second][boundary_bit]
                ]:
                    raise AssertionError(
                        "sibling children leave the same lower rho-fiber at "
                        f"h={horizon}, boundary={boundary_bit}"
                    )

    rho_tau0_collisions = _collision_count(
        [(source_rho, children[0]) for source_rho, children in zip(rho, tau)]
    )
    rho_tau1_collisions = _collision_count(
        [(source_rho, children[1]) for source_rho, children in zip(rho, tau)]
    )

    summary = HorizonSummary(
        horizon=horizon,
        class_count=len(higher.classes),
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

    # These are the finite statements this experiment is intended to guard.
    # The h=1 row is retained as an explicit degenerate counterexample to an
    # unqualified odd-horizon formulation.
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
    """Exhaustively analyze finite horizons 1 through ``max_horizon``.

    ``max_horizon`` is deliberately capped so that the experiment cannot be
    turned into an unbounded job by accident.
    """

    if (
        not isinstance(max_horizon, int)
        or isinstance(max_horizon, bool)
        or not 0 <= max_horizon <= MAX_HORIZON
    ):
        raise ValueError(
            f"max_horizon must be an integer in [0, {MAX_HORIZON}]"
        )

    partitions = [
        predictive_partition(horizon) for horizon in range(max_horizon + 1)
    ]
    summaries = []
    for horizon in range(1, max_horizon + 1):
        lower_lower = partitions[horizon - 2] if horizon >= 2 else None
        summaries.append(
            _summarize(partitions[horizon], partitions[horizon - 1], lower_lower)
        )
    return tuple(summaries)


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

    print("Finite sibling-fiber parity check (exact; bounded)")
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
        "Limits: finite predictive partitions only; no claim for h>10, "
        "the infinite quotient, center-column coverage, or periodicity."
    )


if __name__ == "__main__":
    main()
