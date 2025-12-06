#!/usr/bin/env python3
"""
Z5D Prime Generator Wrapper.

This module provides an interface to the Z5D prime predictor/generator
from https://github.com/zfifteen/z5d-prime-predictor

The Z5D tool uses a proprietary five-dimensional algorithm based on
the Riemann Hypothesis to efficiently find large primes.

Usage:
    - If Z5D tools are available (compiled), uses them via subprocess
    - Otherwise, falls back to Miller-Rabin probabilistic primality testing

This allows the code to work on any platform while leveraging Z5D
when available on Apple Silicon with MPFR/GMP installed.
"""

import subprocess
import shutil
import random
from pathlib import Path
from typing import Optional


# Z5D tool paths (can be customized via environment or config)
Z5D_PRIME_GENERATOR = "prime_generator"  # Expected in PATH or explicit path
Z5D_AVAILABLE = None  # Lazy detection


def _detect_z5d() -> bool:
    """
    Detect if Z5D prime_generator tool is available.
    Caches result for subsequent calls.
    """
    global Z5D_AVAILABLE
    if Z5D_AVAILABLE is not None:
        return Z5D_AVAILABLE
    
    # Check if prime_generator is in PATH
    Z5D_AVAILABLE = shutil.which(Z5D_PRIME_GENERATOR) is not None
    return Z5D_AVAILABLE


def _z5d_next_prime(n: int) -> Optional[int]:
    """
    Find next prime >= n using Z5D prime_generator.
    
    Args:
        n: Starting value
    
    Returns:
        Next prime >= n, or None if Z5D fails
    """
    if not _detect_z5d():
        return None
    
    try:
        # Call: prime_generator --start <n> --count 1 --csv
        result = subprocess.run(
            [Z5D_PRIME_GENERATOR, "--start", str(n), "--count", "1", "--csv"],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            check=False
        )
        
        if result.returncode != 0:
            return None
        
        # Parse CSV output: n,prime,is_mersenne,ms
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:  # Need header + data row
            return None
        
        # Skip header, parse data row
        data_row = lines[1].split(',')
        if len(data_row) < 2:
            return None
        
        prime = int(data_row[1])
        return prime
    
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
        return None


def _miller_rabin(n: int, k: int = 10) -> bool:
    """
    Miller-Rabin probabilistic primality test (fallback).
    
    Args:
        n: Number to test
        k: Number of rounds (higher = more accurate, default 10 gives error < 2^-20)
    
    Returns:
        True if n is probably prime, False if definitely composite
    """
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def _fallback_is_prime(n: int) -> bool:
    """
    Fallback primality test using Miller-Rabin.
    Uses trial division for small numbers.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # For small numbers, use trial division
    if n < 1000:
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True
    
    # For large numbers, use Miller-Rabin
    return _miller_rabin(n, k=10)


def _fallback_next_prime(n: int) -> int:
    """
    Fallback: find next prime >= n using Miller-Rabin.
    """
    if n < 2:
        return 2
    if n == 2:
        return 2
    if n % 2 == 0:
        n += 1
    while True:
        if _fallback_is_prime(n):
            return n
        n += 2


def next_prime(n: int, use_z5d: bool = True) -> int:
    """
    Find the next prime >= n.
    
    This is the main entry point for prime generation in the ladder.
    
    Args:
        n: Starting value
        use_z5d: If True, attempt to use Z5D prime generator when available
    
    Returns:
        Next prime >= n
    
    Algorithm:
        1. If use_z5d=True and Z5D is available, use Z5D prime_generator
        2. Otherwise, fall back to Miller-Rabin probabilistic testing
    
    Notes:
        - Z5D is only available on Apple Silicon with MPFR/GMP compiled
        - Fallback is suitable for all platforms and produces identical results
          for the same RNG seed (determinism maintained)
        - Z5D may be faster for very large primes (100+ bit)
    """
    if use_z5d:
        prime = _z5d_next_prime(n)
        if prime is not None:
            return prime
    
    # Fallback to Miller-Rabin
    return _fallback_next_prime(n)


def is_prime(n: int, use_z5d: bool = True) -> bool:
    """
    Test if n is prime.
    
    Args:
        n: Number to test
        use_z5d: If True, attempt to use Z5D (currently no direct test API, uses next_prime)
    
    Returns:
        True if n is (probably) prime
    
    Notes:
        - Currently uses Miller-Rabin regardless of use_z5d
        - Z5D prime_generator doesn't expose a direct primality test API
    """
    # Z5D doesn't have a direct primality test API in prime_generator
    # Could use next_prime and check if it returns n, but that's wasteful
    # So we always use the Miller-Rabin fallback for is_prime
    return _fallback_is_prime(n)


__all__ = ["next_prime", "is_prime"]
