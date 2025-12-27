from src.data_loader import get_curve
import sys

def main():
    print("Fetching curve...")
    try:
        date_str, curve = get_curve()
        print(f"SUCCESS! Fetched curve for: {date_str}")
        print(f"Tenors found: {len(curve)}")
        print("Sample rates:", list(curve.items())[:3])
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
