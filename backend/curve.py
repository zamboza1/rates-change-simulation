"""
US Treasury Yield Curve Data & Shock Scenarios
Fetches live data from US Treasury API and applies scenario shocks.
"""
import requests
import time
from typing import Dict, Tuple

# Cache mechanism with 3600s TTL (1 hour)
_CURVE_CACHE = {
    'timestamp': 0,
    'data': None
}

CACHE_TTL = 3600  # 1 hour


def get_curve() -> Tuple[str, Dict[float, float]]:
    """
    Fetches the latest US Treasury yield curve from the official API.
    Returns: (date_str, {tenor: yield_pct})
    
    Implements caching with fallback to stale data on network failure.
    """
    now = time.time()
    
    # Return fresh cache if available
    if _CURVE_CACHE['data'] and (now - _CURVE_CACHE['timestamp']) < CACHE_TTL:
        return _CURVE_CACHE['data']
    
    try:
        # Try current year first, then fallback to previous year (e.g. early January)
        from datetime import datetime
        current_year = datetime.now().year
        years_to_try = [current_year, current_year - 1]
        
        response = None
        for year in years_to_try:
            try:
                url = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv"
                # Add User-Agent header to avoid being blocked
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                response = resp
                break # Success
            except Exception as e:
                print(f"Failed to fetch data for {year}: {e}")
                continue
        
        if not response:
            raise Exception("Could not fetch Treasury data for current or previous year.")
        response.raise_for_status()
        
        # Parse CSV safely
        import csv
        import io
        
        f = io.StringIO(response.text.strip())
        reader = csv.reader(f)
        headers = next(reader)  # Header row
        try:
            latest_row = next(reader) # First data row is latest
        except StopIteration:
            raise Exception("CSV is empty (no data rows)")
        
        date_str = latest_row[0]
        
        # Map columns to tenors (in years)
        # Note: CSV headers might change format slightly, logic maps standard names
        tenor_mapping = {
            '1 Mo': 1/12,
            '2 Mo': 2/12,
            '3 Mo': 0.25,
            '4 Mo': 4/12,
            '6 Mo': 0.5,
            '1 Yr': 1.0,
            '2 Yr': 2.0,
            '3 Yr': 3.0,
            '5 Yr': 5.0,
            '7 Yr': 7.0,
            '10 Yr': 10.0,
            '20 Yr': 20.0,
            '30 Yr': 30.0
        }
        
        curve = {}
        for i, header in enumerate(headers):
            # clean header just in case
            header_clean = header.strip()
            if header_clean in tenor_mapping and i < len(latest_row):
                try:
                    val_str = latest_row[i].strip()
                    if val_str and val_str != 'ND': # Handle No Data
                        yield_val = float(val_str)
                        curve[tenor_mapping[header_clean]] = yield_val
                except (ValueError, IndexError):
                    continue
        
        # Update cache
        _CURVE_CACHE['timestamp'] = now
        _CURVE_CACHE['data'] = (date_str, curve)
        
        return date_str, curve
        
    except Exception as e:
        print(f"Treasury API error: {e}")
        
        # Return stale cache if available
        if _CURVE_CACHE['data']:
            print("Returning stale cached data")
            return _CURVE_CACHE['data']
        
        # No fallback data - raise error
        raise Exception(f"Unable to fetch Treasury data: {str(e)}. No cached data available.")


def apply_parallel_shock(curve: Dict[float, float], magnitude_bps: float) -> Dict[float, float]:
    """
    Apply a parallel shift to the entire yield curve.
    
    Args:
        curve: {tenor: yield_pct}
        magnitude_bps: Shift in basis points (+100 = +1%)
    
    Returns:
        Shocked curve with all yields shifted by magnitude_bps
    """
    shift_pct = magnitude_bps / 100.0
    return {tenor: yld + shift_pct for tenor, yld in curve.items()}


def apply_steepener(curve: Dict[float, float], magnitude_bps: float, pivot_tenor: float = 2.0) -> Dict[float, float]:
    """
    Apply a steepener/flattener twist around a pivot point.
    
    The pivot point stays unchanged. Points before the pivot move opposite
    to points after the pivot, creating a twist effect.
    
    Args:
        curve: {tenor: yield_pct}
        magnitude_bps: Twist magnitude at the long end (+100 = steepen by 1%)
        pivot_tenor: The tenor that remains unchanged (default 2.0 years)
    
    Returns:
        Shocked curve with twist applied
    """
    shift_pct = magnitude_bps / 100.0
    
    max_tenor = max(curve.keys())
    
    result = {}
    for tenor, yld in curve.items():
        if tenor <= pivot_tenor:
            # Short end: inverse weight (from -1 at t=0 to 0 at pivot)
            weight = -(pivot_tenor - tenor) / pivot_tenor
        else:
            # Long end: positive weight (from 0 at pivot to 1 at max tenor)
            weight = (tenor - pivot_tenor) / (max_tenor - pivot_tenor)
        
        result[tenor] = yld + (weight * shift_pct)
    
    return result


def apply_custom_shock(curve: Dict[float, float], custom_shocks: Dict[float, float]) -> Dict[float, float]:
    """
    Apply custom shocks to specific tenors.
    
    Args:
        curve: {tenor: yield_pct}
        custom_shocks: {tenor: shock_bps}
    
    Returns:
        Shocked curve with specified tenors adjusted
    """
    result = curve.copy()
    for tenor, shock_bps in custom_shocks.items():
        if tenor in result:
            result[tenor] += shock_bps / 100.0
    return result
