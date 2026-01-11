"""
US Treasury Rates Change Simulator - FastAPI Backend
Provides REST API for yield curve data and scenario analysis.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from backend.curve import (
    get_curve,
    apply_parallel_shock,
    apply_steepener,
    apply_custom_shock
)
from backend.bond import calculate_duration, calculate_dv01

app = FastAPI(title="US Treasury Rates Change Simulator")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Request model for scenario analysis"""
    type: str  # "parallel", "steepener", or "custom"
    magnitude: float = 0  # Shock magnitude in bps
    pivot: Optional[float] = 2.0  # Pivot tenor for steepener
    custom_shocks: Optional[Dict[float, float]] = None  # {tenor: shock_bps}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "US Treasury Rates Change Simulator",
        "status": "operational",
        "version": "1.0"
    }


@app.post("/api/analyze")
async def analyze_scenario(request: AnalyzeRequest):
    """
    Analyze a yield curve scenario with specified shock.
    
    Returns original curve, shocked curve, and key metrics.
    """
    try:
        # Get base curve
        date, original_curve = get_curve()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Treasury data unavailable: {str(e)}"
        )
    
    # Apply shock based on type
    if request.type == "parallel":
        shocked_curve = apply_parallel_shock(original_curve, request.magnitude)
    elif request.type == "steepener":
        shocked_curve = apply_steepener(
            original_curve,
            request.magnitude,
            pivot_tenor=request.pivot or 2.0
        )
    elif request.type == "custom":
        custom_shocks = request.custom_shocks or {}
        shocked_curve = apply_custom_shock(original_curve, custom_shocks)
    else:
        shocked_curve = original_curve.copy()
    
    # Calculate metrics for key tenors
    metrics = {}
    for tenor in original_curve.keys():
        orig_yield = original_curve[tenor]
        shock_yield = shocked_curve[tenor]
        delta_bps = (shock_yield - orig_yield) * 100
        
        metrics[tenor] = {
            "yield": shock_yield,
            "delta_bps": delta_bps,
            "duration": calculate_duration(shock_yield, tenor),
            "dv01": calculate_dv01(shock_yield, tenor)
        }
    
    return {
        "date": date,
        "original_curve": original_curve,
        "shocked_curve": shocked_curve,
        "metrics": metrics
    }


@app.get("/api/curve")
async def get_current_curve():
    """
    Get the current US Treasury yield curve.
    
    Returns the latest yield curve data with date.
    """
    try:
        date, curve = get_curve()
        return {
            "date": date,
            "curve": curve
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Treasury data unavailable: {str(e)}"
        )
