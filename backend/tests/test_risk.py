import pytest
import math
from src.risk import price_zero_coupon, calculate_duration, calculate_dv01

# --- 1. Happy Path ---
def test_price_zero_coupon_nominal():
    """Test standard pricing: 5%, 1yr -> ~95.24."""
    p = price_zero_coupon(5.0, 1.0)
    assert math.isclose(p, 95.238095, rel_tol=1e-5)

def test_calculate_duration_nominal():
    """Test Duration: 5%, 10yr -> ~9.52."""
    d = calculate_duration(5.0, 10.0)
    assert math.isclose(d, 9.52381, rel_tol=1e-4)

# --- 2. Boundary Values ---
def test_price_zero_coupon_zero_rate():
    """Boundary: Rate = 0%. Price should be Face Value (100)."""
    p = price_zero_coupon(0.0, 5.0)
    assert p == 100.0

def test_price_zero_coupon_zero_tenor():
    """Boundary: Tenor = 0. Price should be 100 regardless of rate."""
    p = price_zero_coupon(10.0, 0.0)
    assert p == 100.0

def test_calculate_duration_zero_tenor():
    """Boundary: Tenor = 0 -> Duration = 0."""
    d = calculate_duration(5.0, 0.0)
    assert d == 0.0

# --- 3. Illegal Inputs (Preconditions) ---
def test_price_negative_tenor():
    """Illegal: Negative tenor should raise AssertionError."""
    with pytest.raises(AssertionError, match="Tenor cannot be negative"):
        price_zero_coupon(5.0, -1.0)

def test_price_rate_below_loss_limit():
    """Illegal: Rate < -100% (Price would technically be infinite/undefined physically)."""
    with pytest.raises(AssertionError, match="Rate cannot be less than -100%"):
        price_zero_coupon(-150.0, 5.0)

def test_dv01_negative_tenor():
    """Illegal: DV01 with negative tenor."""
    with pytest.raises(AssertionError, match="Tenor cannot be negative"):
        calculate_dv01(5.0, -5.0)
