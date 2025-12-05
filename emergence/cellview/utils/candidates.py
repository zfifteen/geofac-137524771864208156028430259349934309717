"""
Candidate generation and domain modes.

- Validation mode (small N): generate full contiguous domain [2, floor(sqrt N)].
- Challenge mode (127-bit): sample a sparse corridor around sqrt(N) or custom bands.

All generators are deterministic with respect to the provided RNG.
"""

from math import isqrt
from typing import Iterable, List, Sequence, Tuple

from .challenge import CHALLENGE

DEFAULT_WINDOW = 10_000_000  # for challenge mode corridors


def dense_band(center: int, half_width: int) -> List[int]:
    """
    Return a contiguous band [center-half_width, center+half_width] (inclusive).
    Caller must ensure bounds >=2.
    """
    low = max(2, center - half_width)
    high = center + half_width
    return list(range(low, high + 1))


def dense_bands(bands: Sequence[Tuple[int, int]]) -> List[int]:
    """
    Merge multiple dense bands (center, half_width) into a deduped contiguous list.
    """
    segments = []
    for center, hw in bands:
        low = max(2, center - hw)
        high = center + hw
        segments.append((low, high))
    # merge overlaps
    segments.sort()
    merged = []
    for low, high in segments:
        if not merged or low > merged[-1][1] + 1:
            merged.append([low, high])
        else:
            merged[-1][1] = max(merged[-1][1], high)
    out: List[int] = []
    for low, high in merged:
        out.extend(range(low, high + 1))
    return out


def validation_full_domain(n: int) -> List[int]:
    """
    Full [2, floor(sqrt n)] domain for small validation numbers.
    Caller is responsible for ensuring n is small enough to materialize.
    """
    upper = isqrt(n)
    return list(range(2, upper + 1))


def corridor_around_sqrt(
    n: int,
    rng,
    samples: int = 50_000,
    window: int = DEFAULT_WINDOW,
    center: int = None,
    full: bool = False,
) -> List[int]:
    """
    Sample distinct integers in [sqrt(n)-window, sqrt(n)+window] inclusive.
    Deterministic given rng.
    If full=True, return the full corridor (clamped to positive range).
    """
    center = center if center is not None else isqrt(n)
    low = max(2, center - window)
    high = center + window
    # Rejection sampling to enforce uniqueness without building huge sets first.
    span = high - low + 1
    if full or samples >= span:
        return list(range(low, high + 1))

    seen = set()
    candidates: List[int] = []
    while len(candidates) < samples:
        val = rng.randrange(low, high + 1)
        if val not in seen:
            seen.add(val)
            candidates.append(val)
    return candidates


def multiband_corridors(
    n: int,
    rng,
    bands: Sequence[Tuple[int, int, int]],
) -> List[int]:
    """
    Generate candidates from multiple (center, window, samples) tuples.
    """
    out: List[int] = []
    for center, window, samples in bands:
        out.extend(corridor_around_sqrt(n, rng, samples=samples, window=window, center=center))
    # Deduplicate while preserving band-relative order
    seen = set()
    deduped = []
    for v in out:
        if v not in seen:
            seen.add(v)
            deduped.append(v)
    return deduped


def guard_dense_domain_for_challenge(candidate_count: int, n: int = CHALLENGE.n) -> None:
    """
    Defensive check: prevent accidental materialization of dense [2..sqrt(N)] for the 127-bit challenge.
    """
    sqrt_n = isqrt(n)
    # Ensure we aren't trying to materialize an impossible number of candidates.
    # 50 million ints is roughly 1.4GB of RAM for the object overhead, which is a safe upper bound.
    SAFE_COUNT_LIMIT = 50_000_000
    
    if candidate_count > SAFE_COUNT_LIMIT:
        raise ValueError(
            f"Candidate count {candidate_count} exceeds safe limit {SAFE_COUNT_LIMIT} for challenge mode."
        )
    
    # Also ensure we aren't inadvertently covering a huge fraction of a huge domain (dense mode)
    # if n is large (e.g. > 10^18), but count is small, we are fine (sparse).
    # The only dangerous case is if we somehow claimed to be 'validation' on a huge number, 
    # but this guard is called for 'challenge' mode.
    # So the count check is the primary memory safety guard.



__all__ = [
    "validation_full_domain",
    "corridor_around_sqrt",
    "multiband_corridors",
    "guard_dense_domain_for_challenge",
    "DEFAULT_WINDOW",
]
