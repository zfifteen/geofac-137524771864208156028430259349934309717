"""
Energy / resonance heuristics.

These are purely geometric scores computable from (N, n) without access to factors.
They are intended to be swapped in/out during experiments.
"""

from dataclasses import dataclass
from decimal import Decimal, getcontext
from math import cos, pi, isqrt
from typing import Callable, Dict

from cellview.utils.challenge import CHALLENGE

# Set generous precision for Decimal computations used in some heuristics.
getcontext().prec = 80


EnergyFn = Callable[[int, int, Dict], Decimal]


@dataclass(frozen=True)
class EnergySpec:
    name: str
    fn: EnergyFn
    params: Dict


def dirichlet_energy(n: int, N: int, params: Dict) -> Decimal:
    """
    Dirichlet kernel amplitude |D_j(2π*(N mod n)/n)| with optional normalization.
    """
    j = params.get("j", 5)
    normalize = params.get("normalize", True)
    invert = params.get("invert", True)  # when True, lower energy near residue 0
    mod_val = N % n
    x = 2 * pi * (mod_val / n)
    s = 1.0
    for k in range(1, j + 1):
        s += 2 * cos(k * x)
    if normalize:
        s = s / (2 * j + 1)
    val = abs(s)
    if invert:
        val = 1 - val
    return Decimal(val)


def arctan_geodesic_energy(n: int, N: int, params: Dict) -> Decimal:
    """
    Arctan-based curvature around sqrt(N). Lower is better (closer to sqrt).
    """
    sqrtN = params.get("sqrtN") or isqrt(N)
    scale = params.get("scale", 1.0)
    diff = abs(n - sqrtN) / sqrtN
    # arctan is smooth near zero, giving gentle valley near sqrtN
    return Decimal(abs(__import__("math").atan(scale * diff)))


def z_metric_energy(n: int, N: int, params: Dict) -> Decimal:
    """
    Placeholder "Z-metric": penalize distance from sqrt and residue magnitude together.
    """
    sqrtN = params.get("sqrtN") or isqrt(N)
    residue = N % n
    dist = abs(n - sqrtN)
    # combine with weights to stay finite
    alpha = params.get("alpha", 1.0)
    beta = params.get("beta", 1.0)
    return Decimal(alpha * (dist / sqrtN) + beta * (residue / n))


def residue_energy(n: int, N: int, params: Dict) -> Decimal:
    """
    Simple normalized residue magnitude. Lower is better.
    """
    return Decimal((N % n) / n)


def composite_energy(n: int, N: int, params: Dict) -> Decimal:
    """
    Weighted sum of sub-energies. Sub-energies are looked up by name in REGISTRY.
    """
    weights: Dict[str, float] = params.get("weights", {})
    sub_params: Dict[str, Dict] = params.get("sub_params", {})
    total = Decimal(0)
    wsum = 0.0
    for name, w in weights.items():
        fn = REGISTRY.get(name)
        if fn is None:
            raise ValueError(f"Composite energy references unknown fn '{name}'")
        sp = sub_params.get(name, {})
        total += Decimal(w) * fn(n, N, sp)
        wsum += w
    if wsum == 0:
        return Decimal(0)
    return total / Decimal(wsum)


REGISTRY: Dict[str, EnergyFn] = {
    "dirichlet": dirichlet_energy,
    "arctan": arctan_geodesic_energy,
    "zmetric": z_metric_energy,
    "residue": residue_energy,
    "composite": composite_energy,
}


def resolve_energy(name: str) -> EnergyFn:
    try:
        return REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown energy function: {name}") from exc


def default_specs() -> Dict[str, EnergySpec]:
    """
    Provide a small set of ready-to-use energy specs.
    """
    return {
        "dirichlet5": EnergySpec("dirichlet5", dirichlet_energy, {"j": 5, "normalize": True, "invert": True}),
        "dirichlet11": EnergySpec("dirichlet11", dirichlet_energy, {"j": 11, "normalize": True, "invert": True}),
        "arctan": EnergySpec("arctan", arctan_geodesic_energy, {"sqrtN": CHALLENGE.sqrt_n, "scale": 2.0}),
        "zmetric": EnergySpec("zmetric", z_metric_energy, {"sqrtN": CHALLENGE.sqrt_n, "alpha": 0.2, "beta": 1.0}),
        "combo_dir11_arctan": EnergySpec(
            "combo_dir11_arctan",
            composite_energy,
            {
                "weights": {"dirichlet": 0.6, "arctan": 0.4},
                "sub_params": {
                    "dirichlet": {"j": 11, "normalize": True, "invert": True},
                    "arctan": {"sqrtN": CHALLENGE.sqrt_n, "scale": 2.5},
                },
            },
        ),
        "combo_dir11_res": EnergySpec(
            "combo_dir11_res",
            composite_energy,
            {
                "weights": {"dirichlet": 0.6, "residue": 0.4},
                "sub_params": {
                    "dirichlet": {"j": 11, "normalize": True, "invert": True},
                    "residue": {},
                },
            },
        ),
    }


__all__ = [
    "EnergyFn",
    "EnergySpec",
    "dirichlet_energy",
    "arctan_geodesic_energy",
    "z_metric_energy",
    "resolve_energy",
    "default_specs",
]
