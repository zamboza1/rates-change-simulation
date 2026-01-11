import pytest
import math
from backend.bond import calculate_duration, calculate_dv01

def test_duration_at_zero_percent():
    # ModDur = t / (1 + r). If r=0, ModDur = t.
    assert calculate_duration(0.0, 10.0) == 10.0

def test_duration_at_one_hundred_percent():
    # ModDur = 10 / (1 + 1.0) = 5.0
    assert calculate_duration(100.0, 10.0) == 5.0

def test_dv01_at_zero_percent():
    # Price = 100 / (1+0)^10 = 100
    # ModDur = 10 / (1+0) = 10
    # DV01 = 100 * 10 * 0.0001 = 0.1
    assert math.isclose(calculate_dv01(0.0, 10.0), 0.1)

def test_duration_sensitivity():
    # Higher rates should result in lower modified duration
    d1 = calculate_duration(4.0, 10.0)
    d2 = calculate_duration(5.0, 10.0)
    assert d2 < d1

def test_dv01_sensitivity():
    # Higher rates should result in lower DV01 (price is lower)
    dv1 = calculate_dv01(4.0, 10.0)
    dv2 = calculate_dv01(5.0, 10.0)
    assert dv2 < dv1

def test_negative_rates_duration():
    # ModDur = 10 / (1 - 0.01) = 10 / 0.99 = 10.101
    assert math.isclose(calculate_duration(-1.0, 10.0), 10.10101, rel_tol=1e-5)

def test_very_long_tenor_dv01():
    # 100 year bond at 5%
    # Price = 100 / (1.05^100) = 0.76
    # ModDur = 100 / 1.05 = 95.24
    # DV01 = 0.76 * 95.24 * 0.0001 = 0.007
    dv = calculate_dv01(5.0, 100.0)
    assert dv > 0
    assert dv < 0.01

def test_zero_tenor_metrics():
    # t=0 should have 0 duration and 0 DV01
    assert calculate_duration(5.0, 0.0) == 0.0
    assert calculate_dv01(5.0, 0.0) == 0.0
