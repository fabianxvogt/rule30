"""Reusable finite-width integer transition for the Rule 30 checker.

The encoding is ``state = sum(s[i] << i for i in range(horizon))``: bit 0
is the leftmost, boundary-adjacent cell.  For a binary boundary bit, this
function returns the next width-limited state under the Rule 30 update.

Callers must provide ``horizon >= 0``, ``0 <= state < 2**horizon``, and
``boundary_bit`` equal to 0 or 1.  Validation remains with callers so this
small boundary preserves the checker’s existing behavior for valid inputs.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

__all__ = [
    "PredictivePartition",
    "evolve_integer_state",
    "integer_successor",
    "predictive_partition",
    "response_signature",
    "response_trace",
]


ResponseSignature = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class PredictivePartition:
    """Finite-horizon response-equivalence classes for encoded states.

    ``classes`` is ordered by the first state encountered while scanning
    ``0 .. 2**horizon - 1``.  The ordering is deterministic but has no
    mathematical meaning.  ``class_id`` provides the inverse lookup for a
    valid encoded state.
    """

    horizon: int
    classes: tuple[tuple[int, ...], ...]
    _state_to_class: tuple[int, ...]

    def class_id(self, state: int) -> int:
        """Return the finite-horizon quotient class containing ``state``."""

        if not 0 <= state < (1 << self.horizon):
            raise ValueError(
                f"state must be in [0, {1 << self.horizon}); got {state}"
            )
        return self._state_to_class[state]

    def right_truncation_map(
        self, lower: PredictivePartition
    ) -> tuple[int, ...]:
        """Return the finite quotient map induced by dropping the rightmost bit.

        The returned tuple is indexed by this partition's class IDs; entry
        ``mapping[class_id]`` is the class ID in ``lower`` of the state with
        its highest encoded bit removed. ``lower`` must be the partition at
        exactly one smaller horizon. The map is computed exhaustively over
        class members and therefore checks the finite well-definedness claim
        instead of assuming it.

        This is a bounded cross-horizon map. It does not define an
        infinite-horizon quotient or a same-horizon transition function.
        """

        expected_horizon = self.horizon - 1
        if lower.horizon != expected_horizon:
            raise ValueError(
                "lower partition must have horizon "
                f"{expected_horizon}; got {lower.horizon}"
            )

        mask = (1 << lower.horizon) - 1
        mapping: list[int] = []
        for class_id, members in enumerate(self.classes):
            targets = {lower.class_id(state & mask) for state in members}
            if len(targets) != 1:
                raise ValueError(
                    "right truncation is not well-defined for finite class "
                    f"{class_id} at horizon {self.horizon}"
                )
            mapping.append(targets.pop())
        return tuple(mapping)


def integer_successor(state: int, boundary_bit: int, horizon: int) -> int:
    """Return the width-``horizon`` Rule 30 successor of an encoded state."""

    mask = (1 << horizon) - 1
    left = ((state << 1) | boundary_bit) & mask
    right = state | (state >> 1)
    return (left ^ right) & mask


def evolve_integer_state(
    state: int, boundary_bits: Iterable[int], horizon: int
) -> int:
    """Apply successive boundary bits and return the final encoded state.

    ``boundary_bits`` is consumed once from left to right.  An empty iterable
    leaves a valid encoded state unchanged.  As with ``integer_successor``,
    callers provide a non-negative horizon, a width-limited state, and binary
    boundary values; this helper intentionally keeps the API validation-free.
    """

    for boundary_bit in boundary_bits:
        state = integer_successor(state, boundary_bit, horizon)
    return state


def response_trace(
    state: int, boundary_bits: Iterable[int], horizon: int
) -> tuple[int, ...]:
    """Return the observed leftmost bit before each boundary-driven update.

    This is the integer counterpart of the predictive-state response trace:
    each output is sampled from the current state, then the corresponding
    boundary bit advances the state.  ``boundary_bits`` is consumed once from
    left to right, and an empty iterable returns an empty trace.
    """

    output: list[int] = []
    for boundary_bit in boundary_bits:
        output.append(state & 1)
        state = integer_successor(state, boundary_bit, horizon)
    return tuple(output)


def _boundary_words(horizon: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate all length-``horizon`` boundary words in integer order."""

    return tuple(
        tuple((word >> index) & 1 for index in range(horizon))
        for word in range(1 << horizon)
    )


def response_signature(state: int, horizon: int) -> ResponseSignature:
    """Return the finite response signature of ``state``.

    The signature concatenates the traces for every binary boundary word of
    length ``horizon``.  Two states are equivalent for this finite experiment
    exactly when their signatures are equal.  This is a finite observation
    criterion, not an infinite-horizon quotient.
    """

    if horizon < 0:
        raise ValueError(f"horizon must be non-negative; got {horizon}")
    if not 0 <= state < (1 << horizon):
        raise ValueError(
            f"state must be in [0, {1 << horizon}); got {state}"
        )
    return tuple(
        response_trace(state, boundary_bits, horizon)
        for boundary_bits in _boundary_words(horizon)
    )


def predictive_partition(horizon: int) -> PredictivePartition:
    """Build the bounded response-equivalence partition at ``horizon``.

    Every encoded width-``horizon`` state is included.  The implementation is
    intentionally exhaustive and therefore exponential in ``horizon``; it is
    suitable for small finite checks, not an unbounded production algorithm.
    """

    if horizon < 0:
        raise ValueError(f"horizon must be non-negative; got {horizon}")

    classes_by_signature: dict[ResponseSignature, list[int]] = {}
    for state in range(1 << horizon):
        signature = response_signature(state, horizon)
        classes_by_signature.setdefault(signature, []).append(state)

    classes = tuple(
        tuple(members) for members in classes_by_signature.values()
    )
    state_to_class = [0] * (1 << horizon)
    for class_id, members in enumerate(classes):
        for state in members:
            state_to_class[state] = class_id
    return PredictivePartition(horizon, classes, tuple(state_to_class))
