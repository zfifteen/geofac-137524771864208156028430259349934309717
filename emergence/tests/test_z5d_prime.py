import unittest
from cellview.utils import z5d_prime


class TestZ5DIntegration(unittest.TestCase):
    """Test Z5D prime generator integration and fallback."""
    
    def test_next_prime_basic(self):
        """Test that next_prime works for basic cases."""
        self.assertEqual(z5d_prime.next_prime(2), 2)
        self.assertEqual(z5d_prime.next_prime(3), 3)
        self.assertEqual(z5d_prime.next_prime(4), 5)
        self.assertEqual(z5d_prime.next_prime(10), 11)
        self.assertEqual(z5d_prime.next_prime(100), 101)
    
    def test_is_prime_basic(self):
        """Test that is_prime works for basic cases."""
        self.assertTrue(z5d_prime.is_prime(2))
        self.assertTrue(z5d_prime.is_prime(3))
        self.assertTrue(z5d_prime.is_prime(17))
        self.assertTrue(z5d_prime.is_prime(97))
        
        self.assertFalse(z5d_prime.is_prime(1))
        self.assertFalse(z5d_prime.is_prime(4))
        self.assertFalse(z5d_prime.is_prime(100))
    
    def test_fallback_works_without_z5d(self):
        """Test that fallback works when Z5D is not available."""
        # Force using fallback by setting use_z5d=False
        self.assertEqual(z5d_prime.next_prime(10, use_z5d=False), 11)
        self.assertTrue(z5d_prime.is_prime(17, use_z5d=False))
    
    def test_large_prime_generation(self):
        """Test that large prime generation works (with fallback)."""
        # Generate a 50-bit prime starting from 2^49
        start = 2**49
        prime = z5d_prime.next_prime(start)
        
        # Verify it's actually prime
        self.assertTrue(z5d_prime.is_prime(prime))
        
        # Verify it's >= start
        self.assertGreaterEqual(prime, start)
        
        # Verify it's in the expected range
        self.assertLess(prime, 2**50)
    
    def test_z5d_detection(self):
        """Test Z5D detection mechanism."""
        # This will typically return False in CI/test environments
        # but documents the detection mechanism
        is_available = z5d_prime._detect_z5d()
        self.assertIsInstance(is_available, bool)


if __name__ == '__main__':
    unittest.main()
