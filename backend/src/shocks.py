from __future__ import annotations
from typing import Dict, Any

# Type alias for clarity: {tenor_years: rate_percent}
Curve = Dict[float, float]

def apply_parallel_shock(curve: Curve, bps: float) -> Curve:
    """
    Apply a parallel shift to the entire yield curve.
    
    Preconditions:
    - bps is a finite float representing basis points (e.g., 50.0 for +50bps).
    - curve values are percentages (e.g., 4.50).
    """
    assert isinstance(bps, (int, float)), "bps must be a number"
    
    # Check for NaN/Inf isn't strictly Pythonic with assert, but valid for "finite" check
    # Python float('nan') != float('nan'), so we can check via math.isnan if imported, 
    # or just trust type for now in simple CSC148 style. 
    
    # 1 bp = 0.01%
    shift_amount = bps / 100.0

    new_curve = {}
    for tenor, rate in curve.items():
        new_curve[tenor] = rate + shift_amount
        
    return new_curve

def apply_steepener(curve: Curve, long_end_bps: float, pivot_tenor: float = 2.0) -> Curve:
    """
    Apply a steepening/flattening twist to the curve around a pivot point.
    
    The pivot point stays fixed (0 shock).
    Tenors > pivot_tenor move by a proportion of long_end_bps.
    Tenors < pivot_tenor move in the opposite direction.
    
    This is a simplified linear steepener based on distance from pivot.
    Formula: shock(t) = long_end_bps * ( (t - pivot) / (max_tenor - pivot) )
    
    Preconditions:
    - curve is not empty.
    - pivot_tenor exists in the curve's range or reasonable bounds.
    - max_tenor is determined dynamically from the input curve.
    """
    assert curve, "Curve cannot be empty"
    max_tenor = max(curve.keys())
    
    # Avoid division by zero if pivot == max_tenor
    if max_tenor == pivot_tenor:
        # Trivial case: if we pivot at the very end, treat it as flat or no-op dependent on def.
        # Let's pivot from 0 instead if this edge case hits, or just return copy.
        return curve.copy()
    
    new_curve = {}
    denominator = max(max_tenor - pivot_tenor, 0.001) # Prevent div/0 safe
    
    for tenor, rate in curve.items():
        # Linear weight based on distance from pivot
        weight = (tenor - pivot_tenor) / denominator
        # shock (bps) -> shock (pct)
        shock_val = (weight * long_end_bps) / 100.0
        new_curve[tenor] = rate + shock_val
        
    return new_curve

def apply_custom_shock(curve: Curve, shocks: Dict[float, float]) -> Curve:
    """
    Apply specific shocks to specific tenors.
    
    If a tenor in 'shocks' is not in 'curve', it is ignored.
    If a tenor in 'curve' is not in 'shocks', it remains unchanged.
    
    Preconditions:
    - shocks values are in basis points.
    """
    new_curve = curve.copy()
    
    for tenor, bump in shocks.items():
        if tenor in new_curve:
            new_curve[tenor] += (bump / 100.0)
            
    return new_curve
