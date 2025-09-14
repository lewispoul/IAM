#!/usr/bin/env python3

import requests
import json

# Test with benzene INDIGO format
mol_content = """  -INDIGO-07162507472D

  6  6  0  0  0  0  0  0  0  0999 V2000
    1.7848   -3.1751    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    3.5152   -3.1746    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    4.3802   -4.6746    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.8802   -4.6741    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7452   -3.1741    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7457   -1.6741    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  1  1  0  0  0  0
M  END"""

print("Starting Flask server test...")

# Start server
import subprocess
import time
import os

# Kill any existing Flask processes
subprocess.run(["pkill", "-f", "backend.py"], capture_output=True)
time.sleep(2)

# Start Flask server in background
env = os.environ.copy()
process = subprocess.Popen(
    ["python", "IAM_GUI/backend.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env
)

# Wait for server to start
time.sleep(5)

try:
    # Test MOL conversion
    print("Testing INDIGO MOL conversion...")
    data = {'mol_content': mol_content}
    response = requests.post('http://localhost:5000/molfile_to_xyz', 
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps(data),
                            timeout=10)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ SUCCESS! MOL conversion worked!")
            print("XYZ output (first 200 chars):")
            print(result.get('xyz', '')[:200] + "...")
        else:
            print("❌ CONVERSION FAILED:")
            print(result.get('error', 'Unknown error'))
    else:
        print("❌ SERVER ERROR:")
        print(response.text[:300])

except Exception as e:
    print(f"❌ REQUEST FAILED: {e}")

finally:
    # Clean up
    process.terminate()
    time.sleep(1)
    subprocess.run(["pkill", "-f", "backend.py"], capture_output=True)
