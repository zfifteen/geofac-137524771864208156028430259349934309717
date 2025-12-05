import unittest
import tempfile
import shutil
import os
import json
from decimal import Decimal
from cellview.engine.engine import CellViewEngine
from cellview.utils import challenge
from cellview.utils import rng
from cellview.utils import candidates as cand_utils
from cellview.heuristics.core import default_specs

class TestGuardrails(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_canonical_n(self):
        """Task 1: Assert N is loaded only from canonical source."""
        expected_n = 137524771864208156028430259349934309717
        self.assertEqual(challenge.CHALLENGE.n, expected_n)
        self.assertEqual(challenge.N_VALUE, expected_n)

    def test_determinism(self):
        """Task 1: Verify runs are identical given same config/seed."""
        N = 10_933_133
        candidates = list(range(2, 100))
        specs = default_specs()
        seed_hex = "abcdef123456"
        
        rng1 = rng.rng_from_hex(seed_hex)
        engine1 = CellViewEngine(N, candidates, ["dirichlet5"], specs, rng1, max_steps=10)
        res1 = engine1.run()
        
        rng2 = rng.rng_from_hex(seed_hex)
        engine2 = CellViewEngine(N, candidates, ["dirichlet5"], specs, rng2, max_steps=10)
        res2 = engine2.run()

        self.assertEqual(res1['swaps_per_step'], res2['swaps_per_step'])
        self.assertEqual(res1['dg_index'], res2['dg_index'])
        
        state1 = [(c['n'], c['energy']) for c in res1['final_state']]
        state2 = [(c['n'], c['energy']) for c in res2['final_state']]
        self.assertEqual(state1, state2)

    def test_challenge_mode_sparse_guard(self):
        """Task 3: Test that Challenge mode rejects dense domain allocation."""
        try:
            cand_utils.guard_dense_domain_for_challenge(100, n=challenge.CHALLENGE.n)
        except ValueError:
            self.fail("Should not raise for small count")

        try:
            cand_utils.guard_dense_domain_for_challenge(60_000_000, n=challenge.CHALLENGE.n)
            self.fail("Should raise for > 50M count")
        except ValueError:
            pass

    def test_energy_caching(self):
        """Task 4: Confirm energies are cached."""
        N = 100
        candidates = [10, 20]
        specs = default_specs()
        rng1 = rng.rng_from_hex("123")
        
        engine = CellViewEngine(N, candidates, ["dirichlet5"], specs, rng1)
        
        cell0 = engine.cells[0]
        e1 = engine.energy_of(cell0)
        
        # RESET cell's internal property
        cell0.energy = None
        
        # Modify engine cache using correct (algotype, n) key
        cache_key = (cell0.algotype, cell0.n)
        engine.energy_cache[cache_key] = Decimal("999.99")
        
        e2 = engine.energy_of(cell0)
        
        self.assertEqual(e2, Decimal("999.99"), "Engine did not use cached energy value")

if __name__ == '__main__':
    unittest.main()
