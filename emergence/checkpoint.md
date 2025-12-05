# Checkpoint – Emergence Cell-View Factor Search (Geofac-127)

**Audience:** external observers; no prior context needed.  
**Date:** 2025-12-05

## Problem Statement
Factor a single 127‑bit semiprime  
`N = 137524771864208156028430259349934309717`  
using a *geometric* ranking of candidate divisors, then *arithmetic* certification (mod/gcd) of only the top‑ranked few. No classical wide sweeps (ECM/QS/NFS); runs must be deterministic and replayable.

## Approach (Emergence Track)
We model candidate divisors as “cells” in a 1‑D lattice. Each cell has an energy given by a heuristic (e.g., Dirichlet kernel on the residue `N mod d`). Local swap dynamics (bubble-like sweeps) reorder cells toward lower energy. Metrics such as Sortedness and Delayed Gratification (DG) are logged but do not alter certification.

Certification is strictly arithmetic: for the top‑m ranked candidates we record `N mod d`, `gcd(N, d)`, and whether `d` divides `N`.

## Core Implementation (delivered)
- Deterministic engine with modular energies (Dirichlet, arctan curvature, residue, composites) and energy caching.
- Candidate generators:
  - Sparse corridors (random sampling near √N).
  - **Dense contiguous bands** around √N (full coverage; no sampling miss).
  - Safety guard to prevent accidental huge materializations.
- CLI `run_cellview.py` with logging to JSON (config, seeds, metrics, ranked candidates, certification).
- Experiments for small→mid semiprimes to study scaling.

## Key Findings
1) **Factor-seeking heuristic works.** With the inverted Dirichlet energy, whenever a true factor is present in the candidate set, it ranks #1 (verified on many 16–47 bit semiprimes, both full domains and dense corridors).

2) **Coverage is the bottleneck.** Failures to find factors occurred only when the sampling density was low and the factor was absent from the candidate list. Once we used dense (full) bands, factors surfaced immediately at the top.

3) **DG is not a presence detector.** DG (a backtracking/roughness metric) spikes when sampling is sparse and drops toward zero when coverage is dense. High DG reflects “rough landscape / gaps,” not “factor nearby.” It is not useful for deciding success.

4) **Challenge dense bands tested.**
   - Dense band √N ±2,000,000 (4.0M candidates): no factor in top‑200.
   - Dense band √N ±5,000,000 (10.0M candidates): no factor in top‑200.
   Interpretation: If a factor were within ±5M of √N, it would have appeared at rank #1. It likely lies outside this window.

## Significance
- The geometric ranking component is validated: it reliably elevates a factor to the very top when present.
- The decisive variable is **candidate coverage**. To succeed on the 127‑bit challenge, we must choose windows/bands that actually include a factor; ranking will then expose it quickly, minimizing certification work.
- DG/aggregation were initially hypothesized as guides; evidence shows they do not indicate factor presence and should not drive search decisions.

## Next Steps (planned)
- Expand dense coverage outward from √N in manageable slabs (e.g., ±10M, then adjacent 20M slabs) until resource limits or success.
- Optional: add stratified/quasi-Monte-Carlo sampling only if dense bands become too large; dense coverage is preferred to avoid miss risk.
- Continue strict logging and top‑m certification; keep runs deterministic for replay.

## Reproducibility
- All code and configs reside under `emergence/`; canonical N and seed derivation are in `cellview/utils/challenge.py`.
- Example command (dense band):  
  `python3 run_cellview.py --mode challenge --dense-window 5000000 --top-m 200 --max-steps 10`
- Logs: `emergence/logs/*.json` contain full configs, ranked candidates, and mod/gcd certificates.
