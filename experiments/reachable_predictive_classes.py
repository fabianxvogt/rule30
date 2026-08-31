#!/usr/bin/env python3
"""
Compare full vs. reachable predictive-state class counts for Rule 30.

For the provenance-recorded trajectory-memory question, use
``trajectory_restricted_observer.py``. This older text-only script remains a
quick exploratory reproduction of the same visited-class baseline; it does
not emit hashes or independent generator controls.

For each horizon h we ask: how many of the |S_h| predictive-state classes
are actually visited by the real center-column-driven trajectory?

We trace the actual center column trajectory driving the right half-plane and
record which h-class each right-half state lands in at every time step.

If reachable class counts grow much slower than the full counts, that would be
relevant for the proof strategy (the actual trajectory stays in a sparse sub-system).
"""

from __future__ import annotations

import argparse
from itertools import product
from typing import Optional


# ---------------------------------------------------------------------------
# Rule 30 center column (from single seed)
# ---------------------------------------------------------------------------

def center_column_prefix(length: int) -> list[int]:
    """Generate `length` bits of the Rule 30 center column.

    Uses an expanding bit-window.  The center cell is at position width//2.
    """
    width = 2 * length + 3
    row = [0] * width
    row[width // 2] = 1  # single-seed initial condition
    bits: list[int] = [row[width // 2]]
    for _ in range(length - 1):
        new_row = [0] * width
        for i in range(1, width - 1):
            new_row[i] = row[i - 1] ^ (row[i] | row[i + 1])
        row = new_row
        bits.append(row[width // 2])
    return bits


def center_column_fast(length: int) -> list[int]:
    """Fast bitset-based Rule 30 center column generator."""
    bits: list[int] = []
    # Use integers as bit arrays; cell 0 = seed
    lo: int = 1   # bit i = cell at position -i (left half)
    hi: int = 1   # bit i = cell at position +i (right half), bit 0 = center
    for _ in range(length):
        # Center cell = bit 0 of lo (or hi, they agree at 0)
        bits.append(hi & 1)
        # Extend one cell on each side
        lo = lo << 1
        hi = hi << 1
        # Rule 30: new[x] = left[x] XOR (center[x] OR right[x])
        # The symmetry: lo and hi are mirror symmetric about center
        # We only need hi (right half including center) and lo (left half)
        # Standard reconstruction:
        # hi_new[i] = hi[i-1] XOR (hi[i] | hi[i+1])  with hi[-1]=lo[1]
        # For simplicity, use the expanding row method with integers.
        lo = 0   # will rebuild below
        hi = 0
        # Rebuild using the fast method: track state as integer pair
        # Fall through to slow method for now (fast enough for our purposes)
        break
    # Fall back to expanding row method (clear enough and still fast enough
    # for the horizons we care about, ~50000 steps at width ~h+20)
    return center_column_prefix(length)


# ---------------------------------------------------------------------------
# Predictive-state quotient (copied from predictive_state_growth.py)
# ---------------------------------------------------------------------------

def rule30_next(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    w = len(state)
    if w == 0:
        return ()
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(w))


def build_quotient_at_horizon(
    h: int,
    prev_class: Optional[dict[tuple[int, ...], int]],
) -> dict[tuple[int, ...], int]:
    if h == 0:
        return {(): 0}
    signatures: dict[tuple[int, ...], tuple] = {}
    for state in product(range(2), repeat=h):
        first_bit = state[0]
        if prev_class is None:
            sig = (first_bit, 0, 0)
        else:
            succ0 = rule30_next(state, 0)[: h - 1]
            succ1 = rule30_next(state, 1)[: h - 1]
            sig = (first_bit, prev_class[succ0], prev_class[succ1])
        signatures[state] = sig
    sig_to_id: dict[tuple, int] = {}
    state_to_class: dict[tuple[int, ...], int] = {}
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        state_to_class[state] = sig_to_id[sig]
    return state_to_class


def build_all_quotients(max_h: int) -> dict[int, dict[tuple[int, ...], int]]:
    quotients: dict[int, dict[tuple[int, ...], int]] = {}
    prev = None
    for h in range(max_h + 1):
        cm = build_quotient_at_horizon(h, prev)
        quotients[h] = cm
        prev = cm
    return quotients


# ---------------------------------------------------------------------------
# Right-half state driven by center column
# ---------------------------------------------------------------------------

def simulate_right_half(
    center_bits: list[int],
    h: int,
    quotient: dict[tuple[int, ...], int],
) -> set[int]:
    """Simulate the driven right half-plane at horizon h.

    The right-half state is always width-h (we discard cells beyond position h).
    Returns the set of predictive-class ids visited during the simulation.
    """
    state: tuple[int, ...] = (0,) * h  # initial all-zero right half
    visited: set[int] = {quotient[state]}
    for bit in center_bits[:-1]:  # bit drives the step that produces next state
        next_full = rule30_next(state, bit)
        state = next_full[:h]
        visited.add(quotient[state])
    return visited


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-horizon", type=int, default=14,
                        help="Maximum horizon to analyze (default: 14)")
    parser.add_argument("--steps", type=int, default=10000,
                        help="Number of center-column steps to trace (default: 10000)")
    args = parser.parse_args()

    max_h = args.max_horizon
    steps = args.steps

    print(f"Generating {steps} center-column bits...")
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from rule30_center_column import generate_center_column_bitwise
    # generate_center_column_bitwise(n) returns n+1 bits (indices 0..n)
    center = generate_center_column_bitwise(steps - 1)
    assert len(center) == steps
    print("Done.")
    print()

    print(f"Building quotient maps h=0..{max_h}...")
    quotients = build_all_quotients(max_h)
    print("Done.")
    print()

    print("Reachable vs. full predictive-state class counts:")
    print()
    header = (
        f"{'h':>3} | {'full':>7} | {'reachable':>9} | "
        f"{'reach/full':>10} | {'raw 2^h':>8} | {'reach/raw':>10}"
    )
    print(header)
    print("-" * len(header))

    for h in range(max_h + 1):
        q = quotients[h]
        full_count = max(q.values()) + 1

        if h == 0:
            reachable_count = 1
        else:
            visited = simulate_right_half(center, h, q)
            reachable_count = len(visited)

        raw = 2 ** h if h > 0 else 1
        rf = reachable_count / full_count
        rr = reachable_count / raw
        print(f"{h:>3} | {full_count:>7} | {reachable_count:>9} | "
              f"{rf:>10.4f} | {raw:>8} | {rr:>10.6f}")

    print()
    print("Notes:")
    print("  'full'      = total number of predictive-state equivalence classes at horizon h")
    print("  'reachable' = classes visited by the actual Rule 30 trajectory in", steps, "steps")
    print("  reach/full  = fraction of full quotient that is reachable")
    print("  raw 2^h     = raw state space size before quotienting")
    print("  reach/raw   = reachable classes as fraction of raw state space")


if __name__ == "__main__":
    main()
