import sys
import os

# Appending backend/src to path so tests can import 'src.shocks' etc.
# Current file: backend/tests/conftest.py
# Target: backend/src
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_CURRENT_DIR, "..") 
sys.path.append(_SRC_DIR)
