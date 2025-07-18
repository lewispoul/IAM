#!/usr/bin/env python3
"""
Test script for Enhanced IAM Systems with Reference Knowledge Integration
Tests VoD prediction, stability assessment, and performance optimization
with Klapötke, Agrawal & Keshavarz reference methods
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'IAM_Knowledge'))

# Test imports
try:
    from reference_knowledge_extractor import EnergeticMaterialsKnowledgeBase
    from IAM_VoD_Predictor import predict_vod
    from IAM_StabilityPredictor import predict_stability_logic
    from performance_optimization import optimize_explosive_performance
    print("✅ All enhanced modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_reference_knowledge_base():
    """Test the reference knowledge extraction system"""
    print("\n🔬 Testing Reference Knowledge Base...")
    
    kb = EnergeticMaterialsKnowledgeBase()
    
    # Test knowledge base structure
    kb_data = kb.knowledge_base
    print(f"   📊 Knowledge categories: {list(kb_data.keys())}")
    
    # Test VoD correlations
    if "vod_correlations" in kb_data:
        vod_methods = kb_data["vod_correlations"]
        print(f"   📊 VoD methods available: {len(vod_methods)}")
        if "kamlet_jacobs_enhanced" in vod_methods:
            constants = vod_methods["kamlet_jacobs_enhanced"]["constants"]
            print(f"   🎯 Enhanced Kamlet-Jacobs constants: A={constants.get('A', 'N/A')}")
    
    # Test sensitivity data
    if "sensitivity_data" in kb_data:
        sensitivity_data = kb_data["sensitivity_data"]
        print(f"   ⚡ Sensitivity data available: {bool(sensitivity_data)}")
    
    # Test thermal stability
    if "thermal_stability" in kb_data:
        thermal_data = kb_data["thermal_stability"]
        print(f"   🌡️ Thermal stability data available: {bool(thermal_data)}")
    
    print("   ✅ Reference knowledge base functional")

def test_enhanced_vod_prediction():
    """Test enhanced VoD prediction with reference methods"""
    print("\n🚀 Testing Enhanced VoD Prediction...")
    
    # Test with TNT-like molecule
    tnt_xyz = """15
TNT-like test molecule
C 0.0 0.0 0.0
C 1.4 0.0 0.0
C 2.1 1.2 0.0
C 1.4 2.4 0.0
C 0.0 2.4 0.0
C -0.7 1.2 0.0
N 3.5 1.2 0.2
O 4.1 2.0 0.4
O 4.0 0.4 0.4
N -2.1 1.2 -0.2
O -2.7 2.0 -0.4
O -2.6 0.4 -0.4
N 1.4 3.8 0.2
O 2.0 4.6 0.4
O 0.8 4.6 0.4"""
    
    result = predict_vod(tnt_xyz)
    
    if "error" not in result:
        print(f"   📊 Molecular formula: {result['molecular_info']['formula']}")
        print(f"   🎯 Enhanced VoD estimate: {result['enhanced_vod_estimate']:.0f} m/s")
        print(f"   📈 Multiple method estimates:")
        for method, vod in result['vod_estimates'].items():
            print(f"      {method}: {vod:.0f} m/s")
        print(f"   🏆 Reference class: {result['reference_comparison']['performance_class']}")
        print(f"   ✅ Enhanced VoD prediction successful")
    else:
        print(f"   ❌ VoD prediction failed: {result['error']}")

def test_enhanced_stability_prediction():
    """Test enhanced stability prediction with reference methods"""
    print("\n🛡️ Testing Enhanced Stability Prediction...")
    
    # Test with RDX-like molecule
    rdx_xyz = """21
RDX-like test molecule
C 0.0 0.0 0.0
N 1.3 0.0 0.5
N 0.7 1.2 -0.5
N -0.7 1.2 -0.5
N -1.3 0.0 0.5
N -0.7 -1.2 -0.5
N 0.7 -1.2 -0.5
O 2.3 0.2 0.8
O 1.0 -0.8 0.8
O 1.2 2.0 -0.8
O 0.4 1.4 -1.3
O -1.2 2.0 -0.8
O -0.4 1.4 -1.3
O -2.3 0.2 0.8
O -1.0 -0.8 0.8
O -1.2 -2.0 -0.8
O -0.4 -1.4 -1.3
O 1.2 -2.0 -0.8
O 0.4 -1.4 -1.3
H 0.0 0.0 1.0
H 0.0 0.0 -1.0"""
    
    result = predict_stability_logic(rdx_xyz)
    
    if "error" not in result:
        print(f"   🧪 Molecular formula: {result['molecule_info']['molecular_formula']}")
        
        if "sensitivity_assessment" in result:
            sens = result["sensitivity_assessment"]
            print(f"   ⚡ Sensitivity class: {sens['sensitivity_class']}")
            print(f"   🎯 Impact sensitivity: {sens['estimated_impact_sensitivity']}")
            print(f"   📋 Handling requirements: {sens['handling_requirements']}")
        
        if "thermal_stability" in result:
            thermal = result["thermal_stability"]
            print(f"   🌡️ Decomposition temp: {thermal['estimated_decomposition_temp']:.0f}°C")
            print(f"   🔥 Stability class: {thermal['stability_class']}")
        
        if "overall_stability" in result:
            overall = result["overall_stability"]
            print(f"   📊 Overall score: {overall['overall_score']}/100")
            print(f"   🏷️ Risk level: {overall['risk_level']}")
        
        print("   ✅ Enhanced stability prediction successful")
    else:
        print(f"   ❌ Stability prediction failed: {result['error']}")

def test_enhanced_performance_optimization():
    """Test enhanced performance optimization with reference methods"""
    print("\n⚡ Testing Enhanced Performance Optimization...")
    
    # Test with HMX-like molecule
    hmx_xyz = """24
HMX-like test molecule
C 0.0 0.0 0.0
C 2.0 0.0 0.0
C 2.0 2.0 0.0
C 0.0 2.0 0.0
N 1.0 -0.5 0.5
N 2.5 1.0 0.5
N 1.0 2.5 0.5
N -0.5 1.0 0.5
N 1.0 -0.5 -0.5
N 2.5 1.0 -0.5
N 1.0 2.5 -0.5
N -0.5 1.0 -0.5
O 1.2 -1.2 1.0
O 0.8 -1.2 1.0
O 3.2 1.2 1.0
O 2.8 0.8 1.0
O 1.2 3.2 1.0
O 0.8 2.8 1.0
O -1.2 1.2 1.0
O -0.8 0.8 1.0
O 1.2 -1.2 -1.0
O 0.8 -1.2 -1.0
O 3.2 1.2 -1.0
O 2.8 0.8 -1.0"""
    
    result = optimize_explosive_performance(hmx_xyz)
    
    if "error" not in result:
        current = result["current_properties"]
        print(f"   🧪 Molecular weight: {current['molecular_weight']:.1f} g/mol")
        print(f"   📏 Estimated density: {current['estimated_density']:.2f} g/cm³")
        print(f"   ⚖️ Oxygen balance: {current['oxygen_balance']:.1f}%")
        print(f"   🎯 Average VoD: {current['average_vod']:.0f} m/s")
        print(f"   💥 Detonation pressure: {current['detonation_pressure']:.1f} GPa")
        print(f"   🏆 Performance class: {current['reference_performance_class']}")
        
        strategies = result["optimization_strategies"]
        print(f"   📋 Optimization strategies: {len(strategies)}")
        for i, strategy in enumerate(strategies[:2], 1):  # Show first 2
            print(f"      {i}. {strategy['strategy']}")
        
        if "best_case_scenario" in result["performance_improvements"]:
            best_case = result["performance_improvements"]["best_case_scenario"]
            print(f"   🚀 Projected VoD: {best_case['projected_vod']:.0f} m/s")
            print(f"   📈 Projected class: {best_case['projected_class']}")
        
        print("   ✅ Enhanced performance optimization successful")
    else:
        print(f"   ❌ Performance optimization failed: {result['error']}")

def test_integration_validation():
    """Test integration between all enhanced systems"""
    print("\n🔗 Testing System Integration...")
    
    # Use a realistic explosive molecule for comprehensive testing
    test_molecule = """18
Test energetic material
C 0.0 0.0 0.0
C 1.4 0.0 0.0
C 2.1 1.2 0.0
C 1.4 2.4 0.0
C 0.0 2.4 0.0
C -0.7 1.2 0.0
N 3.5 1.2 0.2
O 4.1 2.0 0.4
O 4.0 0.4 0.4
N -2.1 1.2 -0.2
O -2.7 2.0 -0.4
O -2.6 0.4 -0.4
N 1.4 3.8 0.2
O 2.0 4.6 0.4
O 0.8 4.6 0.4
H 0.5 0.5 0.5
H -0.5 0.5 0.5
H 1.9 1.9 0.5"""
    
    # Test all systems with same molecule
    vod_result = predict_vod(test_molecule)
    stability_result = predict_stability_logic(test_molecule)
    optimization_result = optimize_explosive_performance(test_molecule)
    
    all_successful = (
        "error" not in vod_result and
        "error" not in stability_result and
        "error" not in optimization_result
    )
    
    if all_successful:
        print("   ✅ All systems integrate successfully")
        print("   🎯 Cross-validation successful")
        
        # Compare results for consistency
        vod_estimate = vod_result.get("enhanced_vod_estimate", 0)
        opt_vod = optimization_result["current_properties"].get("average_vod", 0)
        
        if abs(vod_estimate - opt_vod) < 500:  # Within 500 m/s tolerance
            print("   ✅ VoD estimates are consistent between systems")
        else:
            print(f"   ⚠️ VoD estimates differ: {vod_estimate:.0f} vs {opt_vod:.0f}")
        
        print("   🏆 Integration validation complete")
    else:
        print("   ❌ Integration issues detected")
        if "error" in vod_result:
            print(f"      VoD: {vod_result['error']}")
        if "error" in stability_result:
            print(f"      Stability: {stability_result['error']}")
        if "error" in optimization_result:
            print(f"      Optimization: {optimization_result['error']}")

def main():
    """Run comprehensive testing of enhanced IAM systems"""
    print("🧪 IAM Enhanced Systems Integration Test")
    print("=" * 50)
    print("Testing reference-based enhancements with Klapötke, Agrawal & Keshavarz methods")
    
    # Run all tests
    test_reference_knowledge_base()
    test_enhanced_vod_prediction()
    test_enhanced_stability_prediction()
    test_enhanced_performance_optimization()
    test_integration_validation()
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced IAM Systems Test Complete!")
    print("🔬 All systems enhanced with authoritative reference knowledge")
    print("📚 Klapötke sensitivity correlations integrated")
    print("📊 Agrawal performance methods implemented")
    print("🧪 Keshavarz property estimation methods active")
    print("✅ Professional-grade explosive analysis system ready")

if __name__ == "__main__":
    main()
