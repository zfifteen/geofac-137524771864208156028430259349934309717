"""
Metrics for emergent signals: sortedness, aggregation, delayed gratification (DG).
"""

from dataclasses import dataclass
from typing import List, Sequence, Tuple


def sortedness(values: Sequence[int]) -> float:
    """
    Measure local monotonicity by counting adjacent inversions.
    Returns 1.0 when non-decreasing, 0 when fully reversed.
    """
    if len(values) < 2:
        return 1.0
    inversions = sum(1 for a, b in zip(values, values[1:]) if a > b)
    return 1.0 - inversions / (len(values) - 1)


def aggregation(algotypes: Sequence[str]) -> float:
    """
    Fraction of adjacent pairs sharing the same algotype.
    Baseline for random labels with ~3 types is ~0.11; higher implies clustering.
    """
    if len(algotypes) < 2:
        return 1.0
    same = sum(1 for a, b in zip(algotypes, algotypes[1:]) if a == b)
    return same / (len(algotypes) - 1)


@dataclass
class DGEpisode:
    start: int
    end: int
    peak: float
    valley: float
    new_peak: float


def detect_dg(series: Sequence[float], epsilon: float = 1e-3, hysteresis: float = 1e-3) -> Tuple[List[DGEpisode], float]:
    """
    Extract delayed-gratification episodes from a time series S(t).
    Definition: Peak -> Valley -> Higher Peak.
    DG Index = Sum( (New_Peak - Valley) / (Peak - Valley) ) for all such episodes.
    
    Uses a standard peak/valley detector first, then scans the sequence of extrema.
    """
    if len(series) < 3:
        return [], 0.0

    # 1. Identify Extrema (Peaks and Valleys)
    extrema: List[Tuple[str, float, int]] = [] # (type, value, index)
    
    # Direction: 1 = going up, -1 = going down
    direction = 0
    last_val = series[0]
    last_idx = 0
    
    # Initialize direction based on first move > epsilon
    for i, val in enumerate(series):
        if abs(val - last_val) > epsilon:
            direction = 1 if val > last_val else -1
            break
            
    # Simple robust local extrema finder
    current_extreme_val = series[0]
    current_extreme_idx = 0
    
    for i, val in enumerate(series):
        if direction == 1: # Climbing, looking for Peak
            if val > current_extreme_val:
                current_extreme_val = val
                current_extreme_idx = i
            elif val < current_extreme_val - epsilon:
                # Found Peak
                extrema.append(('P', current_extreme_val, current_extreme_idx))
                direction = -1
                current_extreme_val = val
                current_extreme_idx = i
        elif direction == -1: # Descending, looking for Valley
            if val < current_extreme_val:
                current_extreme_val = val
                current_extreme_idx = i
            elif val > current_extreme_val + epsilon:
                # Found Valley
                extrema.append(('V', current_extreme_val, current_extreme_idx))
                direction = 1
                current_extreme_val = val
                current_extreme_idx = i

    # 2. Scan P -> V -> P patterns
    episodes: List[DGEpisode] = []
    dg_index_total = 0.0
    
    # We need at least P, V, P
    if len(extrema) < 3:
        return [], 0.0
        
    for k in range(len(extrema) - 2):
        e1, e2, e3 = extrema[k], extrema[k+1], extrema[k+2]
        
        if e1[0] == 'P' and e2[0] == 'V' and e3[0] == 'P':
            p1_val = e1[1]
            v_val = e2[1]
            p2_val = e3[1]
            
            # Condition: Second peak must be higher (Deferred Gratification paid off)
            if p2_val > p1_val:
                drop = p1_val - v_val
                gain = p2_val - v_val
                
                if drop > 1e-9: # Avoid div by zero
                    score = gain / drop
                    episodes.append(DGEpisode(
                        start=e1[2],
                        end=e3[2],
                        peak=p1_val,
                        valley=v_val,
                        new_peak=p2_val
                    ))
                    dg_index_total += score

    return episodes, dg_index_total


__all__ = ["sortedness", "aggregation", "detect_dg", "DGEpisode"]
