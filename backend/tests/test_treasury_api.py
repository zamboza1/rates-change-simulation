import pytest
from src.treasury_api import build_month_url, parse_latest_curve, fetch_xml
from unittest.mock import patch, MagicMock
import requests

# Sample XML snippet for testing (minimized)
SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" 
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" 
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <entry>
    <content type="application/xml">
      <m:properties>
        <d:NEW_DATE>2025-01-15T00:00:00</d:NEW_DATE>
        <d:BC_1MONTH>4.50</d:BC_1MONTH>
        <d:BC_3MONTH>4.60</d:BC_3MONTH>
        <d:BC_1YEAR>4.20</d:BC_1YEAR>
        <d:BC_2YEAR>4.00</d:BC_2YEAR>
        <d:BC_5YEAR>3.90</d:BC_5YEAR>
        <d:BC_10YEAR>3.80</d:BC_10YEAR>
        <d:BC_30YEAR>4.10</d:BC_30YEAR>
      </m:properties>
    </content>
  </entry>
</feed>
"""

def test_build_month_url_valid():
    """Test URL construction for valid inputs."""
    url = build_month_url(2025, 1)
    expected = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202501"
    assert url == expected

def test_build_month_url_invalid():
    """Test that invalid inputs raise AssertErrors."""
    with pytest.raises(AssertionError):
        build_month_url(1800, 1) # Too old
    with pytest.raises(AssertionError):
        build_month_url(2023, 13) # Bad month

def test_parse_latest_curve_success():
    """Test parsing a valid XML snippet."""
    date_str, curve = parse_latest_curve(SAMPLE_XML)
    
    assert date_str == "2025-01-15"
    assert len(curve) >= 6
    assert curve[0.25] == 4.60 # 3 Month
    assert curve[10.0] == 3.80 # 10 Year

def test_parse_latest_curve_malformed():
    """Test parsing invalid XML."""
    with pytest.raises(ValueError):
        parse_latest_curve("<not>xml</not>")

def test_parse_latest_curve_missing_data():
    """Test parsing XML with insufficient data points."""
    bad_xml = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" 
          xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" 
          xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
      <entry>
        <content type="application/xml">
          <m:properties>
            <d:NEW_DATE>2025-01-10T00:00:00</d:NEW_DATE>
            <d:BC_1MONTH>4.50</d:BC_1MONTH>
          </m:properties>
        </content>
      </entry>
    </feed>
    """
    with pytest.raises(ValueError, match="Insufficient data points"):
        parse_latest_curve(bad_xml)

@patch('requests.get')
def test_fetch_xml_success(mock_get):
    """Test successful API fetch."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "Success"
    mock_get.return_value = mock_resp

    result = fetch_xml("https://example.com")
    assert result == "Success"

@patch('requests.get')
def test_fetch_xml_failure(mock_get):
    """Test API failure handling."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
    mock_get.return_value = mock_resp

    with pytest.raises(ConnectionError):
        fetch_xml("https://example.com")
