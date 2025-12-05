# Geofac-127 Mission Goal (Local Emergence Track)

Purpose: factor **N = 137524771864208156028430259349934309717** by ranking a small, geometrically informed candidate set, then certifying only the top-m via `N mod d` / `gcd(N, d)`—no broad classical sweeps (no ECM/QS/NFS, no bulk trial division outside the ranked set).

Key constraints
- Geometry ranks, arithmetic certifies; every reported factor must be logged with its certificate and be replayable.
- Deterministic, reproducible runs (seeds derived from N); single canonical source of N and derived constants; no factor injection or hidden oracles.
- Small candidate sets only; no fallback to wide classical search paths.

Emergence-driven approach (this subdir)
- Apply Levin-style **cell-view dynamics** on a factor-energy landscape: candidates are “cells”; multiple heuristics act as **Algotypes**; optional “Frozen” cells model defects.
- Track **Sortedness**, **Delayed Gratification (DG)** backtracking episodes, and **Algotype Aggregation** as emergent signals that may pinpoint a narrow corridor around p or q.
- Swap toy energies (mod/quotient/sqrt) for real Geofac heuristics (Dirichlet amplitude, arctan-geodesic curvature, Z-metric, etc.) while keeping the same dynamics and logging.
- Keep the energy layer **modular** so Algotypes/heuristics can be swapped or added without changing dynamics; treat each candidate divisor as an autonomous cell in a 1-D array using only local rules (no global controller), mirroring biological self-organization.
- Design for **scalability**: implementations should run from small validation semiprimes up to the 127-bit target, with attention to numeric types and memory/perf; defects/Frozen cells should be naturally handled by the distributed dynamics.

Implementation guideposts (pulling useful structure from Gemini)
- Organize code into small modules: `cell` (struct), `heuristics` (Algotype enum + energy fns), `metrics` (Sortedness, Aggregation, DG extractor), `engine` (cell-view sweeps and swap rule), `utils` (seeded RNG, canonical N loader), `visualization` (plots for S(t), A(t), DG), and `experiments` scripts for toy semiprimes and the 127-bit run.
- Use high-precision integer/decimal math (e.g., gmpy2/decimal) for energies to avoid ordering drift on the 127-bit target.
- Provide plotting/summary scripts that read logs only (no hidden computation) to visualize emergent signals and corridor selection.

Success criteria
- A factor of N appears early in the geometrically ranked list and is certified with logged `N mod d`/`gcd(N, d)`, with a replayable artifact bundle.
- DG/aggregation signals measurably improve corridor selection versus current baseline ranking.

Guardrails for all work here
- No hard-coding of factors; no external factoring services; no stochastic nondeterminism beyond seeded RNG.
- All configs/readers pull N from the canonical challenge definition; any change to N is treated as breaking.
- Logs must include N, parameters, RNG seeds, ranked candidates with scores, and certification outcomes for audit/replay.
