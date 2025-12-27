from __future__ import annotations
import os
import csv
import glob
from datetime import datetime
from typing import Dict, Optional, Tuple
from dateutil.relativedelta import relativedelta # type: ignore

from src.treasury_api import build_month_url, fetch_xml, parse_latest_curve

# Type alias for clarity
Curve = Dict[float, float]
# Resolve cache dir relative to this file: backend/src/data_loader.py -> backend/data/cache
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(_CURRENT_DIR, "..", "data", "cache")

def get_curve(asof: str | None = None) -> tuple[str, Curve]:
    """
    Get the Treasury yield curve, either from the API or local cache.
    
    Strategy:
    1. If specific date provided (NOT IMPLEMENTED fully yet), just return latest for now or todo.
       (Prompt implies 'asof is None' logic mainly).
    2. If asof is None:
       - Try fetching current month.
       - If valid data found: cache it to CSV, return it.
       - If no data/empty (e.g. holiday?): try previous month (up to 12 times).
       - If API network fails: Fallback to reading most recent cache file.
    
    Returns:
        (date_str, {tenor: rate})
        date_str format: 'YYYY-MM-DD'
    """
    if asof is not None:
        raise NotImplementedError("Specific date fetching not yet implemented. Use asof=None for latest.")

    # Try to fetch fresh data
    try:
        return _fetch_fresh_curve()
    except ConnectionError as e:
        print(f"[WARNING] API unavailable: {e}. Falling back to cache.")
        return _load_from_cache()

def _fetch_fresh_curve() -> tuple[str, Curve]:
    """
    Attempt to fetch the latest available curve by iterating backwards from today.
    """
    current_date = datetime.now()
    attempts = 0
    max_attempts = 12

    while attempts < max_attempts:
        year = current_date.year
        month = current_date.month
        
        url = build_month_url(year, month)
        try:
            xml_text = fetch_xml(url, timeout_sec=10)
            date_str, curve = parse_latest_curve(xml_text)
            
            # If successful, save and return
            _save_to_cache(date_str, curve)
            return date_str, curve
            
        except ValueError:
            # XML parsed but no valid entries? (e.g., start of month with no data yet)
            # Move to previous month
            pass
        except Exception as e:
            # Unexpected error, re-raise to trigger fallback if it's network related
            # But if it's code error? We re-raise to let top-level decide.
            raise e

        # Go back one month
        current_date = current_date - relativedelta(months=1)
        attempts += 1

    raise ConnectionError("Could not find valid data in the last 12 months.")

def _save_to_cache(date_str: str, curve: Curve) -> None:
    """
    Save the curve to a CSV file in data/cache.
    Filename format: curve_YYYY-MM-DD.csv
    
    Preconditions:
    - CACHE_DIR exists
    """
    filename = f"curve_{date_str}.csv"
    filepath = os.path.join(CACHE_DIR, filename)
    
    # Ensure dir exists (redundant if task created it, but safe)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tenor", "rate"])
        for tenor, rate in sorted(curve.items()):
            writer.writerow([tenor, rate])

def _load_from_cache() -> tuple[str, Curve]:
    """
    Load the most recent curve from the local cache.
    
    Raises:
    - FileNotFoundError if cache is empty.
    """
    # Glob for curve_*.csv
    pattern = os.path.join(CACHE_DIR, "curve_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError("No cached data available and API is unreachable.")
    
    # Sort by filename (which includes date, so YYYY-MM-DD works alphabetically)
    latest_file = sorted(files)[-1]
    
    # Extract date from filename: curve_2025-01-01.csv
    basename = os.path.basename(latest_file)
    date_str = basename.replace("curve_", "").replace(".csv", "")
    
    curve = {}
    with open(latest_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            curve[float(row["tenor"])] = float(row["rate"])
            
    return date_str, curve
