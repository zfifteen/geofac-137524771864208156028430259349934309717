"""
Lightweight grid probe on the 127-bit challenge.

Explores corridor widths and composite energy weights, logging DG/Sortedness
and the top-ranked candidate energy.
"""

from itertools import product

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs, EnergySpec
from cellview.utils import candidates as cand_utils
from cellview.utils.challenge import CHALLENGE
from cellview.utils.rng import rng_from_hex


def run_once(window: int, algotype: str, samples: int = 20000):
    rng = rng_from_hex()
    cands = cand_utils.corridor_around_sqrt(CHALLENGE.n, rng, samples=samples, window=window)
    specs = default_specs()
    engine = CellViewEngine(
        N=CHALLENGE.n,
        candidates=cands,
        algotypes=[algotype],
        energy_specs=specs,
        rng=rng,
        sweep_order="ascending",
        max_steps=30,
    )
    res = engine.run()
    ranked = res["ranked_candidates"]
    top = ranked[0]
    return {
        "window": window,
        "algotype": algotype,
        "candidates": len(cands),
        "dg": res["dg_index"],
        "sorted_final": res["sortedness"][-1] if res["sortedness"] else None,
        "aggregation_final": res["aggregation"][-1] if res["aggregation"] else None,
        "top_n": top["n"],
        "top_energy": top["energy"],
    }


def main():
    windows = [500_000, 1_000_000, 5_000_000]
    algotypes = ["dirichlet11", "combo_dir11_arctan", "combo_dir11_res"]
    print("Challenge grid probe (20k samples per run, deterministic seed):")
    for window, algo in product(windows, algotypes):
        out = run_once(window, algo, samples=20_000)
        print(
            f"win={out['window']:,} algo={out['algotype']:<18} "
            f"DG={out['dg']:.5f} S_final={out['sorted_final']:.4f} "
            f"A_final={out['aggregation_final']:.4f} top_n={out['top_n']} energy={out['top_energy']}"
        )


if __name__ == "__main__":
    main()
