#!/usr/bin/env python3
"""Bounded deterministic safe-horizon audit for the Rule 30 right half."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import platform

from rule30 import integer_successor


INPUT = Path("results/center-column-100000.txt")
SOURCE = Path("experiments/rule30_successor.py")
CENTER_SOURCE = Path("experiments/rule30_center_column.py")
MAX_SAFE_DEPTH = 14
MAX_NESTED_WIDTH = 18
PREFIX_BITS = 20_001
INTERVALS = ((0, 4096), (7000, 11_096), (15_000, 19_096))


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def safe_labels(width: int, max_depth: int) -> list[tuple[int, ...]]:
    """Classify width states by all output responses up to each safe depth."""

    labels_by_depth: list[tuple[int, ...]] = [tuple(0 for _ in range(1 << width))]
    for _depth in range(1, max_depth + 1):
        previous = labels_by_depth[-1]
        ids: dict[tuple[int, int, int], int] = {}
        labels: list[int] = []
        for state in range(1 << width):
            key = (
                state & 1,
                previous[integer_successor(state, 0, width)],
                previous[integer_successor(state, 1, width)],
            )
            labels.append(ids.setdefault(key, len(ids)))
        labels_by_depth.append(tuple(labels))
    return labels_by_depth


def true_right_prefixes(center: tuple[int, ...], keep_bits: int) -> tuple[int, ...]:
    """Return exact low-bit right-half states before each supplied update."""

    full_width = len(center) + 1
    full_mask = (1 << full_width) - 1
    keep_mask = (1 << keep_bits) - 1
    state = 0
    prefixes: list[int] = []
    for step, bit in enumerate(center):
        # Starting from a single seed, right-half support before update t is
        # contained in cells 1..t. Thus the far boundary is provably inactive.
        assert state >> step == 0
        prefixes.append(state & keep_mask)
        direct = ((state << 1) ^ (state | (state >> 1)) ^ bit) & full_mask
        checked = integer_successor(state, bit, full_width)
        assert direct == checked
        state = direct
    return tuple(prefixes)


def generated_center(length: int) -> tuple[int, ...]:
    """Repository bitwise single-seed center-column reference."""

    state = 1
    column: list[int] = []
    for index in range(length):
        column.append((state >> index) & 1)
        state = state ^ ((state << 1) | (state << 2))
    return tuple(column)


def relation_stats(
    labels: tuple[int, ...],
    prefixes: tuple[int, ...],
    center: tuple[int, ...],
    interval: tuple[int, int],
) -> tuple[int, int, dict[tuple[int, int], frozenset[int]]]:
    lo, hi = interval
    mask = len(labels) - 1
    relation: dict[tuple[int, int], set[int]] = defaultdict(set)
    visited: set[int] = set()
    for time in range(lo, hi):
        visited.add(labels[prefixes[time] & mask])
    for time in range(lo, hi - 1):
        source = labels[prefixes[time] & mask]
        target = labels[prefixes[time + 1] & mask]
        relation[(source, center[time])].add(target)
    frozen = {key: frozenset(targets) for key, targets in relation.items()}
    conflicts = sum(len(targets) > 1 for targets in frozen.values())
    return len(visited), conflicts, frozen


def main() -> None:
    raw = INPUT.read_bytes()
    center = tuple(int(ch) for ch in raw.decode() if ch in "01")[:PREFIX_BITS]
    assert len(center) == PREFIX_BITS
    assert max(hi for _, hi in INTERVALS) <= len(center)
    center_reference_mismatches = sum(
        observed != expected
        for observed, expected in zip(center, generated_center(len(center)))
    )
    assert center_reference_mismatches == 0

    labels_by_width: dict[int, list[tuple[int, ...]]] = {}
    for width in range(1, MAX_NESTED_WIDTH + 1):
        labels_by_width[width] = safe_labels(
            width, min(width, MAX_SAFE_DEPTH)
        )

    canonical = {
        depth: labels_by_width[depth][depth]
        for depth in range(1, MAX_SAFE_DEPTH + 1)
    }

    print("experiment=Rule30 nested safe-horizon reconstruction-factor audit")
    print(f"python={platform.python_version()}")
    print(f"input={INPUT}")
    print(f"input_sha256={digest(INPUT)}")
    print(f"implementation={SOURCE}")
    print(f"implementation_sha256={digest(SOURCE)}")
    print(f"center_reference={CENTER_SOURCE}")
    print(f"center_reference_sha256={digest(CENTER_SOURCE)}")
    print(f"script={Path(__file__)}")
    print(f"script_sha256={digest(Path(__file__))}")
    print(f"center_bits={len(center)}")
    print(f"center_reference_mismatches={center_reference_mismatches}")
    print("random_seed=None")
    print(f"safe_depths=1..{MAX_SAFE_DEPTH}")
    print(f"nested_widths=depth..{MAX_NESTED_WIDTH}")
    print(f"intervals={INTERVALS}")
    print(
        "safe_definition=depth-d output responses sampled before d updates; "
        "only the first d initial right-half cells can influence them"
    )

    print("SAFE_WIDTH_COHERENCE")
    print(
        "d classes widths exhaustive_states extension_mismatches "
        "lower_target_extension_mismatches nested_transition_conflict_keys "
        "right_extension_same_depth_conflict_keys"
    )
    total_extension_mismatches = 0
    total_lower_target_extension_mismatches = 0
    total_nested_transition_conflicts = 0
    global_conflicts_by_depth: dict[int, int] = {}
    for depth in range(1, MAX_SAFE_DEPTH + 1):
        reference = canonical[depth]
        extension_mismatches = 0
        lower_target_extension_mismatches = 0
        nested_transition_conflicts = 0
        exhaustive_states = 0
        for width in range(depth, MAX_NESTED_WIDTH + 1):
            labels = labels_by_width[width][depth]
            lower = labels_by_width[width][depth - 1]
            mask = (1 << depth) - 1
            lower_mask = (1 << (depth - 1)) - 1
            nested_targets: dict[tuple[int, int], set[int]] = defaultdict(set)
            for state, class_id in enumerate(labels):
                exhaustive_states += 1
                if class_id != reference[state & mask]:
                    extension_mismatches += 1
                for bit in (0, 1):
                    successor = integer_successor(state, bit, width)
                    target = lower[successor]
                    nested_targets[(class_id, bit)].add(target)
                    expected = labels_by_width[depth - 1][depth - 1][
                        successor & lower_mask
                    ] if depth > 1 else 0
                    if target != expected:
                        lower_target_extension_mismatches += 1
            nested_transition_conflicts += sum(
                len(targets) > 1 for targets in nested_targets.values()
            )

        # Same-depth continuation needs one extra initial cell. Enumerating
        # both extensions avoids installing an artificial value at that cell.
        relation: dict[tuple[int, int], set[int]] = defaultdict(set)
        source_mask = (1 << depth) - 1
        next_labels = labels_by_width[depth + 1][depth]
        for state in range(1 << (depth + 1)):
            source_class = reference[state & source_mask]
            for bit in (0, 1):
                successor = integer_successor(state, bit, depth + 1)
                relation[(source_class, bit)].add(next_labels[successor])
        global_conflicts = sum(len(targets) > 1 for targets in relation.values())
        global_conflicts_by_depth[depth] = global_conflicts
        total_extension_mismatches += extension_mismatches
        total_lower_target_extension_mismatches += (
            lower_target_extension_mismatches
        )
        total_nested_transition_conflicts += nested_transition_conflicts
        print(
            f"{depth:2d} {len(set(reference)):4d} {depth:2d}..{MAX_NESTED_WIDTH:2d} "
            f"{exhaustive_states:8d} {extension_mismatches:3d} "
            f"{lower_target_extension_mismatches:3d} "
            f"{nested_transition_conflicts:3d} {global_conflicts:4d}"
        )

    prefixes = true_right_prefixes(center, MAX_SAFE_DEPTH + 1)
    print("TRUE_TRAJECTORY_INTERVAL_COHERENCE")
    print(
        "d classes visits_by_interval within_conflicts_by_interval "
        "pooled_conflict_keys cross_interval_only_conflict_keys "
        "output_mismatches"
    )
    trajectory_rows: list[tuple[int, int, int]] = []
    for depth in range(1, MAX_SAFE_DEPTH + 1):
        labels = canonical[depth]
        class_outputs: dict[int, int] = {}
        for state, class_id in enumerate(labels):
            output = state & 1
            if class_id in class_outputs:
                assert class_outputs[class_id] == output
            else:
                class_outputs[class_id] = output
        visits: list[int] = []
        within_conflicts: list[int] = []
        relations: list[dict[tuple[int, int], frozenset[int]]] = []
        for interval in INTERVALS:
            visited, conflicts, relation = relation_stats(
                labels, prefixes, center, interval
            )
            visits.append(visited)
            within_conflicts.append(conflicts)
            relations.append(relation)

        pooled: dict[tuple[int, int], set[int]] = defaultdict(set)
        for relation in relations:
            for key, targets in relation.items():
                pooled[key].update(targets)
        pooled_conflicts = sum(len(targets) > 1 for targets in pooled.values())
        cross_only = sum(
            len(targets) > 1
            and all(len(relation.get(key, ())) <= 1 for relation in relations)
            for key, targets in pooled.items()
        )
        output_mismatches = 0
        for lo, hi in INTERVALS:
            for time in range(lo, hi):
                class_id = labels[prefixes[time] & ((1 << depth) - 1)]
                if class_outputs[class_id] != (prefixes[time] & 1):
                    output_mismatches += 1
        trajectory_rows.append((depth, pooled_conflicts, cross_only))
        print(
            f"{depth:2d} {len(set(labels)):4d} {visits} {within_conflicts} "
            f"{pooled_conflicts:4d} {cross_only:4d} {output_mismatches:3d}"
        )

    print("SUMMARY")
    print(f"safe_width_extension_mismatches={total_extension_mismatches}")
    print(
        "safe_lower_target_extension_mismatches="
        f"{total_lower_target_extension_mismatches}"
    )
    print(
        "safe_nested_transition_conflict_keys="
        f"{total_nested_transition_conflicts}"
    )
    print(
        "global_same_depth_deterministic_all="
        f"{all(value == 0 for value in global_conflicts_by_depth.values())}"
    )
    print(
        "trajectory_same_depth_deterministic_all="
        f"{all(conflicts == 0 for _, conflicts, _ in trajectory_rows)}"
    )
    first_global = next(
        (depth for depth, conflicts in global_conflicts_by_depth.items() if conflicts),
        None,
    )
    first_trajectory = next(
        (depth for depth, conflicts, _ in trajectory_rows if conflicts), None
    )
    print(f"first_global_same_depth_failure={first_global}")
    print(f"first_trajectory_same_depth_failure={first_trajectory}")


if __name__ == "__main__":
    main()
