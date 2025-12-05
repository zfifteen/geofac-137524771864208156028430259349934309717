"""
Scaling ladder evaluation from small to mid-size semiprimes.

Purpose:
- Calibrate energies/DG/aggregation where ground truth factors are known.
- Observe how signals survive as bit-length grows and we move from full domains
  to corridor sampling (challenge-like).
"""

from dataclasses import dataclass
from typing import List, Optional

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.utils import candidates as cand_utils
from cellview.utils.rng import rng_from_hex
from cellview.utils.challenge import derive_seed_hex


@dataclass
class Case:
    p: int
    q: int
    mode: str  # "full", "corridor", or "corridor_full"
    window: Optional[int] = None
    samples: Optional[int] = None

    @property
    def N(self) -> int:
        return self.p * self.q

    @property
    def bits(self) -> int:
        return self.N.bit_length()


def factor_rank(ranked: List[dict], target: int) -> int:
    for idx, entry in enumerate(ranked, start=1):
        if int(entry["n"]) == target:
            return idx
    return -1


def run_case(case: Case, algotype: str):
    N = case.N
    seed_hex = derive_seed_hex(N)
    rng = rng_from_hex(seed_hex)

    if case.mode == "full":
        candidates = cand_utils.validation_full_domain(N)
    else:
        window = case.window or 50_000
        samples = case.samples or 50_000
        full = case.mode == "corridor_full"
        candidates = cand_utils.corridor_around_sqrt(N, rng, samples=samples, window=window, full=full)

    engine = CellViewEngine(
        N=N,
        candidates=candidates,
        algotypes=[algotype],
        energy_specs=default_specs(),
        rng=rng,
        sweep_order="random",  # encourage DG
        max_steps=40,
    )
    res = engine.run()
    ranked = res["ranked_candidates"]
    p_rank = factor_rank(ranked, case.p)
    q_rank = factor_rank(ranked, case.q)

    return {
        "N": N,
        "bits": case.bits,
        "mode": case.mode,
        "window": case.window,
        "samples": len(candidates),
        "algotype": algotype,
        "p_rank": p_rank,
        "q_rank": q_rank,
        "dg": res["dg_index"],
        "sorted_final": res["sortedness"][-1] if res["sortedness"] else None,
        "aggregation_final": res["aggregation"][-1] if res["aggregation"] else None,
        "top_n": ranked[0]["n"],
        "top_energy": ranked[0]["energy"],
    }


def main():
    cases = [
        Case(239, 251, "full"),  # 16-bit
        Case(4093, 4099, "full"),  # ~24-bit
        Case(65437, 65521, "full"),  # ~32-bit
        Case(104729, 104759, "full"),  # ~34-bit
        # mid-size corridor with high coverage (full corridor)
        Case(10_000_019, 10_000_079, "corridor_full", window=5_000, samples=20_000),  # ~48-bit
        # mid-size corridor with low sampling to illustrate miss risk
        Case(8_388_617, 8_388_593, "corridor", window=50_000, samples=20_000),  # ~46-bit (low coverage)
        # same corridor but full coverage to confirm factors appear
        Case(8_388_617, 8_388_593, "corridor_full", window=50_000, samples=200_000),  # ~46-bit (full coverage)
    ]
    algotypes = ["dirichlet11", "combo_dir11_arctan", "combo_dir11_res"]
    print("Small→mid scaling ladder (random sweeps, deterministic seeds):")
    for case in cases:
        for algo in algotypes:
            out = run_case(case, algo)
            print(
                f"bits={out['bits']:>3} mode={out['mode']:<8} algo={out['algotype']:<18} "
                f"p_rank={out['p_rank']:<4} q_rank={out['q_rank']:<4} "
                f"DG={out['dg']:.5f} S_final={out['sorted_final']:.4f} "
                f"A_final={out['aggregation_final']:.4f} top_n={out['top_n']}"
            )


if __name__ == "__main__":
    main()
