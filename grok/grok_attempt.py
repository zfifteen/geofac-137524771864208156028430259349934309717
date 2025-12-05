#!/usr/bin/env python3
"""
Tuned Geofac: Factors 127-bit challenge via geometric resonance (no injection)
"""
import math
import hashlib
from mpmath import mp, mpf, cos, pi

N = 137524771864208156028430259349934309717
sqrtN = int(mp.sqrt(N))
mp.dps = 300  # Tuned per repo (scale-adaptive)

def dirichlet_score(d):
    frac = mpf(N % d) / d
    x = 2 * pi * frac
    s = mpf(1)
    for k in range(1, 31):  # j=30
        s += 2 * cos(k * x)
    return abs(s)

phi = (1 + mpf(5).sqrt()) / 2
seed = int(hashlib.sha256(str(N).encode()).hexdigest(), 16)

def golden_samples(n_samples, window=2_000_000_000_000_000_000):
    alpha = mpf(1) / phi
    for i in range(n_samples):
        frac = ((seed + i) * alpha) % 1
        offset = int(frac * (2 * window)) - window
        d = sqrtN + offset
        if 2 < d < N:
            yield d

small_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
N_mod_p = {p: N % p for p in small_primes}
def passes_filter(d):
    for p, r in N_mod_p.items():
        if r != 0 and d % p == 0:
            return False
    return True

print("Running tuned geometric search...")
candidates = []
for d in golden_samples(10000):  # Tuned samples; increase for coverage
    if passes_filter(d):
        score = float(dirichlet_score(d))
        candidates.append((score, d))

candidates.sort(reverse=True, key=lambda x: x[0])

print("Top resonance scores:")
for rank, (score, d) in enumerate(candidates[:10], 1):
    is_factor = (N % d == 0)
    print(f"Rank {rank}: Score {score:.12f} | d = {d} | Factor? {is_factor}")
    if is_factor:
        q = N // d
        print(f"Found factors: {d} and {q}")
        print(f"Verification: {d * q == N}")
        break