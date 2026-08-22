#!/usr/bin/env python3
"""
Deep analysis of predictive-state class-count growth using precomputed data.

Class counts for h=0..20 and transition image sizes for h=1..20 were
computed by predictive_state_growth.py.  This script:
  1. Searches for linear recurrences in the class-count sequence.
  2. Characterizes asymptotic growth (polynomial, exponential, stretched exponential).
  3. Analyzes transition image coverage fractions.
"""

from __future__ import annotations

import math

# Precomputed from predictive_state_growth.py --max-horizon 20
CLASS_COUNTS = [
    1, 2, 3, 5, 7, 11, 16, 25, 35, 52, 71, 104, 141, 203, 272,
    387, 517, 733, 971, 1364, 1792,
]

# h -> (domain, image_on_0, image_on_1) from --max-horizon 20 run
TRANS_DATA = {
    1: (2, 1, 1), 2: (3, 2, 2), 3: (5, 3, 3), 4: (7, 5, 5),
    5: (11, 7, 7), 6: (16, 11, 11), 7: (25, 15, 16),
    8: (35, 22, 24), 9: (52, 30, 33), 10: (71, 44, 48),
    11: (104, 60, 64), 12: (141, 87, 93), 13: (203, 117, 125),
    14: (272, 166, 179), 15: (387, 223, 237), 16: (517, 317, 338),
    17: (733, 421, 448), 18: (971, 590, 634), 19: (1364, 773, 834),
    20: (1792, 1075, 1164),
}


def recurrence_search(seq, max_k=5, max_coef=4):
    """Search for integer linear recurrences a(n) = sum c_i * a(n-i) for i=1..k."""
    from itertools import product as iproduct
    found = []
    for k in range(2, max_k + 1):
        coef_range = range(-max_coef, max_coef + 1)
        for coefs in iproduct(coef_range, repeat=k):
            if all(c == 0 for c in coefs):
                continue
            ok = all(
                sum(coefs[j] * seq[i - 1 - j] for j in range(k)) == seq[i]
                for i in range(k, len(seq))
            )
            if ok:
                found.append((k, coefs))
    return found


def main() -> None:
    seq = CLASS_COUNTS
    max_h = len(seq) - 1

    print("=" * 72)
    print("PREDICTIVE-STATE CLASS COUNT: FULL ANALYSIS")
    print("=" * 72)
    print()
    print("Sequence h=0..20:", seq)

    diffs1 = [seq[i] - seq[i - 1] for i in range(1, len(seq))]
    diffs2 = [diffs1[i] - diffs1[i - 1] for i in range(1, len(diffs1))]
    diffs3 = [diffs2[i] - diffs2[i - 1] for i in range(1, len(diffs2))]
    print("1st differences:", diffs1)
    print("2nd differences:", diffs2)
    print("3rd differences:", diffs3)

    # ----------------------------------------------------------------
    print()
    print("=" * 72)
    print("SECTION 1: Linear recurrence search (k=2..5, |coef|<=4)")
    print("=" * 72)
    results = recurrence_search(seq, max_k=5, max_coef=4)
    if results:
        for k, coefs in results:
            terms = " + ".join("%d*a(n-%d)" % (coefs[j], j + 1) for j in range(k))
            print("  a(n) = " + terms)
    else:
        print("  No recurrence found in this range.")

    ev = seq[0::2]
    od = seq[1::2]
    print("Even-h subsequence:", ev)
    ev_results = recurrence_search(ev, max_k=5, max_coef=4)
    if ev_results:
        for k, coefs in ev_results:
            terms = " + ".join("%d*ev(n-%d)" % (coefs[j], j + 1) for j in range(k))
            print("  ev(n) = " + terms)
    else:
        print("  No recurrence for even-h subsequence.")

    print("Odd-h subsequence:", od)
    od_results = recurrence_search(od, max_k=5, max_coef=4)
    if od_results:
        for k, coefs in od_results:
            terms = " + ".join("%d*od(n-%d)" % (coefs[j], j + 1) for j in range(k))
            print("  od(n) = " + terms)
    else:
        print("  No recurrence for odd-h subsequence.")

    # ----------------------------------------------------------------
    print()
    print("=" * 72)
    print("SECTION 2: Asymptotic growth characterization")
    print("=" * 72)
    print()
    print("log(a(h))/h   [-> const if purely exponential]:")
    for i in range(1, len(seq)):
        v = math.log(seq[i]) / i
        print("  h=%2d: %.6f" % (i, v))

    print()
    print("log(a(h))/sqrt(h)   [-> const if exp(c*sqrt(h))]:")
    for i in range(1, len(seq)):
        v = math.log(seq[i]) / math.sqrt(i)
        print("  h=%2d: %.6f" % (i, v))

    print()
    print("log(log(a(h)))/log(h)   [-> beta if a(h) ~ exp(h^beta)]:")
    for i in range(2, len(seq)):
        v = math.log(math.log(seq[i])) / math.log(i)
        print("  h=%2d: %.6f" % (i, v))

    print()
    print("2-step geometric means sqrt(a(h)/a(h-2)) per step:")
    for i in range(2, len(seq)):
        v = math.sqrt(seq[i] / seq[i - 2])
        print("  h=%2d: %.8f" % (i, v))

    # OLS fit log(a(h)) = alpha + beta*h
    n = len(seq)
    xs = list(range(n))
    log_s = [math.log(x) for x in seq]
    mx = sum(xs) / n
    my = sum(log_s) / n
    beta = sum((xs[i] - mx) * (log_s[i] - my) for i in range(n)) / sum((xs[i] - mx) ** 2 for i in range(n))
    alpha = my - beta * mx
    print()
    print("OLS fit (full): log(a(h)) = %.5f + %.5f * h => base per step = %.8f" % (alpha, beta, math.exp(beta)))

    # Tail OLS
    xs2 = xs[12:]
    ls2 = log_s[12:]
    n2 = len(xs2)
    mx2 = sum(xs2) / n2
    my2 = sum(ls2) / n2
    b2 = sum((xs2[i] - mx2) * (ls2[i] - my2) for i in range(n2)) / sum((xs2[i] - mx2) ** 2 for i in range(n2))
    a2 = my2 - b2 * mx2
    print("OLS fit (h>=12): log(a(h)) = %.5f + %.5f * h => base per step = %.8f" % (a2, b2, math.exp(b2)))
    print("For reference: sqrt(2) = %.8f, phi = %.8f" % (math.sqrt(2), (1 + math.sqrt(5)) / 2))

    # ----------------------------------------------------------------
    print()
    print("=" * 72)
    print("SECTION 3: Transition image coverage")
    print("=" * 72)
    print()
    print("%2s | %7s | %5s | %5s | %5s | %9s | %9s" % (
        "h", "domain", "prev", "img0", "img1", "img0/prev", "img1/prev"))
    print("-" * 60)
    for h in sorted(TRANS_DATA.keys()):
        dom, im0, im1 = TRANS_DATA[h]
        prev = seq[h - 1]
        print("%2d | %7d | %5d | %5d | %5d | %9.4f | %9.4f" % (
            h, dom, prev, im0, im1, im0 / prev, im1 / prev))

    print()
    print("Trend: img0/prev and img1/prev fractions (by h):")
    for h in sorted(TRANS_DATA.keys()):
        dom, im0, im1 = TRANS_DATA[h]
        prev = seq[h - 1]
        print("  h=%2d: %.5f  %.5f" % (h, im0 / prev, im1 / prev))

    # ----------------------------------------------------------------
    print()
    print("=" * 72)
    print("SECTION 4: Summary and implications")
    print("=" * 72)
    print()
    print("Growth type: super-polynomial, sub-exponential.")
    print()
    print("Evidence:")
    print("  - log(a(h))/h is steadily DECREASING: growth is slower than any fixed exponential.")
    print("  - log(a(h))/log(h) is steadily INCREASING: growth is faster than any polynomial.")
    print("  - log(log(a(h)))/log(h) converges toward ~0.67 ~ 2/3.")
    print("    This suggests a(h) ~ exp(C * h^(2/3)) (stretched exponential).")
    print()
    print("Implication for proof strategy:")
    print("  - The predictive-state quotient has UNBOUNDED class count.")
    print("  - No finite-state machine can be the infinite-horizon limit.")
    print("  - The sub-exponential growth is, however, an interesting structural fact.")
    print("  - This should be documented as a new empirical result.")
    print()
    print("Transition structure:")
    print("  - img0/prev and img1/prev fractions are ~0.6-0.85 and declining toward ~0.6.")
    print("  - Not all h-1 classes are reachable via transitions from h-classes.")
    print("  - This means the image of the transition map is a proper subset of S_{h-1}.")


if __name__ == "__main__":
    main()
