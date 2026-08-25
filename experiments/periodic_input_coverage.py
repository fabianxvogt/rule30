#!/usr/bin/env python3
"""Measure finite predictive-class coverage under periodic boundary words.

This experiment separates pre-cycle visits from the eventual phase-lifted cycle
of the exact finite raw-state map induced by a periodic boundary word. It is
intentionally a small bounded envelope, not a center-column or infinite-horizon
result.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path
from typing import Iterable, Optional

# Make direct execution (`python3 experiments/...py`) use the repository root,
# while package imports continue to work unchanged under the test runner.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.rule30_successor import (
    PredictivePartition,
    integer_successor,
    predictive_partition,
)


@dataclass(frozen=True)
class MacroCycleObservation:
    """Exact finite macro-cycle data for one word and initial raw state."""

    horizon: int
    boundary_word: tuple[int, ...]
    initial_state: int
    macro_transient_steps: int
    macro_cycle_steps: int
    machine_period: int
    total_classes: int
    precycle_class_count: int
    cycle_class_count: int
    macro_cycle_class_count: int
    cycle_states: tuple[int, ...]
    macro_cycle_classes: tuple[int, ...]
    machine_cycle_classes: tuple[int, ...]


def _validate_word(boundary_word: Iterable[int]) -> tuple[int, ...]:
    word = tuple(boundary_word)
    if not word:
        raise ValueError("boundary_word must not be empty")
    if any(bit not in (0, 1) for bit in word):
        raise ValueError("boundary_word must contain only 0 and 1")
    return word


def _validate_state(state: int, horizon: int) -> None:
    if isinstance(state, bool) or not isinstance(state, int):
        raise TypeError("initial_state must be an integer")
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    if not 0 <= state < (1 << horizon):
        raise ValueError(
            f"initial_state must be in [0, {1 << horizon}); got {state}"
        )


def advance_period(state: int, boundary_word: Iterable[int], horizon: int) -> int:
    """Apply one complete finite boundary word to a raw encoded state."""

    _validate_state(state, horizon)
    word = _validate_word(boundary_word)
    for boundary_bit in word:
        state = integer_successor(state, boundary_bit, horizon)
    return state


def is_primitive_word(boundary_word: Iterable[int]) -> bool:
    """Return whether a non-empty binary word has no shorter repeating period."""

    word = _validate_word(boundary_word)
    length = len(word)
    return not any(
        length % divisor == 0
        and word == word[:divisor] * (length // divisor)
        for divisor in range(1, length)
    )


def primitive_binary_words(max_period: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate primitive binary words with lengths from 1 through max_period."""

    if isinstance(max_period, bool) or not isinstance(max_period, int):
        raise TypeError("max_period must be a positive integer")
    if max_period < 1:
        raise ValueError("max_period must be a positive integer")

    words: list[tuple[int, ...]] = []
    for length in range(1, max_period + 1):
        for word in product((0, 1), repeat=length):
            if is_primitive_word(word):
                words.append(tuple(word))
    return tuple(words)


def analyze_macro_cycle(
    partition: PredictivePartition,
    boundary_word: Iterable[int],
    initial_state: int,
) -> MacroCycleObservation:
    """Find the exact transient and eventual cycle for one finite input word."""

    word = _validate_word(boundary_word)
    _validate_state(initial_state, partition.horizon)

    first_step: dict[int, int] = {}
    trajectory: list[int] = []
    state = initial_state
    while state not in first_step:
        first_step[state] = len(trajectory)
        trajectory.append(state)
        state = advance_period(state, word, partition.horizon)

    macro_transient_steps = first_step[state]
    cycle_states = tuple(trajectory[macro_transient_steps:])
    macro_cycle_classes = tuple(
        sorted({partition.class_id(cycle_state) for cycle_state in cycle_states})
    )

    # Track the exact phase-lifted process as well as the macro-map.  A raw
    # state can enter the eventual phase cycle between two macro boundaries,
    # so expanding every pre-cycle macro state by the whole word can classify
    # an already-cyclic phase as pre-cycle.
    phase_first_step: dict[tuple[int, int], int] = {}
    phase_trajectory: list[tuple[int, int]] = []
    phase_state = initial_state
    phase = 0
    while (phase_state, phase) not in phase_first_step:
        phase_first_step[(phase_state, phase)] = len(phase_trajectory)
        phase_trajectory.append((phase_state, phase))
        phase_state = integer_successor(
            phase_state, word[phase], partition.horizon
        )
        phase = (phase + 1) % len(word)

    phase_cycle_start = phase_first_step[(phase_state, phase)]
    phase_precycle = phase_trajectory[:phase_cycle_start]
    phase_cycle = phase_trajectory[phase_cycle_start:]
    precycle_classes = {
        partition.class_id(state) for state, _ in phase_precycle
    }
    machine_cycle_classes = {
        partition.class_id(state) for state, _ in phase_cycle
    }
    return MacroCycleObservation(
        horizon=partition.horizon,
        boundary_word=word,
        initial_state=initial_state,
        macro_transient_steps=macro_transient_steps,
        macro_cycle_steps=len(cycle_states),
        machine_period=len(cycle_states) * len(word),
        total_classes=len(partition.classes),
        precycle_class_count=len(precycle_classes),
        cycle_class_count=len(machine_cycle_classes),
        macro_cycle_class_count=len(macro_cycle_classes),
        cycle_states=cycle_states,
        macro_cycle_classes=macro_cycle_classes,
        machine_cycle_classes=tuple(sorted(machine_cycle_classes)),
    )


def coverage_envelope(
    horizon: int,
    max_period: int,
    initial_states: Optional[Iterable[int]] = None,
) -> tuple[MacroCycleObservation, ...]:
    """Analyze every primitive word and selected finite raw initial state."""

    if isinstance(horizon, bool) or not isinstance(horizon, int):
        raise TypeError("horizon must be a non-negative integer")
    if horizon < 0:
        raise ValueError("horizon must be a non-negative integer")
    partition = predictive_partition(horizon)
    states = range(1 << horizon) if initial_states is None else tuple(initial_states)
    words = primitive_binary_words(max_period)
    return tuple(
        analyze_macro_cycle(partition, word, state)
        for word in words
        for state in states
    )


def _json_observation(observation: MacroCycleObservation) -> dict:
    payload = asdict(observation)
    payload["boundary_word"] = list(observation.boundary_word)
    payload["cycle_states"] = list(observation.cycle_states)
    payload["macro_cycle_classes"] = list(observation.macro_cycle_classes)
    payload["machine_cycle_classes"] = list(observation.machine_cycle_classes)
    return payload


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=6)
    parser.add_argument("--max-period", type=int, default=3)
    parser.add_argument(
        "--initial-state",
        type=int,
        help="an optional single raw state; default analyzes every raw state",
    )
    args = parser.parse_args(argv)
    if args.horizon < 0:
        parser.error("--horizon must be non-negative")
    if args.max_period < 1:
        parser.error("--max-period must be positive")

    initial_states = None if args.initial_state is None else (args.initial_state,)
    observations = coverage_envelope(args.horizon, args.max_period, initial_states)
    max_cycle_coverage = max(
        (observation.cycle_class_count for observation in observations),
        default=0,
    )
    payload = {
        "schema_version": 1,
        "horizon": args.horizon,
        "max_period": args.max_period,
        "primitive_words": len(primitive_binary_words(args.max_period)),
        "initial_states": len(
            range(1 << args.horizon) if initial_states is None else initial_states
        ),
        "max_eventual_cycle_coverage": max_cycle_coverage,
        "total_classes": len(predictive_partition(args.horizon).classes),
        "observations": [_json_observation(observation) for observation in observations],
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
