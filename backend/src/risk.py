from __future__ import annotations
import math

def price_zero_coupon(rate_pct: float, tenor_years: float) -> float:
    """
    Calculate the price of a Zero-Coupon Bond with $100 face value.
    
    Formula: Price = 100 / (1 + r)^t
    where r is the annualized rate in decimal (rate_pct / 100).
    
    Preconditions:
    - rate_pct >= -100.0 (cannot lose more than 100%)
    - tenor_years >= 0
    """
    assert rate_pct >= -100.0, "Rate cannot be less than -100%"
    assert tenor_years >= 0, "Tenor cannot be negative"
    
    r = rate_pct / 100.0
    
    # Handle t=0 case
    if tenor_years == 0:
        return 100.0
        
    return 100.0 / ((1 + r) ** tenor_years)

def calculate_duration(rate_pct: float, tenor_years: float) -> float:
    """
    Calculate the Modified Duration of a Zero-Coupon Bond.
    
    For a Zero-Coupon bond, Macaulay Duration = tenor.
    Modified Duration = Macaulay Duration / (1 + r/n)
    Assuming annual compounding (n=1) for simplicity in this playground.
    
    Formula: ModDur = tenor / (1 + r)
    
    Preconditions:
    - tenor_years >= 0
    """
    assert tenor_years >= 0, "Tenor cannot be negative"
    
    r = rate_pct / 100.0
    return tenor_years / (1 + r)

def calculate_dv01(rate_pct: float, tenor_years: float) -> float:
    """
    Calculate DV01 (Dollar Value of an 01) for a Zero-Coupon Bond ($100 face).
    
    DV01 is approximately: Price * ModifiedDuration / 10000
    (Price change for 1 basis point shift).
    
    Returns positive value typically, though technically price drops as rate rises.
    We return the absolute magnitude of change.
    
    Preconditions:
    - tenor_years >= 0
    """
    price = price_zero_coupon(rate_pct, tenor_years)
    mod_dur = calculate_duration(rate_pct, tenor_years)
    
    # Classic approximation:
    # dP/dr approx -Price * ModDur
    # DV01 = change for dr = 0.0001
    
    dv01 = price * mod_dur * 0.0001
    return dv01
