"""Benchmark and validate different center-column generators."""
import time
import numpy as np
import sys
sys.path.insert(0, '/Users/fabian/Development/rule30/experiments')
from rule30_center_column import generate_center_column_bitwise as gen_bi


def gen_numpy(steps):
    """Row simulation using numpy: correct Rule 30 with zero boundary."""
    w = 2 * steps + 3
    c = steps + 1
    row = np.zeros(w, dtype=np.uint8)
    row[c] = 1
    result = [0] * (steps + 1)
    result[0] = 1
    for t in range(1, steps + 1):
        # Active region grows by 1 on each side each step
        lo = c - t
        hi = c + t + 1  # exclusive
        # Extend old active region by 1 on each side with zeros
        old_ext = np.zeros(hi - lo + 2, dtype=np.uint8)
        old_ext[1:-1] = row[lo:hi]
        # Rule 30: new[i] = old[i-1] ^ (old[i] | old[i+1])
        row[lo:hi] = old_ext[:-2] ^ (old_ext[1:-1] | old_ext[2:])
        result[t] = int(row[c])
    return result


def gen_numpy_v2(steps):
    """Row simulation using numpy: full-width row, no slicing overhead."""
    w = 2 * steps + 3
    c = steps + 1
    row = np.zeros(w, dtype=np.uint8)
    row[c] = 1
    result = np.empty(steps + 1, dtype=np.uint8)
    result[0] = 1
    for t in range(1, steps + 1):
        # Use full-width padded arrays (constant size, avoids dynamic slicing)
        # But we only update the growing active region
        lo = c - t
        hi = c + t + 1
        # row[lo-1] and row[hi] are always 0 (just outside active region)
        left = row[lo-1:hi-1]
        center = row[lo:hi]
        right = row[lo+1:hi+1]
        row[lo:hi] = center ^ (left | right)
        result[t] = row[c]
    return result


if __name__ == "__main__":
    # Quick correctness check at n=100
    n = 100
    c1 = gen_numpy(n)
    c2 = gen_bi(n)
    print(f"n={n}: gen_numpy correct: {c1 == c2}")
    
    c3 = list(gen_numpy_v2(n))
    print(f"n={n}: gen_numpy_v2 correct: {c3 == c2}")
    
    # Benchmark
    for n in [10000, 100000, 500000]:
        t0 = time.time(); _ = gen_numpy(n); t1 = time.time() - t0
        t0 = time.time(); _ = gen_bi(n); t2 = time.time() - t0
        print(f"n={n}: numpy={t1:.3f}s  bigint={t2:.3f}s  ratio={t2/t1:.1f}x")
