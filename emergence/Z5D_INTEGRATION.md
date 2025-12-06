# Z5D Prime Generator Integration

## Overview

The validation ladder now uses the **Z5D Prime Predictor** for generating large primes when available. Z5D is a high-performance C toolkit that uses a proprietary five-dimensional algorithm based on the Riemann Hypothesis to efficiently predict and locate large primes.

**Repository:** https://github.com/zfifteen/z5d-prime-predictor

## Architecture

The integration uses a wrapper pattern that gracefully falls back to Miller-Rabin when Z5D is unavailable:

```
ladder.py → z5d_prime.py → { Z5D (if available) OR Miller-Rabin (fallback) }
```

### Files

- `emergence/cellview/utils/z5d_prime.py` - Z5D wrapper with fallback
- `emergence/cellview/utils/ladder.py` - Uses Z5D for prime generation
- `emergence/tests/test_z5d_prime.py` - Tests for Z5D integration

## Usage

### Automatic (Recommended)

The ladder generator automatically uses Z5D when available:

```python
from cellview.utils.ladder import generate_ladder

# Automatically uses Z5D if available, falls back to Miller-Rabin otherwise
ladder = generate_ladder()
```

### Manual Control

You can explicitly control Z5D usage:

```python
from cellview.utils.z5d_prime import next_prime, is_prime

# Try Z5D first, fall back if unavailable
p = next_prime(1000)  # or next_prime(1000, use_z5d=True)

# Force Miller-Rabin fallback
p = next_prime(1000, use_z5d=False)

# Test primality
is_prime(17)  # True
```

## Z5D Availability

Z5D requires:
- Apple Silicon (M1/M2/M3)
- macOS
- Homebrew installation of `mpfr` and `gmp`
- Compiled Z5D tools in PATH

### Installation (macOS Apple Silicon only)

```bash
# Install dependencies
brew install mpfr gmp

# Clone and build Z5D
git clone https://github.com/zfifteen/z5d-prime-predictor.git
cd z5d-prime-predictor/src/c
./build_all.sh

# Add to PATH (example)
export PATH="$PATH:/path/to/z5d-prime-predictor/src/c/prime-generator/bin"
```

### Detection

The wrapper automatically detects Z5D availability by checking if `prime_generator` is in PATH:

```python
from cellview.utils.z5d_prime import _detect_z5d

if _detect_z5d():
    print("Z5D available - using optimized prime generation")
else:
    print("Z5D not available - using Miller-Rabin fallback")
```

## Fallback Behavior

When Z5D is not available (e.g., on Linux, Windows, or without compilation):
- Falls back to Miller-Rabin probabilistic primality testing
- Maintains determinism (same seed → same results)
- Still fast (sub-second for 130-bit primes)
- 100% Python stdlib (no external dependencies)

## Performance

**With Z5D (Apple Silicon):**
- Optimized for very large primes (100+ bits)
- Leverages prime-density predictions
- Geodesic-informed candidate jumping

**With Miller-Rabin Fallback (Any Platform):**
- Fast enough for validation ladder (< 0.01s for all 14 gates)
- Probabilistic with error < 2^-20 (k=10 rounds)
- Deterministic given same RNG seed

## Testing

All tests work with or without Z5D:

```bash
cd emergence
python3 -m unittest tests.test_z5d_prime -v
python3 -m unittest tests.test_ladder -v
```

Tests verify:
- Fallback works correctly
- Prime generation is deterministic
- Z5D detection mechanism
- Integration with ladder generator

## Design Principles

1. **Graceful Degradation:** Works everywhere, optimized for Apple Silicon
2. **Zero Dependencies:** Falls back to pure Python stdlib
3. **Determinism:** Same seed produces same results regardless of backend
4. **Transparency:** Clear logging of which backend is used
5. **Testability:** All tests pass with or without Z5D

## Notes

- Z5D `prime_generator` is called via subprocess with CSV output
- Timeout: 60 seconds per prime (configurable)
- Z5D availability is cached after first detection
- Miller-Rabin is always used for `is_prime()` (Z5D doesn't expose direct primality test)

## Future Enhancements

Potential improvements if Z5D integration proves beneficial:
- Python bindings via ctypes/cffi for lower overhead
- Batch prime generation for multiple gates
- Configurable Z5D parameters (precision, MR rounds)
- Performance metrics logging (Z5D vs fallback comparison)
