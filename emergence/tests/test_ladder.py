import unittest
from pathlib import Path
from cellview.utils.ladder import (
    generate_ladder,
    generate_unbalanced_semiprime,
    get_effective_seed,
    get_gate,
    load_ladder_yaml,
    BASE_SEED,
    RATIO,
    CHALLENGE_N,
    CHALLENGE_BITS,
    _is_prime,
    _simple_next_prime,
)


class TestPrimalityFunctions(unittest.TestCase):
    """Test basic primality functions."""
    
    def test_is_prime_small_primes(self):
        """Test that _is_prime correctly identifies small primes."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in primes:
            self.assertTrue(_is_prime(p), f"{p} should be prime")
    
    def test_is_prime_composites(self):
        """Test that _is_prime correctly rejects composites."""
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for c in composites:
            self.assertFalse(_is_prime(c), f"{c} should not be prime")
    
    def test_is_prime_edge_cases(self):
        """Test edge cases for primality."""
        self.assertFalse(_is_prime(0))
        self.assertFalse(_is_prime(1))
        self.assertTrue(_is_prime(2))
    
    def test_simple_next_prime(self):
        """Test that _simple_next_prime finds the next prime."""
        self.assertEqual(_simple_next_prime(2), 2)
        self.assertEqual(_simple_next_prime(3), 3)
        self.assertEqual(_simple_next_prime(4), 5)
        self.assertEqual(_simple_next_prime(10), 11)
        self.assertEqual(_simple_next_prime(14), 17)


class TestSeedDerivation(unittest.TestCase):
    """Test seed derivation logic."""
    
    def test_effective_seed_calculation(self):
        """Test that effective seeds are calculated correctly."""
        self.assertEqual(get_effective_seed(42, 10), 52)
        self.assertEqual(get_effective_seed(42, 20), 62)
        self.assertEqual(get_effective_seed(42, 127), 169)
        self.assertEqual(get_effective_seed(42, 130), 172)


class TestSemiprimeGeneration(unittest.TestCase):
    """Test unbalanced semiprime generation."""
    
    def test_generate_small_semiprime(self):
        """Test generating a small unbalanced semiprime."""
        gate = generate_unbalanced_semiprime(10, 52, RATIO)
        
        self.assertEqual(gate.target_bits, 10)
        self.assertIsNotNone(gate.N)
        self.assertIsNotNone(gate.p)
        self.assertIsNotNone(gate.q)
        
        # Verify it's actually a semiprime
        self.assertEqual(gate.N, gate.p * gate.q)
        
        # Verify both factors are prime
        self.assertTrue(_is_prime(gate.p))
        self.assertTrue(_is_prime(gate.q))
        
        # Verify p < q (p is smaller factor)
        self.assertLess(gate.p, gate.q)
        
        # Verify N is approximately the target bit size
        self.assertLessEqual(abs(gate.actual_bits - gate.target_bits), 2)
    
    def test_determinism(self):
        """Test that same seed produces same semiprime."""
        gate1 = generate_unbalanced_semiprime(20, 62, RATIO)
        gate2 = generate_unbalanced_semiprime(20, 62, RATIO)
        
        self.assertEqual(gate1.N, gate2.N)
        self.assertEqual(gate1.p, gate2.p)
        self.assertEqual(gate1.q, gate2.q)
    
    def test_different_seeds_produce_different_semiprimes(self):
        """Test that different seeds produce different semiprimes."""
        gate1 = generate_unbalanced_semiprime(30, 72, RATIO)
        gate2 = generate_unbalanced_semiprime(30, 73, RATIO)
        
        self.assertNotEqual(gate1.N, gate2.N)
    
    def test_unbalanced_property(self):
        """Test that p is well below sqrt(N)."""
        gate = generate_unbalanced_semiprime(60, 102, RATIO)
        
        # p should be much smaller than sqrt(N)
        # For 1:3 ratio, p gets ~25% of bits, so p should be << sqrt(N)
        self.assertLess(gate.p, gate.sqrt_N)
        
        # p should be a small fraction of sqrt(N)
        self.assertLess(gate.p_as_fraction_of_sqrt, 1.0)


class TestLadderGeneration(unittest.TestCase):
    """Test full ladder generation."""
    
    def test_ladder_length(self):
        """Test that ladder has correct number of gates."""
        ladder = generate_ladder()
        
        # Should have gates for 10, 20, 30, ..., 120, 127, 130
        # That's 12 gates from 10-120 (step 10) + 1 for 127 + 1 for 130 = 14 total
        self.assertEqual(len(ladder), 14)
    
    def test_ladder_ordering(self):
        """Test that gates are in ascending bit order."""
        ladder = generate_ladder()
        
        for i in range(len(ladder) - 1):
            self.assertLessEqual(
                ladder[i].target_bits, 
                ladder[i + 1].target_bits,
                "Ladder should be in ascending bit order"
            )
    
    def test_g127_is_challenge(self):
        """Test that G127 is the canonical challenge."""
        ladder = generate_ladder()
        
        g127 = next(g for g in ladder if g.gate == "G127")
        
        self.assertEqual(g127.target_bits, 127)
        self.assertEqual(g127.N, CHALLENGE_N)
        self.assertIsNone(g127.p)
        self.assertIsNone(g127.q)
        self.assertIsNone(g127.effective_seed)
        self.assertIsNotNone(g127.note)
        self.assertIn("challenge", g127.note.lower())
    
    def test_all_gates_present(self):
        """Test that all expected gates are present."""
        ladder = generate_ladder()
        gate_names = [g.gate for g in ladder]
        
        expected_gates = [
            "G010", "G020", "G030", "G040", "G050", "G060", 
            "G070", "G080", "G090", "G100", "G110", "G120", 
            "G127", "G130"
        ]
        
        self.assertEqual(sorted(gate_names), sorted(expected_gates))
    
    def test_generated_gates_have_factors(self):
        """Test that generated gates (not G127) have factors."""
        ladder = generate_ladder()
        
        for gate in ladder:
            if gate.gate == "G127":
                continue
            
            self.assertIsNotNone(gate.p)
            self.assertIsNotNone(gate.q)
            self.assertEqual(gate.N, gate.p * gate.q)
            self.assertTrue(_is_prime(gate.p))
            self.assertTrue(_is_prime(gate.q))


class TestGateRetrieval(unittest.TestCase):
    """Test gate retrieval functions."""
    
    def test_get_gate_existing(self):
        """Test retrieving an existing gate."""
        gate = get_gate("G030")
        
        self.assertIsNotNone(gate)
        self.assertEqual(gate.gate, "G030")
        self.assertEqual(gate.target_bits, 30)
    
    def test_get_gate_challenge(self):
        """Test retrieving the G127 challenge gate."""
        gate = get_gate("G127")
        
        self.assertIsNotNone(gate)
        self.assertEqual(gate.gate, "G127")
        self.assertEqual(gate.N, CHALLENGE_N)
    
    def test_get_gate_nonexistent(self):
        """Test that nonexistent gate returns None."""
        gate = get_gate("G999")
        self.assertIsNone(gate)
    
    def test_get_gate_with_pregenerated_ladder(self):
        """Test retrieving gate from pre-generated ladder."""
        ladder = generate_ladder()
        gate = get_gate("G050", ladder=ladder)
        
        self.assertIsNotNone(gate)
        self.assertEqual(gate.target_bits, 50)


class TestYAMLLoading(unittest.TestCase):
    """Test YAML configuration loading."""
    
    def test_load_ladder_yaml(self):
        """Test that YAML file can be loaded."""
        # This should load the validation_ladder.yaml file
        config = load_ladder_yaml()
        
        self.assertIsNotNone(config)
        self.assertIn("base_seed", config)
        self.assertIn("ratio", config)
        self.assertIn("ladder", config)
        
        self.assertEqual(config["base_seed"], BASE_SEED)
        self.assertEqual(config["ratio"], RATIO)
        
        # Check that ladder has entries
        self.assertGreater(len(config["ladder"]), 0)
    
    def test_yaml_has_all_gates(self):
        """Test that YAML includes all expected gates."""
        config = load_ladder_yaml()
        
        gate_names = [g["gate"] for g in config["ladder"]]
        
        expected_gates = [
            "G010", "G020", "G030", "G040", "G050", "G060",
            "G070", "G080", "G090", "G100", "G110", "G120",
            "G127", "G130"
        ]
        
        self.assertEqual(sorted(gate_names), sorted(expected_gates))
    
    def test_yaml_has_metadata(self):
        """Test that YAML has expected metadata."""
        config = load_ladder_yaml()
        
        self.assertIn("algotypes", config)
        self.assertIn("progression", config)
        
        # Check algotypes
        algotypes = config["algotypes"]
        algotype_names = [a["name"] for a in algotypes]
        self.assertIn("bubble", algotype_names)
        self.assertIn("selection", algotype_names)
        
        # Check progression criteria
        progression = config["progression"]
        self.assertIn("pass_criteria", progression)
        self.assertIn("time_budgets", progression)
        self.assertIn("top_m_for_certification", progression)


if __name__ == '__main__':
    unittest.main()
