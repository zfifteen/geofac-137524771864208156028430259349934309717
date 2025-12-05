#!/usr/bin/env python3
"""
CLI entrypoint for the emergence cell-view engine.
"""

import argparse
import json
import os
from typing import Dict

from cellview.cert.certify import certify_top_m
from cellview.engine.engine import CellViewEngine
from cellview.heuristics.core import default_specs
from cellview.utils import candidates as cand_utils
from cellview.utils.challenge import CHALLENGE
from cellview.utils.logging import ensure_dir, timestamp_id, write_json
from cellview.utils.rng import rng_from_hex


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emergence cell-view search engine (geofac)")
    parser.add_argument("--mode", choices=["challenge", "validation"], default="challenge")
    parser.add_argument("--override-n", type=int, help="Optional override modulus (for validation)")
    parser.add_argument("--samples", type=int, default=50_000, help="Samples for corridor mode")
    parser.add_argument("--window", type=int, default=cand_utils.DEFAULT_WINDOW, help="Window around sqrt(N)")
    parser.add_argument("--bands", type=str, help="Optional multiband spec center:window:samples,... (sparse)")
    parser.add_argument(
        "--dense-window",
        type=int,
        help="Use dense contiguous band of +/- dense_window around sqrt(N) (challenge mode only).",
    )
    parser.add_argument(
        "--dense-bands",
        type=str,
        help="Dense bands spec center:halfwidth,... (challenge mode only), full coverage per band.",
    )
    parser.add_argument("--algotypes", type=str, default="dirichlet5", help="Comma-separated algotypes")
    parser.add_argument("--sweep-order", choices=["ascending", "random"], default="ascending")
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--top-m", type=int, default=50, help="Number of candidates to certify")
    parser.add_argument("--seed-hex", type=str, help="Override seed hex")
    parser.add_argument("--candidates-file", type=str, help="Optional file with newline-separated candidates")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory to store JSON logs")
    return parser.parse_args()


def load_candidates(args, N, rng):
    if args.candidates_file:
        with open(args.candidates_file, "r", encoding="utf-8") as f:
            vals = [int(line.strip()) for line in f if line.strip()]
        return vals

    # Dense contiguous options (challenge mode)
    if args.dense_window:
        center = int((N ** 0.5))
        half = args.dense_window
        return cand_utils.dense_band(center, half)
    if args.dense_bands:
        bands_spec = []
        for token in args.dense_bands.split(","):
            center, half = token.split(":")
            bands_spec.append((int(center), int(half)))
        return cand_utils.dense_bands(bands_spec)

    if args.mode == "validation":
        if N > 10**12:
            raise ValueError("Validation mode expects small N; override N accordingly.")
        domain = cand_utils.validation_full_domain(N)
        return domain

    # challenge mode corridors
    if args.bands:
        bands_spec = []
        for token in args.bands.split(","):
            center, window, samples = token.split(":")
            bands_spec.append((int(center), int(window), int(samples)))
        return cand_utils.multiband_corridors(N, rng, bands_spec)

    return cand_utils.corridor_around_sqrt(N, rng, samples=args.samples, window=args.window)


def main():
    args = parse_args()
    N = args.override_n or CHALLENGE.n
    if args.mode == "challenge" and N != CHALLENGE.n:
        raise ValueError("Challenge mode must use canonical N; use validation mode to override.")

    algotypes = [a.strip() for a in args.algotypes.split(",") if a.strip()]
    energy_specs: Dict[str, any] = default_specs()
    rng = rng_from_hex(args.seed_hex)

    candidates = load_candidates(args, N, rng)
    if args.mode == "challenge":
        cand_utils.guard_dense_domain_for_challenge(len(candidates), n=N)

    engine = CellViewEngine(
        N=N,
        candidates=candidates,
        algotypes=algotypes,
        energy_specs=energy_specs,
        rng=rng,
        sweep_order=args.sweep_order,
        max_steps=args.max_steps,
    )
    run_results = engine.run()

    cert_results = certify_top_m(run_results["ranked_candidates"], N, m=args.top_m)

    payload = {
        "config": vars(args),
        "N": str(N),
        "seed_hex": args.seed_hex or CHALLENGE.seed_hex,
        "candidate_count": len(candidates),
        "results": run_results,
        "certification": cert_results,
    }

    ensure_dir(args.log_dir)
    run_id = timestamp_id("run")
    log_path = os.path.join(args.log_dir, f"{run_id}.json")
    write_json(log_path, payload)

    print(f"Run complete. Candidates: {len(candidates)}. Log: {log_path}")
    print(f"Top-{args.top_m} certified (showing first 5):")
    for row in cert_results[:5]:
        print(json.dumps(row, default=str))


if __name__ == "__main__":
    main()
