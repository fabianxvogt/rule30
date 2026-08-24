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

    def class_members(self, class_id: int) -> tuple[int, ...]:
        """Return the encoded states in one finite quotient class.

        Class IDs are the deterministic, first-seen IDs in ``classes``.  The
        returned tuple is immutable and preserves the member ordering used by
        the exhaustive partition builder.  This is finite introspection only;
        it does not expose or imply an infinite-horizon class.
        """

        if (
            not isinstance(class_id, int)
            or isinstance(class_id, bool)
            or not 0 <= class_id < len(self.classes)
        ):
            raise ValueError(
                "class_id must be an integer in "
                f"[0, {len(self.classes)}); got {class_id}"
            )
        return self.classes[class_id]

    def class_trace(
        self, state: int, boundary_bits: Iterable[int]
    ) -> tuple[int, ...]:
        """Return the finite class ID before each boundary-driven update.

        The returned tuple has one entry per consumed boundary bit. Each
        entry identifies the class of the current encoded state before that
        bit is applied; the final state after the last bit is not included.
        An empty boundary word therefore returns an empty trace. This is a
        finite trajectory helper, not an infinite-horizon class process.
        """

        self.class_id(state)
        trace: list[int] = []
        for boundary_bit in boundary_bits:
            trace.append(self.class_id(state))
            state = integer_successor(state, boundary_bit, self.horizon)
        return tuple(trace)

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

    def nested_transition_map(
        self, lower: PredictivePartition
    ) -> tuple[tuple[int, int], ...]:
        """Return the finite boundary-driven map from this partition to ``lower``.

        For each source class and boundary bit, apply one width-``horizon``
        Rule 30 update, drop the highest encoded bit, and classify the result
        in the adjacent lower partition.  The returned tuple is indexed as
        ``mapping[source_class_id][boundary_bit]``.

        Every source-class member is checked to ensure that each boundary bit
        has one lower-horizon target.  This is a finite nested-transition
        check; it does not define a same-horizon transition or an
        infinite-horizon quotient.
        """

        expected_horizon = self.horizon - 1
        if lower.horizon != expected_horizon:
            raise ValueError(
                "lower partition must have horizon "
                f"{expected_horizon}; got {lower.horizon}"
            )

        mask = (1 << lower.horizon) - 1
        mapping: list[tuple[int, int]] = []
        for class_id, members in enumerate(self.classes):
            targets_for_bits: list[int] = []
            for boundary_bit in (0, 1):
                targets = {
                    lower.class_id(
                        integer_successor(state, boundary_bit, self.horizon)
                        & mask
                    )
                    for state in members
                }
                if len(targets) != 1:
                    raise ValueError(
                        "nested transition is not well-defined for finite "
                        f"class {class_id} at horizon {self.horizon} "
                        f"with boundary bit {boundary_bit}"
                    )
                targets_for_bits.append(targets.pop())
            mapping.append((targets_for_bits[0], targets_for_bits[1]))
        return tuple(mapping)

    def right_truncation_fibers(
        self, lower: PredictivePartition
    ) -> tuple[tuple[int, ...], ...]:
        """Return source-class fibers of the checked truncation map.

        The returned tuple is indexed by class ID in ``lower``.  Each entry
        contains the source class IDs in this partition whose finite
        right-truncation lands in that lower class.  The adjacent-horizon and
        finite well-definedness checks are delegated to
        :meth:`right_truncation_map` before fibers are grouped.
        """

        mapping = self.right_truncation_map(lower)
        fibers: list[list[int]] = [[] for _ in lower.classes]
        for source_class_id, target_class_id in enumerate(mapping):
            fibers[target_class_id].append(source_class_id)
        return tuple(tuple(source_ids) for source_ids in fibers)


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

    Every encoded width-``horizon`` state is included.  Classes are built from
    the finite recursive key ``(first_output, successor_on_0,
    successor_on_1)`` using the already-built lower-horizon partition.  This
    avoids enumerating all boundary words at every level while remaining an
    exhaustive finite computation; it is suitable for bounded checks, not an
    unbounded production algorithm.
    """

    if horizon < 0:
        raise ValueError(f"horizon must be non-negative; got {horizon}")

    previous = PredictivePartition(0, ((0,),), (0,))
    for current_horizon in range(1, horizon + 1):
        lower_mask = (1 << (current_horizon - 1)) - 1
        classes_by_key: dict[tuple[int, int, int], list[int]] = {}
        for state in range(1 << current_horizon):
            key = (
                state & 1,
                previous.class_id(
                    integer_successor(state, 0, current_horizon) & lower_mask
                ),
                previous.class_id(
                    integer_successor(state, 1, current_horizon) & lower_mask
                ),
            )
            classes_by_key.setdefault(key, []).append(state)

        classes = tuple(
            tuple(members) for members in classes_by_key.values()
        )
        state_to_class = [0] * (1 << current_horizon)
        for class_id, members in enumerate(classes):
            for state in members:
                state_to_class[state] = class_id
        previous = PredictivePartition(
            current_horizon, classes, tuple(state_to_class)
        )

    return previous
