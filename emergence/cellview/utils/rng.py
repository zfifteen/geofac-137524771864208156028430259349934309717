"""
Deterministic RNG utilities.

Seeds default to SHA-256(N) (hex) from the canonical challenge module unless
explicitly overridden by the caller/CLI.
"""

import random
from typing import Optional

from .challenge import CHALLENGE


def rng_from_hex(seed_hex: Optional[str] = None) -> random.Random:
    """
    Create a Random instance seeded deterministically from a hex string.
    """
    seed_hex = seed_hex or CHALLENGE.seed_hex
    # Convert hex to int for random seeding; masking not needed (Python int is unbounded).
    seed_int = int(seed_hex, 16)
    rng = random.Random()
    rng.seed(seed_int)
    return rng


__all__ = ["rng_from_hex"]
