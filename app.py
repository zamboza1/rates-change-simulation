import sys
from typing import Optional

from src.data_loader import get_curve
from src.shocks import apply_parallel_shock, apply_steepener
from src.risk import calculate_dv01, calculate_duration
from src.plots import plot_comparison

def print_menu():
    print("\n--- Rates Playground ---")
    print("[1] View Rates")
    print("[2] Apply Shock")
    print("[3] Calculate Risk")
    print("[4] Plot Comparison")
    print("[0] Exit")

def print_curve_table(curve: dict[float, float], title: str = "Curve"):
    print(f"\n--- {title} ---")
    print(f"{'Tenor':<10} | {'Rate (%)':<10}")
    print("-" * 25)
    for t in sorted(curve.keys()):
        print(f"{t:<10.2f} | {curve[t]:<10.2f}")

def main():
    print("Initializing Rates Playground...")
    try:
        current_date, original_curve = get_curve()
        print(f"Loaded data as of: {current_date}")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load data. {e}")
        return

    # State
    shocked_curve = None
    
    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        
        if choice == '0':
            print("Exiting...")
            break
            
        elif choice == '1':
            print_curve_table(original_curve, "Original Curve")
            if shocked_curve:
                print_curve_table(shocked_curve, "Shocked Curve")
                
        elif choice == '2':
            print("\n--- Shocks ---")
            print("[1] Parallel Shift (+/- bps)")
            print("[2] Steepener (Pivot 2Y)")
            sc = input("Select shock type: ").strip()
            
            if sc == '1':
                try:
                    val = float(input("Enter bps shift (e.g. 50, -25): "))
                    shocked_curve = apply_parallel_shock(original_curve, val)
                    print(f"Applied {val} bps parallel shift.")
                except ValueError:
                    print("Invalid input.")
            elif sc == '2':
                try:
                    val = float(input("Enter long-end shock bps (e.g. 100): "))
                    shocked_curve = apply_steepener(original_curve, long_end_bps=val, pivot_tenor=2.0)
                    print(f"Applied steepener with {val} bps on long end.")
                except ValueError:
                    print("Invalid input.")
            else:
                print("Unknown shock.")

        elif choice == '3':
            print("\n--- Risk Metrics (Original) ---")
            # Just show some key tenors
            print(f"{'Tenor':<10} | {'ModDur':<10} | {'DV01 ($)':<10}")
            print("-" * 36)
            for t in [2.0, 5.0, 10.0, 30.0]:
                if t in original_curve:
                    r = original_curve[t]
                    dur = calculate_duration(r, t)
                    dv01 = calculate_dv01(r, t)
                    print(f"{t:<10.1f} | {dur:<10.2f} | {dv01:<10.4f}")
                    
        elif choice == '4':
            print("Generating plot...")
            if shocked_curve:
                plot_comparison(original_curve, shocked_curve, title=f"Comparison: {current_date}")
            else:
                plot_comparison(original_curve, title=f"Original: {current_date}")
            print("Plot displayed (check window).")
            
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
