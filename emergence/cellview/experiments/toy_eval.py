"""
Batch toy evaluations for small semiprimes with known factors.

Purpose: measure where true factors land in the energy-ranked list and collect
DG/Aggregation signals to see if emergent metrics correlate with factor proximity.
"""

from decimal import Decimal
from typing import List, Tuple

from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.utils import candidates as cand_utils
from cellview.utils.challenge import derive_seed_hex
from cellview.utils.rng import rng_from_hex


ToyCase = Tuple[int, Tuple[int, int]]


def factor_ranks(ranked: List[dict], factors: Tuple[int, int]) -> Tuple[int, int]:
    ranks = {}
    for idx, entry in enumerate(ranked, start=1):
        n = int(entry["n"])
        if n in factors:
            ranks[n] = idx
    return ranks.get(factors[0], -1), ranks.get(factors[1], -1)


def run_case(N: int, factors: Tuple[int, int], algotypes: List[str]):
    seed_hex = derive_seed_hex(N)
    rng = rng_from_hex(seed_hex)
    domain = cand_utils.validation_full_domain(N)

    engine = CellViewEngine(
        N=N,
        candidates=domain,
        algotypes=algotypes,
        energy_specs=default_specs(),
        rng=rng,
        sweep_order="ascending",
        max_steps=50,
    )
    res = engine.run()
    ranked = res["ranked_candidates"]
    ranks = factor_ranks(ranked, factors)

    return {
        "N": N,
        "factors": factors,
        "candidate_count": len(domain),
        "factor_ranks": ranks,
        "dg_index": res["dg_index"],
        "aggregation_final": res["aggregation"][-1] if res["aggregation"] else None,
        "sortedness_final": res["sortedness"][-1] if res["sortedness"] else None,
    }


def main():
    cases: List[ToyCase] = [
        (221, (13, 17)),
        (899, (29, 31)),
        (1763, (41, 43)),
        (8051, (83, 97)),
        (10403, (101, 103)),
    ]
    algotypes = ["dirichlet5"]
    results = []
    for N, factors in cases:
        out = run_case(N, factors, algotypes)
        results.append(out)

    print("Toy evaluation (dirichlet5, full domain, deterministic seeds):")
    for r in results:
        print(
            f"N={r['N']} factors={r['factors']} count={r['candidate_count']} "
            f"ranks={r['factor_ranks']} DG={r['dg_index']:.6f} "
            f"agg_final={r['aggregation_final']:.3f} sorted_final={r['sortedness_final']:.3f}"
        )


if __name__ == "__main__":
    main()
