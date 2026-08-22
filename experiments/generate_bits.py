#!/usr/bin/env python3
"""Generate a large number of center column bits using the fast bitwise method and save to file."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from rule30_center_column import generate_center_column_bitwise


def main():
    n = 15_000_000
    print(f"Generating {n} center-column bits...")
    t0 = time.time()
    bits = generate_center_column_bitwise(n - 1)
    t1 = time.time()
    print(f"Generated {len(bits)} bits in {t1-t0:.1f}s")
    
    outpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", f"center-column-{n}.txt")
    with open(outpath, 'w') as f:
        f.write(''.join(str(b) for b in bits))
        f.write('\n')
    print(f"Saved to {outpath}")


if __name__ == "__main__":
    main()
