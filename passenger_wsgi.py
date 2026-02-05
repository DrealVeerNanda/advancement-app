import sys, os

# This is a standard entry point for PythonAnywhere
INTERP = sys.executable
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

# Add project root to path
sys.path.append(os.getcwd())

# Import the Flask app
# Assuming src/app.py defines 'app'
from src.app import app as application
