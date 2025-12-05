"""
Arithmetic certification: only gcd / N mod d.
"""

import math
from typing import List, Dict


def certify_top_m(ranked_candidates: List[Dict], N: int, m: int = 20) -> List[Dict]:
    """
    Evaluate top-m candidates for divisibility.
    """
    results = []
    for idx, entry in enumerate(ranked_candidates[:m]):
        d = int(entry["n"])
        mod = N % d
        g = math.gcd(N, d)
        is_factor = mod == 0
        results.append(
            {
                "rank": idx + 1,
                "n": d,
                "energy": entry["energy"],
                "mod": mod,
                "gcd": g,
                "is_factor": is_factor,
            }
        )
    return results


__all__ = ["certify_top_m"]
