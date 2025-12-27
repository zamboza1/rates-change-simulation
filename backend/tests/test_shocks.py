import pytest
from src.shocks import apply_parallel_shock, apply_steepener, apply_custom_shock

# --- Fixtures / Constants ---
NOMINAL_CURVE = {2.0: 4.00, 10.0: 5.00}
EMPTY_CURVE = {}

# --- 1. Happy Path ---
def test_apply_parallel_shock_nominal():
    """Test standard parallel shift (+50bps)."""
    new_curve = apply_parallel_shock(NOMINAL_CURVE, bps=50.0)
    assert new_curve[2.0] == 4.50
    assert new_curve[10.0] == 5.50

def test_apply_steepener_nominal():
    """Test steepener around pivot."""
    # Pivot at 2.0 (unchanged), long end +100bps
    new_curve = apply_steepener(NOMINAL_CURVE, long_end_bps=100.0, pivot_tenor=2.0)
    assert new_curve[2.0] == 4.00
    assert new_curve[10.0] == 6.00

# --- 2. Boundary Values ---
def test_apply_parallel_shock_zero_bps():
    """Boundary: 0 shift should result in identical curve."""
    new_curve = apply_parallel_shock(NOMINAL_CURVE, bps=0.0)
    assert new_curve == NOMINAL_CURVE

def test_apply_parallel_shock_negative_rates():
    """Boundary: Large negative shock pushing rates below zero (valid in logic)."""
    # -500 bps = -5.00%
    new_curve = apply_parallel_shock(NOMINAL_CURVE, bps=-500.0)
    assert new_curve[2.0] == -1.00 # 4.00 - 5.00

def test_steepener_pivot_at_end():
    """Boundary: Pivot is exactly the max tenor."""
    # Pivot at 10.0. Weight = (t - 10) / (10 - 10). Code handles div/0 safe or logic.
    # Implementation used max(denominator, 0.001).
    # If pivot=10, max_tenor=10. Denom=0.001.
    # For t=10: weight=0 -> shock=0.
    new_curve = apply_steepener(NOMINAL_CURVE, long_end_bps=100.0, pivot_tenor=10.0)
    assert new_curve[10.0] == 5.00

# --- 3. Empty/Smallest Case ---
def test_apply_parallel_shock_empty():
    """Empty: Applying shock to empty curve returns empty curve."""
    new_curve = apply_parallel_shock(EMPTY_CURVE, bps=50.0)
    assert new_curve == {}

def test_steepener_empty_fail():
    """Empty: Steepener requires non-empty curve to find max tenor."""
    # Precondition in code: assert curve, "Curve cannot be empty"
    with pytest.raises(AssertionError, match="Curve cannot be empty"):
        apply_steepener(EMPTY_CURVE, long_end_bps=100.0)

# --- 4. Illegal Inputs (Preconditions) ---
def test_parallel_shock_invalid_type():
    """Illegal: bps is not a number."""
    with pytest.raises(AssertionError, match="bps must be a number"):
        apply_parallel_shock(NOMINAL_CURVE, bps="fifty") # type: ignore

def test_custom_shock_partial():
    """Graybox/State: Custom shock with keys not in curve (ignored)."""
    shocks = {2.0: 10.0, 99.0: 50.0} # 99.0 doesn't exist
    new_curve = apply_custom_shock(NOMINAL_CURVE, shocks)
    assert new_curve[2.0] == 4.10 # +10bps
    assert 99.0 not in new_curve  # Should not be added
