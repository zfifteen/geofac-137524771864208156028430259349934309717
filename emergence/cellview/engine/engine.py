from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from decimal import Decimal

from cellview.heuristics.core import EnergySpec, resolve_energy, default_specs
from cellview.metrics.core import aggregation, detect_dg, sortedness


@dataclass
class Cell:
    n: int
    algotype: str
    frozen: bool = False
    energy: Optional[Decimal] = None  # position-independent


class CellViewEngine:
    def __init__(
        self,
        N: int,
        candidates: Sequence[int],
        algotypes: Sequence[str],
        energy_specs: Dict[str, EnergySpec],
        rng,
        sweep_order: str = "ascending",
        max_steps: int = 50,
        type2_immovable: bool = False,
    ):
        self.N = N
        self.rng = rng
        self.sweep_order = sweep_order
        self.max_steps = max_steps
        self.type2_immovable = type2_immovable
        self.energy_specs = energy_specs or default_specs()
        # cache keyed by (algotype, n) to support multiple energy families
        self.energy_cache: Dict[tuple, Decimal] = {}
        # Assign algotypes deterministically via cycle
        self.cells: List[Cell] = []
        algotypes = list(algotypes)
        if not algotypes:
            algotypes = ["dirichlet5"]
        for idx, val in enumerate(candidates):
            algo = algotypes[idx % len(algotypes)]
            self.cells.append(Cell(n=val, algotype=algo, frozen=False, energy=None))

    # --- energy helpers ---
    def energy_of(self, cell: Cell) -> Decimal:
        if cell.energy is not None:
            return cell.energy
        cache_key = (cell.algotype, cell.n)
        if cache_key in self.energy_cache:
            cell.energy = self.energy_cache[cache_key]
            return cell.energy
        spec = self.energy_specs.get(cell.algotype)
        if spec is None:
            # fallback: try registry by name
            fn = resolve_energy(cell.algotype)
            spec = EnergySpec(cell.algotype, fn, {})
            self.energy_specs[cell.algotype] = spec
        value = spec.fn(cell.n, self.N, spec.params)
        self.energy_cache[cache_key] = value
        cell.energy = value
        return value

    # --- dynamics ---
    def sweep_indices(self, length: int) -> List[int]:
        if self.sweep_order == "random":
            idxs = list(range(length - 1))
            self.rng.shuffle(idxs)
            return idxs
        return list(range(length - 1))

    def step(self) -> int:
        swaps = 0
        idxs = self.sweep_indices(len(self.cells))
        for i in idxs:
            a = self.cells[i]
            b = self.cells[i + 1]
            # Type-2: immovable if frozen flag set
            if self.type2_immovable and (a.frozen or b.frozen):
                continue
            # Type-1: frozen cannot initiate swap, but may be moved by neighbor
            if a.frozen and b.frozen:
                continue

            e_left = self.energy_of(a)
            e_right = self.energy_of(b)
            if e_left > e_right:
                # only allow if right is not frozen (it must "move into" lower energy slot)
                if not b.frozen:
                    self.cells[i], self.cells[i + 1] = self.cells[i + 1], self.cells[i]
                    swaps += 1
        return swaps

    def run(self) -> Dict:
        swaps_per_step: List[int] = []
        sortedness_series: List[float] = []
        aggregation_series: List[float] = []

        for _ in range(self.max_steps):
            swaps = self.step()
            swaps_per_step.append(swaps)
            sortedness_series.append(sortedness([c.n for c in self.cells]))
            aggregation_series.append(aggregation([c.algotype for c in self.cells]))
            if swaps == 0:
                break

        dg_episodes, dg_index = detect_dg(sortedness_series)
        final_state = [
            {"index": idx, "n": c.n, "algotype": c.algotype, "energy": str(self.energy_of(c))}
            for idx, c in enumerate(self.cells)
        ]

        ranked_candidates = sorted(final_state, key=lambda x: Decimal(x["energy"]))

        return {
            "swaps_per_step": swaps_per_step,
            "sortedness": sortedness_series,
            "aggregation": aggregation_series,
            "dg_episodes": [ep.__dict__ for ep in dg_episodes],
            "dg_index": dg_index,
            "final_state": final_state,
            "ranked_candidates": ranked_candidates,
        }


__all__ = ["Cell", "CellViewEngine"]
