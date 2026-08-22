#!/usr/bin/env python3
"""
The trajectory visits all 2^h raw states within expected coupon-collector time.
Compute the coupon-collector expected time E[T] = N * H_N = N * sum(1/k, k=1..N)
and compare with the actual raw saturation time.
"""
from __future__ import annotations
import math

# Data from raw_saturation.py
data = [
    (8,   256,   1954),
    (10,  1024,  7117),
    (12,  4096,  36712),
    (13,  8192,  71187),
    (14,  16384, 155150),
    (15,  32768, 350951),
]

print(f"{'h':>3s} {'N=2^h':>8s} {'sat_step':>10s} {'E[T]=N*H_N':>12s} {'ratio':>8s}")
for h, N, sat in data:
    H_N = sum(1.0/k for k in range(1, N+1))
    expected = N * H_N
    ratio = sat / expected
    print(f"{h:3d} {N:8d} {sat:10d} {expected:12.0f} {ratio:8.3f}")
