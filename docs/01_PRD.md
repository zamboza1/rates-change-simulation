# 01_PRD.md

## Product Requirements Document: Rates Playground

### Overview
A Python-based playground for analyzing and shocking U.S. Treasury yield curves.

### Data Source
- **Primary**: U.S. Treasury Daily Interest Rate XML Feed.
- **Format**: XML.
- **Frequency**: Daily updates.
- **Strategy**: 
    - Pull by month/year.
    - Cache results locally in `data/cache`.
    - Fallback to cache if API is unavailable.

### Core Features
1. **Data Loading**: Fetch live rates, parse XML, return standardized `Curve` object.
2. **Analysis**: Calculate risk metrics.
3. **Visualization**: Plot yield curves (CLI or simple UI).
4. **Shocks**: Apply scenarios (parallel shift, tilt) to curves.

### Technical Constraints
- **Language**: Python 3.9+
- **Style**: CSC148 standards (Type hints, Docstrings + Preconditions, simple `assert` tests).
- **Security**: No hardcoded secrets, safe path handling, validated inputs.
