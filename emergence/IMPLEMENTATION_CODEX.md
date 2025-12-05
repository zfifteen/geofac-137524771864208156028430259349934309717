# Implementation Plan (Codex Track — Emergence Cell-View Engine)

Purpose: build a deterministic, reproducible cell-view search engine that surfaces DG/aggregation signals and feeds a narrow, geometrically ranked candidate set to arithmetic certification for **N = 137524771864208156028430259349934309717**.

## 1) Canonical inputs & config
- Read N and seeds from the canonical challenge source (no duplication). Expose CLI/JSON config for:
  - domain/candidate set:
    - Validation mode (small N): full [2, floor(sqrt N)] allowed.
    - Challenge mode (127-bit): sparse candidate list or narrow/sliding windows (e.g., sqrt(N)±W or multi-band corridors); never materialize a dense 0..√N lattice.
  - Algotypes/energy definitions and params,
  - RNG seed, sweep order, frozen cell count/placement,
  - stopping criteria (max_steps, no-swap halt).
- Ensure deterministic seeding derived from N unless explicitly overridden.

## 2) Data model
- Cell struct: `value n`, `algotype`, `frozen`, `energy`.
- Array (1-D lattice) with deterministic index order.
- Energy layer modular: plug-in interface for heuristics (Dirichlet amplitude, arctan-geodesic curvature, Z-metric, etc.).
- Suggested module layout (borrowed where useful from the Gemini scaffold):
  - `cell` (struct/class),
  - `heuristics` (Algotype enum + energy functions; include toy and real Geofac variants),
  - `metrics` (Sortedness, Aggregation, DG extractor),
  - `engine` (cell-view sweeps and swap rule),
  - `utils` (seeded RNG, canonical N loader),
  - `visualization` (plots for S(t), A(t), DG using logs only),
  - `experiments` scripts for toy semiprimes and the 127-bit run.

## 3) Dynamics engine
- Implement cell-view Bubble-like sweep:
  - Fixed or seeded-permutation sweep order (logged).
  - Non-frozen cells may swap with neighbor if it reduces local energy inversions; Frozen Type-1 never initiate but can be moved.
  - Optional toggle for Type-2 (immovable) for experiments.
- Terminate on no-swaps-in-sweep or max_steps.
- Instrument to record swaps per step.
- Neighbor notion: adjacency is in the candidate list order (rank-order topology), not necessarily consecutive integers; local monotonicity is over that ordering.

## 4) Metrics & logging
- Time series per run: Sortedness S(t), Aggregation A(t), swap counts.
- DG extraction post-run from S(t) peaks/valleys; store DG episodes and total DG index.
- Final lattice dump: ordered `(index, n, algotype, energy)`.
- Ranked candidate list (by chosen geometric score) to pass to certifier.
- Log full config + RNG seed for replay; write JSON in `logs/` with run id.
- Keep plotting/summary scripts purely log-driven (no hidden computation) for auditability.
- DG extraction should use a hysteresis/epsilon peak-valley detector to avoid counting noise as episodes.

## 5) Certification bridge
- Take top-m ranked `n` values from final state (or lowest-energy set) and run arithmetic check (`N mod n`, `gcd(N, n)`).
- Record ranks, geometric scores, and mod/gcd results in the log; no other factoring methods.

## 6) Experiment harness (XP)
- Batch runner to sweep parameter grids:
  - energy sets / Algotypes,
  - window/domain choices,
  - frozen cell counts,
  - sweep orders.
- Aggregate metrics: DG vs defects, Aggregation peaks, factor rank (for test semiprimes), runtime/step counts.

## 7) Validation steps
- Unit tests: energy functions, swap rule correctness, determinism of sweep order/seeds, DG extraction.
- Integration tests on small semiprimes with known factors injected into domain; verify factor appears in top-m and logs cert.
- Determinism check: same seed/config → identical logs and final lattice.

## 8) Scalability & perf
- Use Python `int`/gmpy2 (or decimal where appropriate) for N and n; if numpy is used, enforce object dtype to avoid overflow; avoid float drift where ordering matters.
- Cache/memoize energies per candidate (position-independent) to avoid recomputation in swaps.
- Stream/avoid large copies; optional sparse corridor mode to limit memory.
- Profiling hooks to measure steps and wall time per run.

## 9) Guardrails & audits
- No factor constants or external factoring APIs in any path.
- No wide classical sweeps; certification limited to ranked top-m.
- Ensure all N usage comes from the canonical config; changing N is a breaking change.

## 10) Deliverables
- Reproducible CLI entrypoint (Python preferred here) with documented flags.
- Logging schema doc and sample run artifacts.
- Scripts/notebooks to visualize S(t), A(t), DG episodes, and candidate corridors.
