# US Treasury Rates Change Simulator
#    git clone https://github.com/zamboza1/us-treasury-rates-change-simulator.git

[![React](https://img.shields.io/badge/Frontend-React%20%7C%20Tailwind-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)

## The Project

I built this rate change simulator to better understand Yield Curve Risk through interactive simulation. 

This project connects directly to the US Treasury feed to get live data, then lets you apply stress tests such as parallel shifts, curve steepeners, and custom point shocks while instantly observing the results on the yield curve.

## How It Works

The full-stack system involves:

*   **Logic (Backend)**: Python FastAPI handling the math. It parses the Treasury's XML feed, handles caching, and calculates DV01 & Modified Duration.
*   **Visuals (Frontend)**: React + Tailwind CSS. Chart.js for rendering the yield curve.

## Engineering Standards

Creating this utilized:
*   **Testing**: Comprehensive `pytest` suite covering edge cases (negative rates, empty feeds) and network failures.
*   **Architecture**: Separated frontend/backend to allow independent scaling.

## Run It Yourself

To launch both the backend and frontend automatically:

```bash
./start.sh
```

Then access the app at: **http://localhost:3001**

Alternatively, run them separately:
1. `pip install -r requirements.txt`
2. `uvicorn backend.main:app --reload --port 8081`
3. `python3 -m http.server 3001 --directory frontend`

License: MIT.
