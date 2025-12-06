#!/usr/bin/env python3
"""
Validation Ladder Generator for Cell-View Factor Morphospace.

Generates UNBALANCED semiprimes with a 1:3 factor ratio.
Uses base seed 42 with per-gate derivation for reproducibility.

Unbalanced semiprimes are harder than balanced ones because
the small factor p is far below √N, not clustered near it.

Prime Generation:
    Uses Z5D prime generator when available (Apple Silicon with MPFR/GMP).
    Falls back to Miller-Rabin probabilistic primality testing otherwise.
    See: https://github.com/zfifteen/z5d-prime-predictor
"""

import random
import json
import yaml
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from pathlib import Path
from math import isqrt

# Import Z5D prime generator wrapper
from .z5d_prime import next_prime as z5d_next_prime, is_prime as z5d_is_prime

# Canonical constants
BASE_SEED = 42
RATIO = 0.25  # small factor gets 25% of bits → 1:3 ratio
CHALLENGE_N = 137524771864208156028430259349934309717
CHALLENGE_BITS = 127


def _simple_next_prime(n: int) -> int:
    """
    Find the next prime >= n using Z5D prime generator.
    
    Uses Z5D prime predictor when available (Apple Silicon with MPFR/GMP),
    otherwise falls back to Miller-Rabin probabilistic testing.
    
    This maintains determinism while leveraging Z5D's optimized
    prime-density predictions for large primes.
    """
    return z5d_next_prime(n, use_z5d=True)


def _is_prime(n: int) -> bool:
    """
    Probabilistic primality test using Z5D or Miller-Rabin fallback.
    """
    return z5d_is_prime(n, use_z5d=True)


@dataclass
class GateSemiprime:
    """Represents a single gate in the validation ladder."""
    gate: str
    target_bits: int
    actual_bits: Optional[int] = None
    N: Optional[int] = None
    p: Optional[int] = None
    q: Optional[int] = None
    p_bits: Optional[int] = None
    q_bits: Optional[int] = None
    effective_seed: Optional[int] = None
    ratio: Optional[float] = None
    sqrt_N: Optional[int] = None
    p_distance_from_sqrt: Optional[int] = None
    p_as_fraction_of_sqrt: Optional[float] = None
    note: Optional[str] = None


def get_effective_seed(base_seed: int, bit_size: int) -> int:
    """Derive per-gate seed from base seed + bit size."""
    return base_seed + bit_size


def generate_unbalanced_semiprime(
    bit_size: int, 
    seed: int, 
    ratio: float = RATIO
) -> GateSemiprime:
    """
    Generate an unbalanced semiprime of the specified bit size.
    
    The small factor p gets ~ratio of the bits (default 25%).
    This places p well below √N, making it a non-trivial search target.
    
    Args:
        bit_size: Target bit length of N
        seed: RNG seed for reproducibility
        ratio: Fraction of bits for smaller factor (default 0.25 = 1:3 ratio)
    
    Returns:
        GateSemiprime with all fields populated
    """
    rng = random.Random(seed)
    
    # Small factor p gets ~ratio of the bits
    p_bits = max(4, int(bit_size * ratio))  # at least 4 bits for meaningful prime
    
    # Generate p (small factor)
    p_min = 1 << (p_bits - 1)  # ensure correct bit length
    p_max = (1 << p_bits) - 1
    p_candidate = rng.randint(p_min, p_max) | 1  # ensure odd
    p = _simple_next_prime(p_candidate)
    
    # Compute required q_bits to hit target N bit size
    # N = p * q, so log2(N) ≈ log2(p) + log2(q)
    q_bits = bit_size - p.bit_length()
    q_bits = max(p.bit_length() + 1, q_bits)  # ensure q > p
    
    q_min = 1 << (q_bits - 1)
    q_max = (1 << q_bits) - 1
    q_candidate = rng.randint(q_min, q_max) | 1  # ensure odd
    q = _simple_next_prime(q_candidate)
    
    # Ensure p < q (p is the small factor)
    if p > q:
        p, q = q, p
    
    N = p * q
    sqrt_N = isqrt(N)
    
    return GateSemiprime(
        gate=f"G{bit_size:03d}",
        target_bits=bit_size,
        actual_bits=N.bit_length(),
        N=N,
        p=p,
        q=q,
        p_bits=p.bit_length(),
        q_bits=q.bit_length(),
        effective_seed=seed,
        ratio=ratio,
        sqrt_N=sqrt_N,
        p_distance_from_sqrt=sqrt_N - p,
        p_as_fraction_of_sqrt=round(p / sqrt_N, 6) if sqrt_N > 0 else None,
    )


def generate_ladder(
    base_seed: int = BASE_SEED, 
    ratio: float = RATIO
) -> List[GateSemiprime]:
    """
    Generate the full validation ladder from 10 to 130 bits.
    G127 is the canonical challenge (not generated, factors unknown).
    
    Returns:
        List of GateSemiprime objects in ascending bit order
    """
    ladder = []
    
    # Generate gates from 10 to 130 in increments of 10
    for bits in range(10, 131, 10):
        effective_seed = get_effective_seed(base_seed, bits)
        gate = generate_unbalanced_semiprime(bits, effective_seed, ratio)
        ladder.append(gate)
    
    # Insert G127 (canonical challenge, factors unknown)
    g127_idx = next(i for i, g in enumerate(ladder) if g.target_bits > 127)
    g127 = GateSemiprime(
        gate="G127",
        target_bits=127,
        actual_bits=CHALLENGE_N.bit_length(),
        N=CHALLENGE_N,
        p=None,
        q=None,
        p_bits=None,
        q_bits=None,
        effective_seed=None,
        ratio=None,
        sqrt_N=isqrt(CHALLENGE_N),
        p_distance_from_sqrt=None,
        p_as_fraction_of_sqrt=None,
        note="Canonical challenge - factors unknown"
    )
    ladder.insert(g127_idx, g127)
    
    return ladder


def load_ladder_yaml(path: Path = None) -> Dict[str, Any]:
    """
    Load the validation ladder from YAML file.
    
    Args:
        path: Path to YAML file (default: validation_ladder.yaml in emergence/)
    
    Returns:
        Parsed YAML as dictionary
    """
    if path is None:
        # Default to validation_ladder.yaml in emergence/ directory
        path = Path(__file__).parent.parent.parent / "validation_ladder.yaml"
    
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_gate(gate_name: str, ladder: List[GateSemiprime] = None) -> Optional[GateSemiprime]:
    """
    Get a specific gate by name (e.g., "G030").
    
    Args:
        gate_name: Gate identifier like "G030" or "G127"
        ladder: Pre-generated ladder (if None, generates fresh)
    
    Returns:
        GateSemiprime or None if not found
    """
    if ladder is None:
        ladder = generate_ladder()
    
    for gate in ladder:
        if gate.gate == gate_name:
            return gate
    return None


def print_ladder_summary(ladder: List[GateSemiprime] = None) -> None:
    """Print a human-readable summary of the ladder."""
    if ladder is None:
        ladder = generate_ladder()
    
    print("=" * 100)
    print("VALIDATION LADDER: Unbalanced Semiprimes (Base Seed: 42, Ratio: 1:3)")
    print("=" * 100)
    print(f"{'Gate':<6} {'Bits':<6} {'p bits':<8} {'q bits':<8} {'p/√N':<12} {'p':>24}")
    print("-" * 100)
    
    for g in ladder:
        if g.p is None:
            print(f"{g.gate:<6} {g.target_bits:<6} {'?':<8} {'?':<8} {'?':<12} {'[CHALLENGE]':>24}")
        else:
            print(f"{g.gate:<6} {g.actual_bits:<6} {g.p_bits:<8} {g.q_bits:<8} "
                  f"{g.p_as_fraction_of_sqrt:<12.6f} {g.p:>24}")
    
    print("=" * 100)


def export_ladder_json(path: Path = None, ladder: List[GateSemiprime] = None) -> None:
    """
    Export the ladder to JSON format.
    
    Args:
        path: Output path (default: validation_ladder.json in emergence/)
        ladder: Pre-generated ladder (if None, generates fresh)
    """
    if ladder is None:
        ladder = generate_ladder()
    
    if path is None:
        path = Path(__file__).parent.parent.parent / "validation_ladder.json"
    
    data = {
        "base_seed": BASE_SEED,
        "ratio": RATIO,
        "description": "Unbalanced semiprimes for cell-view emergence validation",
        "ladder": [asdict(g) for g in ladder]
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"Ladder exported to {path}")


if __name__ == "__main__":
    ladder = generate_ladder()
    print_ladder_summary(ladder)
    export_ladder_json(ladder=ladder)
