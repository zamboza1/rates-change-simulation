from __future__ import annotations
import matplotlib.pyplot as plt
from typing import Dict, Optional

# Type alias
Curve = Dict[float, float]

def plot_comparison(original: Curve, 
                    shocked: Optional[Curve] = None, 
                    title: str = "Yield Curve Analysis", 
                    filename: Optional[str] = None) -> None:
    """
    Plot the original yield curve and optionally a shocked curve for comparison.
    
    Preconditions:
    - original curve is not empty.
    - If filename is provided, it must be a valid path/string ending in .png/.jpg etc.
    """
    assert original, "Original curve cannot be empty"
    
    # Prepare data
    tenors = sorted(original.keys())
    rates = [original[t] for t in tenors]
    
    plt.figure(figsize=(10, 6))
    
    # Plot Original
    plt.plot(tenors, rates, marker='o', linestyle='-', linewidth=2, label='Original')
    
    # Plot Shocked if exists
    if shocked:
        # User implies we should handle mismatch tenors? 
        # For playground, assume same tenors or just plot what's there.
        s_tenors = sorted(shocked.keys())
        s_rates = [shocked[t] for t in s_tenors]
        plt.plot(s_tenors, s_rates, marker='x', linestyle='--', linewidth=2, color='r', label='Shocked')
        
    plt.title(title)
    plt.xlabel("Tenor (Years)")
    plt.ylabel("Rate (%)")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    if filename:
        plt.savefig(filename)
        plt.close() # Close to free memory/avoid interactive popup if script
    else:
        plt.show() # Interactive mode
