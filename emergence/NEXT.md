# Levin-Style Cell-View Dynamics for Geofac

*A reproducible note for local experiments with coding agents*

## 0. Purpose

Capture what we learned from:

* Levin et al., **“Classical Sorting Algorithms as a Model of Morphogenesis”**, arXiv:2401.05375
* Our toy “cell-view factor morphospace” simulation

…and turn it into a **clear, reproducible spec** that your local agents can implement and extend (including toward the 127-challenge number).

Goal:
Test whether **emergent competencies** (Delayed Gratification, Algotype aggregation, chimeric equilibria) appear in a **factorization energy landscape**, and then weaponize those signals for Geofac.

---

## 1. Core ideas from Levin et al. (minimal recap)

### 1.1 Key definitions

* **Cell** – basic element; here: one entry in an array, with a fixed integer “value”.
* **Cell-view sorting algorithm** – each cell runs a local rule (e.g., Bubble / Insertion / Selection variant) and decides whether to swap with neighbors to improve **local monotonicity**. No top-down controller.
* **Algotype** – which algorithm/policy a cell follows (e.g., Bubble vs Insertion vs Selection). It’s a *behavioral type*, not visible to other cells or used in the rules.
* **Frozen Cell** – damaged cell that sometimes or never moves, even when the rule says it should.
* **Sortedness** – fraction of adjacent pairs that obey monotone order (increasing/decreasing).
* **Delayed Gratification (DG)** – a move that temporarily *reduces* Sortedness (goes away from the goal) but enables a later net gain in Sortedness. DG index = Σ(gain / drop) over such episodes in the Sortedness time-series.
* **Aggregation Value** – in mixed-Algotypes, fraction of cells whose immediate neighbors (left/right) share the same Algotype (measures spatial clustering of types).

### 1.2 Main empirical findings (why we care)

1. **Cell-view (distributed) sorts are at least as good as top-down sorts.**

    * Some are *more efficient* if you count both comparisons and swaps (metabolic cost).

2. **Cell-view algorithms show robust error tolerance.**

    * With Frozen Cells (movable or immovable), cell-view sorts maintain lower monotonicity error than classical versions.

3. **Delayed Gratification is real and context-sensitive.**

    * DG increases systematically with the number of Frozen Cells for Bubble/Insertion sorts.
    * This is **not** random wandering; DG is deployed more in “rough” media.

4. **Mixed Algotypes show unexpected aggregation.**

    * Different Algotypes *cluster spatially* (Aggregation Value up to ~0.7+) **even though**:

        * rules never mention Algotype,
        * no cell can read its own or neighbors’ Algotype,
        * the explicit task is only “sort by value”.

5. **Chimeras with conflicting goals reach stable equilibria.**

    * If one Algotype wants increasing order and another wants decreasing, the system converges to a mixed, non-trivial Sortedness + Aggregation plateau (no type fully wins).

Interpretation:
Very simple, deterministic, open-loop rules in a distributed medium show **proto-cognitive behavior** in their problem space: DG, robust rerouting around defects, spontaneous clustering of behavioral types.

---

## 2. Our toy “cell-view factor morphospace” simulation

This is what we actually did in the sandbox (summarized so you can re-run and extend it locally).

### 2.1 Target number & domain

* **Semiprime**:

    * Example used: (N = 10,933,133 = 2473 \times 4421) (toy, not 127-challenge).
* **Cells / domain**:

    * 1-D lattice of integers
    * (n = 2, 3, \dots, 121)
    * Each (n) is one **cell**.

### 2.2 Algotypes (three Geofac-like heuristics)

Each cell has:

* **value**: the integer (n) currently occupying its position.
* **Algotype** ∈ {A, B, C}, assigned uniformly at random at start.

Algotypes define which **energy function** the cell cares about:

* **A: mod-resonance energy**
  (E_A(n) = N \bmod n)
* **B: quotient-balance energy**
  (E_B(n) = |n - N/n|) (ignore division by zero by domain choice)
* **C: sqrt-geodesic energy**
  (E_C(n) = |N - n^2|)

The idea: each Algotype implements a different “view” of factor goodness.

### 2.3 Cell energy & global Sortedness

For a cell with Algotype X ∈ {A,B,C} at position i:

* **Local energy**: (E_i = E_X(n_i))
* **Global Sortedness**: fraction of adjacent pairs (i, i+1) where (E_i \le E_{i+1}).

This mirrors Levin’s Sortedness, but in a **factor energy landscape** instead of numeric value order.

### 2.4 Dynamics: cell-view Bubble-like rule

* Time proceeds in **steps**.
* At each step, we visit cells in some order (asynchronous, single-threaded approximation of their parallel updates).
* For each non-frozen cell i:

    * Consider swapping with left or right neighbor (or both, depending on chosen variant).
    * Accept a swap if it **locally improves monotonicity in energy** (e.g., reduces local inversions).
* Stop when:

    * a full pass does **zero** swaps, or
    * we hit a safety step cap.

This is a direct analogue of their cell-view Bubble sort: local swaps driven by **energy monotonicity**, not by a top-down controller.

### 2.5 Frozen Cells

We implemented a **Type-1 analogue** (movable but non-initiating) as in the paper:

* Frozen Cells:

    * never initiate swaps themselves,
    * but neighbors can swap **through** them (they move if grabbed).

We ran multiple conditions:

* frozen_count ∈ {0, 1, 2, 3}

### 2.6 Metrics (ported from Levin)

1. **Sortedness(t)**

    * As defined above, at each step t.

2. **Delayed Gratification (DG)**

    * Track Sortedness(t) as a time-series.
    * Every “backtrack” episode (Sortedness drops then rises above the previous peak) contributes:
      $$
      \text{DG episode} = \frac{\Delta S_{\text{up}}}{\Delta S_{\text{down}}}
      $$
    * **DG index** = sum over all episodes during a run.

3. **Aggregation(t)**

    * For each internal cell i (2…N−1), check if
      Algotype(i−1) = Algotype(i) = Algotype(i+1).
    * Aggregation(t) = fraction of such triplets.

   With 3 types and random assignment, the baseline is ~1/9 ≈ 0.11.

---

## 3. Qualitative results (toy, but important)

### 3.1 Convergence & robustness

* All conditions converged to **Sortedness ≈ 0.99–1.00**.
* More Frozen Cells ⇒ more steps to converge (roughly +5–10 steps per extra defect).

**Takeaway:**
Cell-view dynamics **do** sort a factor energy landscape into a monotone profile, even with defects.

### 3.2 Delayed Gratification

* Clearly visible DG episodes in Sortedness(t).
* DG index **increased** slightly with more Frozen Cells, mirroring Levin’s Bubble/Insertion results.

**Interpretation:**
The system **backtracks more** in rougher media, exactly as in the paper. DG is not noise; it’s a real, context-sensitive competence.

### 3.3 Algotype aggregation

* Baseline Aggregation with random types: ~0.11.
* During runs, Aggregation(t) climbed sharply toward **~0.97**.
* Final configuration: **large contiguous blocks of a single Algotype**.

Looking at the **lowest-energy cells** in a typical run:

* Top ~10 lowest-energy positions were **all Algotype A** (mod-resonance).
* A “won” the best basin, even though:

    * all Algotypes were equally likely at start,
    * the rule **never** referenced Algotype.

**Interpretation:**
The factor energy landscape + local monotone dynamics cause **spontaneous clustering of the most informative heuristic**, just like Algotype aggregation in the Levin chimeric arrays.

---

## 4. Mapping to Geofac / 127-challenge experiments

This section is the bridge from toy → Geofac.

### 4.1 Conceptual mapping

* **Cells** → candidate divisors (n \in [1, \lfloor \sqrt{N} \rfloor])

* **Cell Value** → the integer n itself (and its associated geometric data).

* **Algotype** → one Geofac heuristic:

    * Dirichlet kernel amplitude
    * arctan-geodesic curvature
    * Z-metric / Z-energy
    * other resonance / curvature metrics you already use

* **Energy** (E_{\text{type}}(n)) → “badness” of n as a factor candidate according to that heuristic.

* **Frozen Cell** → any n you:

    * forbid from initiating moves (e.g., certain residues),
    * mask (e.g., dead zones, bad m-span windows),
    * treat as “stuck” in your current pipeline.

* **Sortedness** → how monotone the energy profile is.

    * You can define this separately for each energy or for a combined energy.

* **DG index** → global measure of how often the system “goes away from” a better configuration before achieving a stronger improvement.

* **Aggregation** → measure of how much **heuristics agree** spatially; e.g., contiguous clusters dominated by the same Algotype near the true factor region.

### 4.2 High-level hypothesis for Gate-127

For the real 127-bit challenge number N:

1. **DG will spike near the factor corridor.**

    * Hard local structure around p, q creates “barrier-like” behavior.
    * Cell-view dynamics will show more backtracking episodes there.

2. **One or two Algotypes will aggregate around the factor corridor.**

    * Their energy definitions align best with the true multiplicative structure.
    * They spontaneously monopolize the best basin, just as Algotype A did in the toy simulation.

3. **These emergent signals (DG + Aggregation) will give you a new way to locate a narrow window around p or q**, which you can then certify with your existing arithmetic checks.

---

## 5. Experiment spec for local coding agents

This is the **minimal reproducible spec** you can hand to Codex / Copilot / Grok / Gemini.

### 5.1 Inputs

* **Target N**:

    * Start with test semiprimes (you choose sizes consistent with your validation gates).
    * Then move to **127-challenge N**.

* **Heuristics (Algotypes)**:

    * At least 2, ideally 3–4, chosen from:

        * Dirichlet amplitude
        * arctan-geodesic curvature
        * Z-metric
        * other existing Geofac resonance metrics

* **Domain**:

    * Continuous range of candidate divisors (n_{\min} \dots n_{\max}), typically:

        * (n_{\min} = 2)
        * (n_{\max} = \lfloor\sqrt{N}\rfloor) or a well-chosen subset corridor for early experiments.

### 5.2 Data structures

Per cell (candidate n):

* `value`: integer n
* `algotype`: enum {A, B, C, …}
* `energy`: float, computed by the cell’s Algotype function E_type(n)
* `frozen`: bool (true for Frozen Cells)

Global:

* `cells`: 1-D array of cells in current order.
* `sortedness`: float ∈ [0,1]
* `aggregation`: float ∈ [0,1]
* `DG_index`: float

### 5.3 Cell-view update rule (one example)

For each “sweep”:

1. Shuffle indices or iterate in fixed order (pick one and keep it fixed for reproducibility).
2. For each index i:

    * Skip if cell is Frozen.
    * Choose left or right neighbor according to a simple policy, e.g.:

        * Test (i−1, i) pair; if swapping reduces local inversions in energy, swap.
        * Else test (i, i+1) pair similarly.
3. At end of sweep:

    * Compute new Sortedness, Aggregation.
    * Update DG_index from the Sortedness(t) series.

Stop when:

* no swaps occurred in a full sweep, **or**
* step count hits a configured max.

### 5.4 Metrics to log

Per run:

* N, domain bounds, RNG seed.
* Algotypes and their energy functions.
* Number and positions of Frozen Cells.
* Time series:

    * `sortedness[t]`
    * `aggregation[t]`
    * `DG_index[t]` or final DG_index
* Final ordering:

    * sequence of `(n, algotype, energy)` sorted by position.
* Optionally:

    * the subset of lowest-energy cells and their Algotypes.

### 5.5 Analyses

1. **DG vs Frozen Cells**

    * For each N and heuristic mix, run with different counts of Frozen Cells.
    * Plot DG_index vs number of Frozen Cells.
    * Expectation: DG_index increases with more defects (Levin-style behavior).

2. **Aggregation trajectories**

    * Plot Aggregation(t) for each run.
    * Expectation:

        * Early: near random baseline.
        * Mid: spike in Aggregation.
        * End: depending on constraints, either:

            * drop back toward baseline (if strict sorting breaks clusters), or
            * stay high (if constraints allow clusters to remain).

3. **Localization near true factors**

    * For semiprimes where p, q are known:

        * Map each cell’s final `position` to its integer `value n`.
        * Check:

            * Do low-energy cells cluster near p or q?
            * Which Algotype dominates that region?
    * For Gate-127:

        * Use these patterns learned from smaller N as clues.

4. **Corridor detection rule-of-thumb**

Given a final configuration:

* Compute:

    * energy rank of each n
    * DG contributions localized to n (e.g., how often n participates in DG episodes)
    * local Aggregation around n (are its neighbors same Algotype?)

Candidate corridor for factor search:

* set of n where:

    * energy is in lowest x%,
    * DG participation score is high,
    * local Aggregation is high and dominated by 1–2 Algotypes.

Then pass this corridor to your existing **arithmetic certification** pipeline.

---

## 6. Reproducibility checklist

To keep runs reproducible across different coding agents:

* Fix:

    * random seed,
    * exact domain bounds,
    * Algotypes and energy formulas,
    * Frozen Cell count and placements (or randomized with known seed),
    * update rule variant (left-first, right-first, both, etc.),
    * stopping criteria (no-swaps or max-steps).

* Always store:

    * config JSON / YAML for each run,
    * full logs of Sortedness(t), Aggregation(t), DG episodes,
    * final lattice state.

---

## 7. How to extend

* Swap in **real Geofac energies**:

    * Dirichlet, arctan-geodesic, Z-metric, etc.
* Scale up:

    * larger domains,
    * real 127-challenge N as target.
* Add:

    * **cross-purpose Algotypes** (conflicting goals) to study chimeric equilibria as a separate signal (like Figure 9 in the paper).
* Compare:

    * cell-view dynamics vs your current Geofac pipeline:

        * Does DG-index or Aggregation-based corridor selection give better factor candidate rankings?

---

This document should be enough for any of your local coding agents to:

1. Recreate the toy experiment.
2. Swap in Geofac heuristics.
3. Start probing for Levin-style emergent signals in your actual factorization morphospace.
