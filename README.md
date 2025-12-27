# Rates Change Simulation
#    git clone https://github.com/zamboza1/rates-change-simulation.git

[![React](https://img.shields.io/badge/Frontend-React%20%7C%20Tailwind-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)

## The Project

I built this rate change simulator to better understand **Yield Curve Risk** through interactive simulation. 

This project connects directly to the **US Treasury** feed to get live data, then lets you apply stress tests such as parallel shifts, and bear steepeners while instantly observing the results.

## How It Works

The full-stack system involves:

*   **Logic (Backend)**: Python **FastAPI** handling the  math. It parses the Treasury's XML feed, handles caching (so it works even if the government site blinks), and calculates **DV01** & **Modified Duration**.
*   **Visuals (Frontend)**: **React** + **Tailwind CSS**. **Chart.js** for smooth, lag-free rendering of the term structure.

## Engineering Standards

Creating this utilized:
*   **Testing**: Comprehensive `pytest` suite covering edge cases (negative rates, empty feeds) and network failures.
*   **Architecture**: Decoupled frontend/backend to allow independent scaling.
*   **Type Safety**: Full Python type hinting to keep the logic strict.

## Run It Yourself

### 1. Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Backend (Terminal 1)
```bash
uvicorn backend.main:app --reload
```

### 3. Start Frontend (Terminal 2)
```bash
python3 -m http.server 3000 --directory frontend
```
Then search `http://localhost:3000`.

License: MIT.
