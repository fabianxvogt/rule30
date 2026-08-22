#!/usr/bin/env python3
"""Check whether rho_{h-1}(tau_b(c)) = tau_b(rho_h(c)) holds on predictive classes."""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=21)
    args = parser.parse_args()

    print("h b=0_commutes b=1_commutes")
    print("-- ------------ ------------")
    for h in range(3, args.max_horizon + 1):
        qh = build_quotient(h)
        qh1 = build_quotient(h - 1)
        qh2 = build_quotient(h - 2)

        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        commute = {0: True, 1: True}
        bad_example: dict[int, tuple[int, list[int], list[int]] | None] = {0: None, 1: None}
        for class_id, states in states_by_class.items():
            rho_targets = {qh1[state[:-1]] for state in states}
            if len(rho_targets) != 1:
                raise RuntimeError(f"rho failed at h={h}, class={class_id}")
            rho_class = next(iter(rho_targets))
            rho_states = [state for state, cid in qh1.items() if cid == rho_class]

            for bit in (0, 1):
                lhs = {qh2[rule30_next_tuple(state, bit)[:-1][:-1]] for state in states}
                rhs = {qh2[rule30_next_tuple(state, bit)[:-1]] for state in rho_states}
                if lhs != rhs:
                    commute[bit] = False
                    if bad_example[bit] is None:
                        bad_example[bit] = (class_id, sorted(lhs), sorted(rhs))

        print(f"{h:2d} {str(commute[0]):>12s} {str(commute[1]):>12s}")
        for bit in (0, 1):
            if not commute[bit] and bad_example[bit] is not None:
                class_id, lhs, rhs = bad_example[bit]
                print(f"   bit {bit} counterexample: class={class_id}, lhs={lhs}, rhs={rhs}")


if __name__ == "__main__":
    main()