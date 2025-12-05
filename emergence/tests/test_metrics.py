import unittest
from cellview.metrics.core import detect_dg, aggregation

class TestMetrics(unittest.TestCase):

    def test_dg_strict_logic(self):
        """Task 5: Validate P-V-P logic with strictly higher second peak."""
        # Series: Climb to 1.0, Drop to 0.2, Climb to 1.5, Drop to 0.0
        series = [0.0, 1.0, 0.2, 1.5, 0.0]
        
        episodes, index = detect_dg(series, epsilon=0.1)
        
        self.assertEqual(len(episodes), 1, "Should detect exactly 1 episode")
        ep = episodes[0]
        
        self.assertAlmostEqual(ep.peak, 1.0)
        self.assertAlmostEqual(ep.valley, 0.2)
        self.assertAlmostEqual(ep.new_peak, 1.5)
        
        # Calculation
        # Drop = 1.0 - 0.2 = 0.8
        # Gain = 1.5 - 0.2 = 1.3
        # Score = 1.3 / 0.8 = 1.625
        self.assertAlmostEqual(index, 1.625)

    def test_dg_ignore_smaller_recovery(self):
        """Task 5: Ensure we ignore cases where we don't improve (P2 <= P1)."""
        # Climb to 1.0, Drop to 0.2, Climb to 0.8, Drop to 0.0
        series = [0.0, 1.0, 0.2, 0.8, 0.0]
        episodes, index = detect_dg(series, epsilon=0.1)
        self.assertEqual(len(episodes), 0, "Should ignore episode where new peak < old peak")

    def test_aggregation_baseline(self):
        """Task 5: Check Aggregation computation."""
        # All same
        self.assertEqual(aggregation(["A", "A", "A", "A"]), 1.0)
        
        # Alternating (A != B != A)
        self.assertEqual(aggregation(["A", "B", "A", "B"]), 0.0)
        
        # Mixed: A A B B
        # Pairs: (A,A) match, (A,B) no, (B,B) match. Total 3 pairs. 2 matches.
        self.assertAlmostEqual(aggregation(["A", "A", "B", "B"]), 2/3)

if __name__ == '__main__':
    unittest.main()