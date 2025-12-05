"""
Canonical challenge constants for the emergence cell-view engine.

There is exactly one in-scope modulus N (127-bit semiprime, "CHALLENGE_127").
All modules must import N from here to avoid drift or accidental overrides.
No factor information (p, q) is present or permitted.
"""

from dataclasses import dataclass
from math import isqrt


@dataclass(frozen=True)
class Challenge:
    n: int
    bit_length: int
    sqrt_n: int
    seed_hex: str


# Single source of truth for N.
N_VALUE = 137524771864208156028430259349934309717

BIT_LENGTH = N_VALUE.bit_length()  # should be 127
SQRT_N = isqrt(N_VALUE)


def derive_seed_hex(n: int) -> str:
    """
    Deterministically derive a 256-bit seed from N using SHA-256 hex digest.
    The hex string (not int) is stored to avoid platform-dependent int size.
    """
    import hashlib

    digest = hashlib.sha256(str(n).encode("utf-8")).hexdigest()
    return digest


CHALLENGE = Challenge(
    n=N_VALUE,
    bit_length=BIT_LENGTH,
    sqrt_n=SQRT_N,
    seed_hex=derive_seed_hex(N_VALUE),
)


__all__ = ["CHALLENGE", "N_VALUE", "BIT_LENGTH", "SQRT_N", "derive_seed_hex", "Challenge"]
