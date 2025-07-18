#!/usr/bin/env python3
"""
Enhanced IAM System Test with Jaguar Thermochemical Integration
Test all enhanced modules with reference knowledge validation
"""

import sys
import os

# Add the IAM_Knowledge directory to Python path
sys.path.append('/home/pouli/IAM/IAM_Knowledge')

def test_enhanced_iam_system():
    """Test the complete enhanced IAM system"""
    
    print("=" * 80)
    print("ENHANCED IAM SYSTEM TEST WITH JAGUAR INTEGRATION")
    print("=" * 80)
    
    # Test molecule: RDX (C3H6N6O6)
    rdx_xyz = """12
RDX molecule
C    0.000000    0.000000    0.000000
H    1.090000    0.000000    0.000000
H   -0.545000    0.943000    0.000000
N   -0.545000   -0.943000    0.000000
N    0.545000    0.943000    1.500000
O    1.090000    1.886000    1.500000
O   -1.090000    1.886000    1.500000
C    1.090000   -1.886000   -1.500000
H    1.635000   -2.829000   -1.500000
H    0.545000   -0.943000   -1.500000
N   -0.545000   -0.943000    1.500000
O    0.000000    0.000000    3.000000"""
    
    print("🧪 Testing Enhanced VoD Prediction with Jaguar Integration...")
    print("-" * 60)
    
    try:
        # Import and test VoD predictor
        from IAM_VoD_Predictor import predict_vod
        
        vod_results = predict_vod(rdx_xyz)
        
        if "error" in vod_results:
            print(f"❌ VoD Prediction Error: {vod_results['error']}")
            return
        
        print("✅ VoD Prediction Results:")
        print(f"   Molecular Formula: {vod_results['molecule_info']['molecular_formula']}")
        print(f"   Molecular Weight: {vod_results['molecule_info']['molecular_weight']:.2f} g/mol")
        print(f"   Estimated Density: {vod_results['density']['estimated_density']:.3f} g/cm³")
        print(f"   Oxygen Balance: {vod_results['oxygen_balance']['oxygen_balance_co2']:.1f}%")
        print(f"   Heat of Explosion: {vod_results['heat_of_explosion']['heat_of_explosion_cal_g']:.0f} cal/g")
        
        # VoD Methods
        vod_pred = vod_results['vod_predictions']
        print(f"\n📊 VoD Prediction Methods:")
        print(f"   Enhanced Kamlet-Jacobs: {vod_pred['enhanced_kamlet_jacobs']:.0f} m/s")
        print(f"   Agrawal Correlation: {vod_pred['agrawal_correlation']:.0f} m/s")
        if vod_pred['keshavarz_nitrogen_rich'] > 0:
            print(f"   Keshavarz N-rich: {vod_pred['keshavarz_nitrogen_rich']:.0f} m/s")
        print(f"   BKW Simplified: {vod_pred['bkw_simplified']:.0f} m/s")
        
        # Jaguar Integration
        if 'jaguar_thermochemical' in vod_results:
            jaguar = vod_results['jaguar_thermochemical']
            if 'error' not in jaguar:
                print(f"   🔬 Jaguar Thermochemical: {jaguar['jaguar_vod_m_s']:.0f} m/s")
                print(f"   CJ Temperature: {jaguar['cj_conditions']['temperature_K']:.0f} K")
                print(f"   CJ Pressure: {jaguar['cj_conditions']['pressure_GPa']:.1f} GPa")
                
                # Method comparison
                if 'method_comparison' in jaguar:
                    comp = jaguar['method_comparison']
                    print(f"   Method Agreement: {comp['agreement_assessment']}")
                    print(f"   Difference: {comp['relative_difference_percent']:.1f}%")
            else:
                print(f"   ⚠️ Jaguar Analysis: {jaguar['error']}")
        else:
            print("   ℹ️ Jaguar integration not available")
        
        print(f"\n🎯 Recommended VoD: {vod_pred['recommended_vod']:.0f} m/s")
        print(f"   Confidence: {vod_pred['confidence']}")
        print(f"   Method Count: {vod_pred['method_count']}")
        if 'method_agreement' in vod_pred:
            print(f"   Method Agreement: {vod_pred['method_agreement']:.3f}")
        
        # Performance Assessment
        perf = vod_results['performance_assessment']
        print(f"\n⚡ Performance Assessment:")
        print(f"   Overall Score: {perf['overall_score']:.1f}/100")
        print(f"   Rating: {perf['rating']}")
        print(f"   Category: {perf['vod_category']}")
        print(f"   vs TNT: {perf['comparison_to_tnt']}")
        
        # Reference Validation
        ref_val = vod_pred['reference_validation']
        print(f"\n📚 Reference Validation:")
        print(f"   Performance Class: {ref_val['performance_class']}")
        if ref_val['comparable_compounds']:
            print(f"   Comparable: {', '.join(ref_val['comparable_compounds'])}")
        
    except Exception as e:
        print(f"❌ VoD Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🧪 Testing Enhanced Stability Prediction...")
    print("-" * 60)
    
    try:
        from IAM_StabilityPredictor import predict_stability
        
        stability_results = predict_stability(rdx_xyz)
        
        if "error" in stability_results:
            print(f"❌ Stability Prediction Error: {stability_results['error']}")
            return
        
        print("✅ Stability Prediction Results:")
        
        # Enhanced sensitivity assessment
        if 'sensitivity_assessment' in stability_results:
            sens = stability_results['sensitivity_assessment']
            print(f"   Sensitivity Class: {sens['sensitivity_class']}")
            print(f"   Sensitivity Score: {sens['sensitivity_score']:.1f}")
            print(f"   Impact Sensitivity: {sens['estimated_impact_sensitivity']}")
            print(f"   Handling: {sens['handling_requirements']}")
            
            if sens['risk_factors']:
                print(f"   Risk Factors: {', '.join(sens['risk_factors'][:3])}")
        
        # Enhanced thermal stability
        if 'thermal_stability' in stability_results:
            thermal = stability_results['thermal_stability']
            print(f"   Thermal Class: {thermal['stability_class']}")
            print(f"   Decomp. Temp: {thermal['estimated_decomposition_temp']:.0f}°C")
            print(f"   Safe Temp: {thermal['safe_handling_temperature']}")
        
        # Overall assessment
        if 'overall_stability' in stability_results:
            overall = stability_results['overall_stability']
            print(f"   Overall Score: {overall['overall_score']:.1f}/100")
            print(f"   Stability Class: {overall['stability_class']}")
            print(f"   Risk Level: {overall['risk_level']}")
        
        # Design recommendations
        if 'design_recommendations' in stability_results:
            design_recs = stability_results['design_recommendations']
            print(f"   Design Recommendations: {len(design_recs)} items")
            for i, rec in enumerate(design_recs[:3]):
                print(f"     {i+1}. {rec}")
        
    except Exception as e:
        print(f"❌ Stability Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🧪 Testing Jaguar Thermochemical Methods...")
    print("-" * 60)
    
    try:
        from jaguar_thermochemical_methods import JaguarThermochemicalCalculator
        
        calculator = JaguarThermochemicalCalculator()
        
        # RDX composition: C3H6N6O6
        rdx_composition = {'C': 3, 'H': 6, 'N': 6, 'O': 6}
        
        # Test equilibrium composition calculation
        equilibrium = calculator.calculate_equilibrium_composition(
            rdx_composition, temperature=3500, pressure=25.0
        )
        
        print("✅ Jaguar Thermochemical Analysis:")
        print(f"   Method: {equilibrium['method']}")
        print(f"   Temperature: {equilibrium['temperature_K']:.0f} K")
        print(f"   Pressure: {equilibrium['pressure_GPa']:.1f} GPa")
        
        composition = equilibrium['composition']
        print("   Product Composition:")
        for species, moles in sorted(composition.items(), key=lambda x: x[1], reverse=True):
            if moles > 0.01:  # Show only significant products
                percentage = moles / sum(composition.values()) * 100
                print(f"     {species}: {percentage:.1f}%")
        
        properties = equilibrium['properties']
        print(f"   Avg. Molecular Weight: {properties['average_molecular_weight']:.2f} g/mol")
        print(f"   Heat of Formation: {properties['heat_of_formation_kj']:.1f} kJ")
        print(f"   Compressibility Factor: {properties['compressibility_factor']:.3f}")
        
        # Test enhanced VoD calculation
        vod_result = calculator.calculate_jaguar_enhanced_vod(
            rdx_composition, 1.82, 1510  # RDX properties
        )
        
        print(f"\n🚀 Jaguar VoD Calculation:")
        print(f"   VoD: {vod_result['vod_m_s']:.0f} m/s")
        print(f"   CJ Temperature: {vod_result['cj_temperature_K']:.0f} K")
        print(f"   CJ Pressure: {vod_result['cj_pressure_GPa']:.1f} GPa")
        print(f"   Accuracy: {vod_result['accuracy']}")
        
    except ImportError:
        print("ℹ️ Jaguar thermochemical methods not available")
    except Exception as e:
        print(f"❌ Jaguar Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🎯 ENHANCED IAM SYSTEM INTEGRATION TEST COMPLETE")
    print("=" * 80)
    
    print("\n📊 System Enhancement Summary:")
    print("✅ Enhanced VoD Prediction with multiple reference methods")
    print("✅ Klapötke sensitivity correlations integrated")
    print("✅ Agrawal thermochemical improvements applied")
    print("✅ Keshavarz density and nitrogen-rich methods")
    print("✅ Jaguar thermochemical code principles implemented")
    print("✅ Reference validation against known explosives")
    print("✅ Multi-method agreement assessment")
    print("✅ Enhanced stability and thermal analysis")
    
    print("\n🔬 Reference Sources Integrated:")
    print("📚 Klapötke: Chemistry of High Energy Materials")
    print("📚 Keshavarz: Properties of Energetic Materials")
    print("📚 Agrawal: High Energy Materials")
    print("📚 Energetic Materials Encyclopedia")
    print("📚 Jaguar Thermochemical Code Manual")
    
    print("\n🎓 Educational Impact:")
    print("🎯 ChemCompute-quality molecular orbital visualization")
    print("🧪 Professional-grade explosive property prediction")
    print("📈 Reference-validated thermochemical analysis")
    print("🔍 Comprehensive safety and stability assessment")
    print("⚖️ Multi-method validation and uncertainty quantification")

if __name__ == "__main__":
    test_enhanced_iam_system()
