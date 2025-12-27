from __future__ import annotations
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Tuple, Optional

# Constants for the Treasury API
BASE_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
NS = {'d': 'http://schemas.microsoft.com/ado/2007/08/dataservices', 
      'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
      'atom': 'http://www.w3.org/2005/Atom'}

def build_month_url(year: int, month: int) -> str:
    """
    Construct the URL for fetching Treasury yield curve data for a specific month.

    Preconditions:
    - 1990 <= year <= current year + 1
    - 1 <= month <= 12
    """
    assert isinstance(year, int) and 1990 <= year <= 2100, f"Invalid year: {year}"
    assert isinstance(month, int) and 1 <= month <= 12, f"Invalid month: {month}"
    
    month_str = f"{year}{month:02d}"
    return f"{BASE_URL}?data=daily_treasury_yield_curve&field_tdr_date_value_month={month_str}"

def fetch_xml(url: str, timeout_sec: int = 10) -> str:
    """
    Fetch XML content from the given URL with comprehensive error handling.

    Preconditions:
    - url is a valid string starting with 'https://'
    - timeout_sec > 0
    """
    assert url.startswith("https://"), "URL must be secure (https)"
    assert timeout_sec > 0, "Timeout must be positive"

    try:
        response = requests.get(url, timeout=timeout_sec)
        response.raise_for_status() # Check for 200 OK
        return response.text
    except requests.exceptions.RequestException as e:
        # Wrap all network errors in a clean message
        raise ConnectionError(f"Failed to fetch Treasury data: {str(e)}")

def parse_latest_curve(xml_text: str) -> Tuple[str, Dict[float, float]]:
    """
    Parse the XML text to extract the most recent yield curve.
    
    Returns a tuple containing:
    - Date string in 'YYYY-MM-DD' format
    - Dictionary mapping tenor (years) to rate (percent)

    Raises:
    - ValueError if XML is malformed or contains no valid entries.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        raise ValueError("Invalid XML received")

    # Find all 'entry' elements (ATOM feed structure)
    entries = root.findall('atom:entry', NS)
    if not entries:
        raise ValueError("No entries found in XML")

    # Sort entries by date (descending) to get the latest
    # The date is inside content/m:properties/d:NEW_DATE
    latest_entry = None
    latest_date_str = ""
    
    # We loop through all to find the max date. 
    # (The feed is usually sorted, but we verify.)
    for entry in entries:
        content = entry.find('atom:content', NS)
        if content is None: 
            continue
        props = content.find('m:properties', NS)
        if props is None:
            continue
            
        date_elem = props.find('d:NEW_DATE', NS)
        if date_elem is not None and date_elem.text:
            # Format usually: 2025-01-02T00:00:00
            if date_elem.text > latest_date_str:
                latest_date_str = date_elem.text
                latest_entry = props

    if latest_entry is None or not latest_date_str:
        raise ValueError("No valid date found in XML entries")

    # Extract rates from the latest entry
    rates = _extract_rates(latest_entry)
    
    # Sanity check: verify we have a reasonable number of points
    if len(rates) < 6:
        raise ValueError(f"Insufficient data points in curve: {len(rates)} found")

    # Clean up date format (take YYYY-MM-DD part)
    clean_date = latest_date_str.split('T')[0]
    
    return clean_date, rates

def _extract_rates(properties_elem: ET.Element) -> Dict[float, float]:
    """
    Helper to extract and normalize tenor rates from a properties element.
    
    Mapping tags like 'BC_1MONTH' to 0.0833 years.
    Ignores missing or non-numeric values.
    """
    # Map XML tags to tenor in years
    # Note: Tags might be 'BC_1MONTH', 'BC_2MONTH', 'BC_30YEAR' etc.
    # We'll explicitly look for known tags to be safe.
    tag_map = {
        'd:BC_1MONTH': 1/12,
        'd:BC_2MONTH': 2/12,  # sometimes present
        'd:BC_3MONTH': 0.25,
        'd:BC_4MONTH': 4/12,  # sometimes present
        'd:BC_6MONTH': 0.5,
        'd:BC_1YEAR': 1.0,
        'd:BC_2YEAR': 2.0,
        'd:BC_3YEAR': 3.0,
        'd:BC_5YEAR': 5.0,
        'd:BC_7YEAR': 7.0,
        'd:BC_10YEAR': 10.0,
        'd:BC_20YEAR': 20.0,
        'd:BC_30YEAR': 30.0
    }
    
    rates = {}
    for tag, tenor in tag_map.items():
        elem = properties_elem.find(tag, NS)
        if elem is not None and elem.text:
            try:
                # Value is percentage (e.g., '4.35')
                val = float(elem.text)
                rates[tenor] = val
            except ValueError:
                continue # Skip non-numeric garbage
                
    return rates
