"""Reusable finite-width integer transition for the Rule 30 checker.

The encoding is ``state = sum(s[i] << i for i in range(horizon))``: bit 0
is the leftmost, boundary-adjacent cell.  For a binary boundary bit, this
function returns the next width-limited state under the Rule 30 update.

Callers must provide ``horizon >= 0``, ``0 <= state < 2**horizon``, and
``boundary_bit`` equal to 0 or 1.  Validation remains with callers so this
small boundary preserves the checker’s existing behavior for valid inputs.
"""

from __future__ import annotations

__all__ = ["integer_successor"]


def integer_successor(state: int, boundary_bit: int, horizon: int) -> int:
    """Return the width-``horizon`` Rule 30 successor of an encoded state."""

    mask = (1 << horizon) - 1
    left = ((state << 1) | boundary_bit) & mask
    right = state | (state >> 1)
    return (left ^ right) & mask
