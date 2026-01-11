import pytest
import math
from backend.curve import apply_parallel_shock, apply_steepener, apply_custom_shock

@pytest.fixture
def sample_curve():
    return {0.5: 5.0, 2.0: 4.5, 10.0: 4.0, 30.0: 4.2}

def test_parallel_shock_positive(sample_curve):
    shocked = apply_parallel_shock(sample_curve, 100) # +1%
    assert math.isclose(shocked[0.5], 6.0)
    assert math.isclose(shocked[30.0], 5.2)

def test_parallel_shock_negative(sample_curve):
    shocked = apply_parallel_shock(sample_curve, -50) # -0.5%
    assert math.isclose(shocked[2.0], 4.0)
    assert math.isclose(shocked[10.0], 3.5)

def test_steepener_long_end_up(sample_curve):
    # Pivot at 2.0, +100bps at 30Y
    shocked = apply_steepener(sample_curve, 100, pivot_tenor=2.0)
    assert math.isclose(shocked[2.0], 4.5) # Pivot point unchanged
    assert math.isclose(shocked[30.0], 5.2) # 4.2 + 1.0
    assert shocked[0.5] < 5.0 # Short end lowered

def test_flattener_long_end_down(sample_curve):
    shocked = apply_steepener(sample_curve, -100, pivot_tenor=2.0)
    assert math.isclose(shocked[30.0], 3.2) # 4.2 - 1.0
    assert shocked[0.5] > 5.0   # Short end raised

def test_custom_shock_single_point(sample_curve):
    shocked = apply_custom_shock(sample_curve, {10.0: 50.0}) # +50bps at 10Y
    assert math.isclose(shocked[10.0], 4.5)
    assert math.isclose(shocked[2.0], 4.5) # Unchanged

def test_custom_shock_multi_point(sample_curve):
    shocked = apply_custom_shock(sample_curve, {2.0: 10.0, 30.0: -10.0})
    assert math.isclose(shocked[2.0], 4.6)
    assert math.isclose(shocked[30.0], 4.1)

def test_steepener_extrapolation_check(sample_curve):
    # Weight at t=0 should be -1
    # Weight at 2.0 should be 0
    # Weight at 30.0 should be 1
    # Check linear progression
    shocked = apply_steepener(sample_curve, 100, pivot_tenor=2.0)
    increase_at_10y = shocked[10.0] - sample_curve[10.0]
    increase_at_30y = shocked[30.0] - sample_curve[30.0]
    assert 0 < increase_at_10y < increase_at_30y

def test_shock_empty_curve():
    assert apply_parallel_shock({}, 100) == {}


# --- Network Failure Tests ---
from unittest.mock import patch
from backend import curve

def test_network_failure_returns_stale_cache():
    """When API fails, should return stale cached data if available."""
    # Inject stale cache
    curve._CURVE_CACHE['timestamp'] = 0  # Expired
    curve._CURVE_CACHE['data'] = ("2000-01-01", {10.0: 99.99})
    
    with patch('backend.curve.requests.get', side_effect=Exception("Network down")):
        date, data = curve.get_curve()
    
    assert date == "2000-01-01"
    assert data[10.0] == 99.99


def test_network_failure_raises_when_no_cache():
    """When API fails and no cache exists, should raise exception."""
    # Clear cache
    curve._CURVE_CACHE['timestamp'] = 0
    curve._CURVE_CACHE['data'] = None
    
    with patch('backend.curve.requests.get', side_effect=Exception("Network down")):
        with pytest.raises(Exception, match="Unable to fetch Treasury data"):
            curve.get_curve()

