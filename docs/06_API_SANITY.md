# 06_API_SANITY.md

## API Safety & Sanity Rules

To ensure robustness when fetching from the U.S. Treasury Daily Interest Rate XML Feed, the following rules are enforced.

### 1. Request Safety
- **Fixed Base URL**: We strictly use `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml` to prevent arbitrary URL injection.
- **Timeouts**: All HTTP requests MUST have a timeout (default 10s) to prevent hanging processes.
- **Retries**: Implement a maximum of 2 retries with exponential blackoff for transient network errors.
- **Status Checks**: Explicitly check for `status_code == 200`. Any other status raises a clean, descriptive exception (no raw stack traces to the UI).

### 2. Data Sanity
- **XML Validation**: The response must be valid XML.
- **Content Checks**:
    - Must contain `G_NEW_DATE` and `LIST_G_NEW_DATE` elements.
    - Dates must be parseable.
    - Rates must be convertible to floats.
- **Schema Validation**: We expect specific tenor tags (e.g., `BC_1MONTH`, `BC_10YEAR`). If a response has fewer than 6 valid tenors, it is considered "bad data" and rejected.
- **Blank Handling**: Missing or "N/A" values are skipped, not converted to 0.0 or causing crashes.

### 3. Reliability & Fallback
- **Caching**: Every successful fetch for a specific month is saved to `data/cache/curve_<YYYYMM>.xml` (or parsed CSV).
- **Fallback**:
    - If the live API fails (timeout, 500 error, etc.), attempt to load the most recent matching file from `data/cache`.
    - If no cache exists for the requested period, search backwards for the nearest available cached month (up to 12 months).

### 4. Implementation Constraints
- **Docstrings**: All API functions must specify `Preconditions` in their docstrings.
- **Type Hints**: Full typing required.
