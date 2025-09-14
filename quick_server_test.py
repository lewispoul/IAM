#!/usr/bin/env python3
"""
Quick server test and startup
"""

import sys
import os
sys.path.append('/home/pouli/IAM')

print("🧪 Testing Enhanced IAM Server Startup...")

# Test imports
try:
    from IAM_Knowledge.IAM_StabilityPredictor import predict_stability_logic
    print("✅ Stability predictor imported")
except Exception as e:
    print(f"❌ Stability predictor error: {e}")

try:
    from IAM_Knowledge.IAM_VoD_Predictor import predict_vod
    print("✅ VoD predictor imported")
except Exception as e:
    print(f"❌ VoD predictor error: {e}")

try:
    from IAM_Knowledge.performance_optimization import optimize_explosive_performance
    print("✅ Performance optimizer imported")
except Exception as e:
    print(f"❌ Performance optimizer error: {e}")

# Start server
print("\n🚀 Starting Flask server...")
os.chdir('/home/pouli/IAM/IAM_GUI')

try:
    import backend
    print("✅ Server startup initiated")
except Exception as e:
    print(f"❌ Server startup error: {e}")
    import traceback
    traceback.print_exc()
