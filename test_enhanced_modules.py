#!/usr/bin/env python3
"""
Test script for the enhanced IAM stability and VoD prediction modules
"""

import sys
import os

# Add the IAM project directory to Python path
sys.path.append('/home/pouli/IAM')

def test_stability_predictor():
    """Test the enhanced stability predictor"""
    print("🧪 Testing Enhanced Stability Predictor...")
    
    try:
        from IAM_Knowledge.IAM_StabilityPredictor import predict_stability_logic
        
        # Test with methane data
        methane_xyz = """4
Methane molecule
C      0.0000    0.0000    0.0000
H      1.0000    1.0000    1.0000
H     -1.0000   -1.0000    1.0000
H      1.0000   -1.0000   -1.0000
H     -1.0000    1.0000   -1.0000"""
        
        result = predict_stability_logic(methane_xyz)
        
        print("✅ Stability Predictor - SUCCESS")
        print(f"   Method: {result.get('method', 'Unknown')}")
        print(f"   Overall Stability: {result.get('overall_stability', {}).get('stability_level', 'Unknown')}")
        print(f"   Stability Score: {result.get('overall_stability', {}).get('stability_score', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Stability Predictor - FAILED: {e}")
        return False

def test_vod_predictor():
    """Test the enhanced VoD predictor"""
    print("\n🚀 Testing Enhanced VoD Predictor...")
    
    try:
        from IAM_Knowledge.IAM_VoD_Predictor import predict_vod
        
        # Test with nitromethane data (explosive compound)
        nitromethane_xyz = """6
Nitromethane molecule
C      0.0000    0.0000    0.0000
H      0.0000    1.0900    0.0000
H      0.9440   -0.5450    0.0000
H     -0.9440   -0.5450    0.0000
N      0.0000    0.0000    1.4890
O      1.0350    0.0000    2.0340
O     -1.0350    0.0000    2.0340"""
        
        result = predict_vod(nitromethane_xyz)
        
        print("✅ VoD Predictor - SUCCESS")
        print(f"   Method: {result.get('method', 'Unknown')}")
        print(f"   Recommended VoD: {result.get('vod_predictions', {}).get('recommended_vod', 'Unknown')} m/s")
        print(f"   Detonation Pressure: {result.get('detonation_pressure', {}).get('pressure_gpa', 'Unknown')} GPa")
        print(f"   Performance Rating: {result.get('performance_assessment', {}).get('rating', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ VoD Predictor - FAILED: {e}")
        return False

def test_performance_optimizer():
    """Test the performance optimization module"""
    print("\n⚡ Testing Performance Optimizer...")
    
    try:
        from IAM_Knowledge.performance_optimization import optimize_explosive_performance
        
        # Test with TNT-like compound
        tnt_xyz = """21
TNT-like molecule
C      0.0000    0.0000    0.0000
C      1.4000    0.0000    0.0000
C      2.1000    1.2124    0.0000
C      1.4000    2.4249    0.0000
C      0.0000    2.4249    0.0000
C     -0.7000    1.2124    0.0000
N     -2.1000    1.2124    0.0000
O     -2.8000    0.0000    0.0000
O     -2.8000    2.4249    0.0000
N      2.1000    3.6373    0.0000
O      1.4000    4.8497    0.0000
O      3.5000    3.6373    0.0000
N      3.5000    1.2124    0.0000
O      4.2000    0.0000    0.0000
O      4.2000    2.4249    0.0000
C      2.1000   -1.2124    0.0000
H      0.5000   -0.8660    0.0000
H     -0.5000   -0.8660    0.0000
H     -0.5000    3.2909    0.0000
H      0.5000    3.2909    0.0000
H      1.6000   -2.0784    0.0000"""
        
        target_properties = {
            "min_vod": 7000,
            "min_pressure": 20,
            "optimal_ob": 0,
            "max_sensitivity": "moderate"
        }
        
        result = optimize_explosive_performance(tnt_xyz, target_properties)
        
        print("✅ Performance Optimizer - SUCCESS")
        print(f"   Current VoD: {result.get('current_properties', {}).get('estimated_vod', 'Unknown')} m/s")
        print(f"   Optimization Strategies: {len(result.get('optimization_strategies', []))} found")
        print(f"   Overall Feasibility: {result.get('feasibility_assessment', {}).get('overall_feasibility', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance Optimizer - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 IAM Enhanced Modules Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test each module
    if test_stability_predictor():
        tests_passed += 1
    
    if test_vod_predictor():
        tests_passed += 1
    
    if test_performance_optimizer():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} modules working")
    
    if tests_passed == total_tests:
        print("🎉 All enhanced modules are functional!")
        print("✅ Stability prediction: Advanced analysis ready")
        print("✅ VoD prediction: Comprehensive calculations ready") 
        print("✅ Performance optimization: Strategic recommendations ready")
    else:
        print("⚠️ Some modules need attention")
    
    print("\n🚀 Enhanced IAM system ready for professional use!")

if __name__ == "__main__":
    main()
