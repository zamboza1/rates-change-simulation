import sys
import os
import subprocess

def run_step(name, command):
    print(f"🔹 [CHECK] {name}...", end=" ")
    try:
        if isinstance(command, str):
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        elif callable(command):
            command()
        print("✅ PASS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAIL")
        return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

def check_structure():
    required = [
        "backend/main.py",
        "frontend/index.html",
        "requirements.txt"
    ]
    for r in required:
        if not os.path.exists(r):
            raise FileNotFoundError(f"Missing {r}")

def check_connection():
    # Sanity check internet
    cmd = "curl -I -s -o /dev/null -w '%{http_code}' https://home.treasury.gov/"
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)
        if res.stdout.strip() != "200":
            print(f"(Warning: HTTP {res.stdout.strip()})", end="")
    except:
        raise ConnectionError("No Internet")

def main():
    print("🛡️  RATES PLAYGROUND SAFETY NET (FastAPI Nodeless Edition) 🛡️")
    print("===========================================================")
    
    steps = [
        ("Architecture Check", check_structure),
        ("Backend Unit Tests", "python3 -m pytest backend/tests -q"),
        ("Treasury Ping", check_connection),
    ]
    
    all_passed = True
    for name, task in steps:
        if not run_step(name, task):
            all_passed = False
    
    print("===========================================================")
    if all_passed:
        print("🚀 SYSTEM HEALTHY. READY TO SHIP. 🚀")
        sys.exit(0)
    else:
        print("🛑 CHECKS FAILED. DO NOT DEPLOY. 🛑")
        sys.exit(1)

if __name__ == "__main__":
    main()
