#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir("/home/marcelo/Documents/costaricatravel.dev/backend")
os.environ["PYTHONPATH"] = "/home/marcelo/Documents/costaricatravel.dev/backend"

proc = subprocess.Popen([
    sys.executable, "-m", "uvicorn", "app.main:app", 
    "--host", "0.0.0.0", "--port", "8000"
])
proc.wait()
