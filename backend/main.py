from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import sys
import os

# Add local src to path if needed (though uvicorn usually handles package imports relative to run dir)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import get_curve
from src.shocks import apply_parallel_shock, apply_steepener, apply_custom_shock
from src.risk import calculate_dv01, calculate_duration

app = FastAPI(title="Rates Change Simulation API")

# Allow CORS for local dev (Frontend static file -> API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class ShockRequest(BaseModel):
    type: str # 'parallel', 'steepener', 'custom'
    magnitude: float = 0.0 # bps
    pivot: float = 2.0 # for steepener (tenor)
    custom_shocks: Dict[float, float] = {} # {tenor: bps}

class AnalysisResponse(BaseModel):
    date: str
    original_curve: Dict[float, float]
    shocked_curve: Dict[float, float]
    metrics: Dict[str, Dict[str, float]] # {tenor: {dv01: x, duration: y}}

# --- Endpoints ---

@app.get("/api/market/latest")
def get_latest_data():
    try:
        date_str, curve = get_curve()
        return {
            "date": date_str,
            "curve": curve
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
def analyze_scenario(req: ShockRequest):
    try:
        # 1. Get Base Data
        date_str, original = get_curve()
        
        # 2. Apply Shock
        shocked = original.copy()
        
        if req.type == 'parallel':
            shocked = apply_parallel_shock(original, req.magnitude)
        elif req.type == 'steepener':
            shocked = apply_steepener(original, req.magnitude, pivot_tenor=req.pivot)
        elif req.type == 'custom':
            # Convert string keys to float if JSON passed string keys
            safe_shocks = {float(k): v for k, v in req.custom_shocks.items()}
            shocked = apply_custom_shock(original, safe_shocks)
            
        # 3. Calculate Risk Metrics (Delta, DV01, Duration)
        # We focus on key tenors: 2, 5, 10, 30
        key_tenors = [2.0, 5.0, 10.0, 30.0]
        metrics = {}
        
        for t in key_tenors:
            if t in shocked:
                rate = shocked[t]
                metrics[str(t)] = {
                    "yield": rate,
                    "delta_bps": (rate - original.get(t, rate)) * 100,
                    "dv01": calculate_dv01(rate, t),
                    "duration": calculate_duration(rate, t)
                }
                
        return AnalysisResponse(
            date=date_str,
            original_curve=original,
            shocked_curve=shocked,
            metrics=metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "rates-playground-backend"}
