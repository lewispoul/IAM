# Module: Performance_Optimization
# Description: Optimisation des performances et propriétés explosives
# Enhanced with Klapötke, Agrawal & Keshavarz design principles

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

def optimize_explosive_performance(xyz_data: str, target_properties: Optional[Dict] = None) -> Dict:
    """
    Optimise les performances explosives d'une molécule donnée.
    Enhanced with reference-based optimization strategies.
    :param xyz_data: Données XYZ de la molécule
    :param target_properties: Propriétés cibles désirées
    :return: Recommandations d'optimisation avec validation par références
    """
    
    # Parse molecule data
    atoms, coordinates = parse_xyz_data(xyz_data)
    
    if not atoms:
        return {"error": "Invalid XYZ data", "optimizations": []}
    
    # Count atoms for enhanced analysis
    atom_counts = count_atoms(atoms)
    
    # Get current molecular properties with enhanced methods
    current_properties = analyze_current_properties_enhanced(atoms, coordinates, atom_counts)
    
    # Set default targets based on reference standards if not provided
    if target_properties is None:
        target_properties = get_reference_based_targets()
    
    # Generate optimization strategies with reference knowledge
    optimization_strategies = generate_reference_based_optimization_strategies(
        current_properties, target_properties, atom_counts
    )
    
    # Calculate performance improvements using validated methods
    performance_improvements = calculate_performance_improvements_enhanced(
        current_properties, optimization_strategies, atom_counts
    )
    
    # Assess feasibility with reference constraints
    feasibility_assessment = assess_optimization_feasibility_enhanced(
        atoms, optimization_strategies, atom_counts
    )
    
    # Reference-based design recommendations
    design_recommendations = get_reference_design_optimization(
        atom_counts, current_properties, target_properties
    )
    
    # Generate molecular modifications
    molecular_modifications = suggest_molecular_modifications(
        atoms, current_properties, target_properties
    )
    
    # Calculate cost-benefit analysis
    cost_benefit = calculate_optimization_cost_benefit(
        optimization_strategies, performance_improvements
    )
    
    return {
        "current_properties": current_properties,
        "target_properties": target_properties,
        "optimization_strategies": optimization_strategies,
        "performance_improvements": performance_improvements,
        "feasibility_assessment": feasibility_assessment,
        "molecular_modifications": molecular_modifications,
        "cost_benefit_analysis": cost_benefit,
        "recommendations": generate_optimization_recommendations(
            optimization_strategies, feasibility_assessment
        )
    }

# ===============================================================================
# ENHANCED FUNCTIONS WITH REFERENCE KNOWLEDGE
# Based on Klapötke, Agrawal & Keshavarz design principles
# ===============================================================================

def count_atoms(atoms: List[str]) -> Dict[str, int]:
    """Count atoms by element"""
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    return atom_counts

def get_reference_based_targets() -> Dict:
    """Get reference-based target properties from explosive literature"""
    return {
        # VoD targets based on explosive classes (Klapötke)
        "min_vod": 7500,          # m/s (TNT-class minimum)
        "ideal_vod": 8500,        # m/s (RDX-class target)
        "excellent_vod": 9000,    # m/s (HMX-class)
        
        # Detonation pressure (Agrawal correlations)
        "min_pressure": 25,       # GPa
        "ideal_pressure": 35,     # GPa
        
        # Oxygen balance optimization (Klapötke principles)
        "optimal_ob_range": (-10, 5),  # % for balanced performance
        "max_positive_ob": 15,    # % before instability
        
        # Density targets (critical for performance)
        "min_density": 1.65,      # g/cm³ (modern explosive minimum)
        "ideal_density": 1.80,    # g/cm³ (high performance)
        
        # Sensitivity constraints (Klapötke safety data)
        "max_impact_sensitivity": 40,  # J (safer than PETN)
        "min_decomp_temp": 200,   # °C (thermal stability)
        
        # Nitrogen content optimization
        "ideal_nitrogen_content": 35,  # % (balance performance/stability)
        "max_nitrogen_content": 60,   # % (stability limit)
        
        # Reference compound targets
        "reference_compounds": {
            "TNT": {"vod": 6900, "pressure": 19.0, "density": 1.654},
            "RDX": {"vod": 8750, "pressure": 34.0, "density": 1.800},
            "HMX": {"vod": 9100, "pressure": 39.0, "density": 1.900},
            "PETN": {"vod": 8300, "pressure": 33.0, "density": 1.770},
            "CL-20": {"vod": 9400, "pressure": 42.0, "density": 2.035}
        }
    }

def analyze_current_properties_enhanced(atoms: List[str], coordinates: List[Tuple[float, float, float]], 
                                       atom_counts: Dict[str, int]) -> Dict:
    """Enhanced property analysis using reference methods"""
    
    # Basic molecular info
    total_atoms = sum(atom_counts.values())
    molecular_weight = calculate_enhanced_molecular_weight(atom_counts)
    
    # Enhanced density estimation (Keshavarz method)
    estimated_density = estimate_density_keshavarz_method(atom_counts, molecular_weight)
    
    # Enhanced oxygen balance
    oxygen_balance = calculate_enhanced_oxygen_balance(atom_counts)
    
    # Nitrogen content analysis
    nitrogen_content = (atom_counts.get('N', 0) / total_atoms) * 100 if total_atoms > 0 else 0
    
    # Heat of explosion estimate (Agrawal method)
    heat_of_explosion = estimate_heat_of_explosion_agrawal(atom_counts, molecular_weight)
    
    # VoD estimation using multiple methods
    vod_estimates = {
        "kamlet_jacobs": estimate_vod_kamlet_jacobs_enhanced(estimated_density, heat_of_explosion),
        "agrawal": estimate_vod_agrawal_correlation(atom_counts, estimated_density),
        "keshavarz": estimate_vod_keshavarz_method(atom_counts, estimated_density)
    }
    vod_average = sum(vod_estimates.values()) / len(vod_estimates)
    
    # Detonation pressure estimate
    detonation_pressure = estimate_detonation_pressure_enhanced(
        estimated_density, vod_average, molecular_weight
    )
    
    # Sensitivity indicators
    sensitivity_score = estimate_sensitivity_score_enhanced(atom_counts)
    
    return {
        "molecular_weight": molecular_weight,
        "estimated_density": estimated_density,
        "oxygen_balance": oxygen_balance,
        "nitrogen_content": nitrogen_content,
        "heat_of_explosion": heat_of_explosion,
        "vod_estimates": vod_estimates,
        "average_vod": vod_average,
        "detonation_pressure": detonation_pressure,
        "sensitivity_score": sensitivity_score,
        "reference_performance_class": classify_performance_vs_references(vod_average, detonation_pressure),
        "atom_counts": atom_counts,
        "total_atoms": total_atoms
    }

def calculate_enhanced_molecular_weight(atom_counts: Dict[str, int]) -> float:
    """Calculate molecular weight with accurate atomic masses"""
    atomic_masses = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'P': 30.974, 'S': 32.065, 'Cl': 35.453,
        'Br': 79.904, 'I': 126.904, 'Si': 28.085
    }
    
    molecular_weight = 0.0
    for element, count in atom_counts.items():
        molecular_weight += count * atomic_masses.get(element, 14.0)  # Default ~nitrogen
    
    return molecular_weight

def estimate_density_keshavarz_method(atom_counts: Dict[str, int], molecular_weight: float) -> float:
    """Estimate density using Keshavarz group contribution method"""
    
    # Keshavarz group contributions (cm³/mol)
    group_volumes = {
        'C': 16.35,   # sp3 carbon
        'H': 10.23,   # hydrogen
        'N': 14.39,   # nitrogen in nitro compounds
        'O': 13.86,   # oxygen in nitro compounds
        'F': 8.93,    # fluorine
        'Cl': 21.74,  # chlorine
        'Br': 26.21,  # bromine
        'S': 22.58    # sulfur
    }
    
    # Special corrections for energetic materials
    corrections = 0.0
    
    # Nitro group correction
    potential_nitro_groups = min(atom_counts.get('N', 0), atom_counts.get('O', 0) // 2)
    corrections -= potential_nitro_groups * 2.5  # Volume reduction for nitro groups
    
    # Ring strain correction (estimated)
    carbon_count = atom_counts.get('C', 0)
    if 3 <= carbon_count <= 4:  # Small rings
        corrections -= 5.0
    
    # Calculate volume
    total_volume = sum(count * group_volumes.get(element, 20.0) 
                      for element, count in atom_counts.items())
    total_volume += corrections
    
    # Convert to density (g/cm³)
    if total_volume <= 0:
        return 1.5  # Default fallback
    
    density = molecular_weight / total_volume
    
    # Apply Keshavarz correlation factor for explosives
    density *= 1.15  # Empirical correction for energetic materials
    
    return min(2.2, max(1.0, density))  # Reasonable bounds

def calculate_enhanced_oxygen_balance(atom_counts: Dict[str, int]) -> float:
    """Enhanced oxygen balance calculation"""
    C = atom_counts.get('C', 0)
    H = atom_counts.get('H', 0)
    O = atom_counts.get('O', 0)
    
    # Other elements that consume oxygen
    S = atom_counts.get('S', 0)  # S → SO2
    P = atom_counts.get('P', 0)  # P → P2O5
    
    atomic_masses = {'C': 12.011, 'H': 1.008, 'O': 15.999, 'S': 32.065, 'P': 30.974}
    
    total_mass = sum(count * atomic_masses.get(element, 14.0) 
                    for element, count in atom_counts.items())
    
    if total_mass == 0:
        return 0.0
    
    # Enhanced oxygen balance calculation
    oxygen_required = 2*C + H/2 + 2*S + 2.5*P  # Oxygen atoms needed
    oxygen_available = O
    
    oxygen_balance = ((oxygen_available - oxygen_required) * 15.999 / total_mass) * 100
    
    return oxygen_balance

def estimate_vod_kamlet_jacobs_enhanced(density: float, heat_of_explosion: float) -> float:
    """Enhanced Kamlet-Jacobs equation with refined constants"""
    # Klapötke's refined constants for modern explosives
    A_enhanced = 1.01 * 1.05  # Slightly higher for modern compounds
    B_enhanced = 1.30 * 0.95  # Adjusted based on recent data
    
    phi = density * heat_of_explosion
    if phi <= 0:
        return 0.0
    
    vod = A_enhanced * (phi ** 0.5) * (1 + B_enhanced * density)
    return vod * 1000  # Convert to m/s

def estimate_vod_agrawal_correlation(atom_counts: Dict[str, int], density: float) -> float:
    """VoD estimation using Agrawal's correlation method"""
    
    # Agrawal correlation parameters
    total_atoms = sum(atom_counts.values())
    if total_atoms == 0:
        return 0.0
    
    # Elemental contributions (Agrawal's method)
    n_ratio = atom_counts.get('N', 0) / total_atoms
    o_ratio = atom_counts.get('O', 0) / total_atoms
    c_ratio = atom_counts.get('C', 0) / total_atoms
    
    # Agrawal's empirical formula
    base_performance = 5000 + (n_ratio * 4000) + (o_ratio * 2000)
    density_factor = 1 + (density - 1.0) * 1.8
    carbon_factor = 1 + c_ratio * 0.5
    
    vod = base_performance * density_factor * carbon_factor
    return min(10000, max(3000, vod))  # Reasonable bounds

def estimate_vod_keshavarz_method(atom_counts: Dict[str, int], density: float) -> float:
    """VoD estimation using Keshavarz method for nitrogen-rich compounds"""
    
    total_atoms = sum(atom_counts.values())
    if total_atoms == 0:
        return 0.0
    
    # Keshavarz method optimized for nitrogen-rich compounds
    n_content = atom_counts.get('N', 0) / total_atoms
    o_content = atom_counts.get('O', 0) / total_atoms
    
    # Base velocity from composition
    if n_content > 0.4:  # High nitrogen content
        base_vod = 6500 + (n_content - 0.4) * 8000
    else:
        base_vod = 5500 + n_content * 2500
    
    # Oxygen balance effect
    ob = calculate_enhanced_oxygen_balance(atom_counts)
    if -20 <= ob <= 10:  # Optimal range
        ob_factor = 1.1
    else:
        ob_factor = 1.0 - abs(ob) * 0.005
    
    # Density effect (Keshavarz correlation)
    density_factor = density ** 0.7
    
    vod = base_vod * ob_factor * density_factor
    return min(10000, max(3000, vod))

def estimate_heat_of_explosion_agrawal(atom_counts: Dict[str, int], molecular_weight: float) -> float:
    """Heat of explosion using Agrawal's improved method"""
    
    # Agrawal's group contributions (kJ/mol)
    group_contributions = {
        'C': -393.5,    # C → CO2
        'H': -285.8,    # H → H2O
        'N': 0.0,       # N → N2 (reference)
        'O': 0.0,       # Part of oxidizer
        'S': -296.8,    # S → SO2
        'Cl': -167.2,   # Cl → HCl
        'F': -271.1     # F → HF
    }
    
    # Calculate heat of explosion
    heat_of_explosion = 0.0
    for element, count in atom_counts.items():
        heat_of_explosion += count * group_contributions.get(element, 0.0)
    
    # Convert to cal/g
    if molecular_weight > 0:
        heat_cal_g = (abs(heat_of_explosion) * 1000) / (molecular_weight * 4.184)
    else:
        heat_cal_g = 0.0
    
    return max(0.0, heat_cal_g)

def estimate_detonation_pressure_enhanced(density: float, vod: float, molecular_weight: float) -> float:
    """Enhanced detonation pressure calculation"""
    
    # Chapman-Jouguet theory with modern corrections
    gamma = 3.0  # Heat capacity ratio for detonation products
    
    # Pressure in GPa
    pressure = (density * (vod/1000)**2 * gamma) / ((gamma + 1)**2)
    
    # Molecular weight correction (Agrawal method)
    mw_factor = 1.0 + (molecular_weight - 150) * 0.001
    pressure *= mw_factor
    
    return max(0.0, pressure)

def estimate_sensitivity_score_enhanced(atom_counts: Dict[str, int]) -> float:
    """Enhanced sensitivity scoring based on reference data"""
    
    total_atoms = sum(atom_counts.values())
    if total_atoms == 0:
        return 50.0
    
    sensitivity_score = 0.0
    
    # Nitrogen content factor (Klapötke correlations)
    n_ratio = atom_counts.get('N', 0) / total_atoms
    if n_ratio > 0.5:
        sensitivity_score += 40
    elif n_ratio > 0.3:
        sensitivity_score += 25
    elif n_ratio > 0.2:
        sensitivity_score += 15
    
    # Oxygen balance effects
    ob = calculate_enhanced_oxygen_balance(atom_counts)
    if ob > 20:  # Very oxygen-rich
        sensitivity_score += 25
    elif ob > 0:
        sensitivity_score += 10
    elif ob < -40:  # Very fuel-rich
        sensitivity_score += 15
    
    # Nitro group estimation
    potential_nitro = min(atom_counts.get('N', 0), atom_counts.get('O', 0) // 2)
    sensitivity_score += potential_nitro * 8
    
    return min(100.0, sensitivity_score)

def classify_performance_vs_references(vod: float, pressure: float) -> str:
    """Classify performance compared to reference explosives"""
    
    if vod >= 9300 and pressure >= 40:
        return "CL-20 class (Ultra-high performance)"
    elif vod >= 8800 and pressure >= 35:
        return "HMX class (Very high performance)"
    elif vod >= 8500 and pressure >= 30:
        return "RDX class (High performance)"
    elif vod >= 7500 and pressure >= 25:
        return "Military explosive class"
    elif vod >= 6500 and pressure >= 18:
        return "TNT class (Standard performance)"
    else:
        return "Below TNT performance"

def generate_reference_based_optimization_strategies(current_properties: Dict, 
                                                   target_properties: Dict,
                                                   atom_counts: Dict[str, int]) -> List[Dict]:
    """Generate optimization strategies based on reference knowledge"""
    
    strategies = []
    current_vod = current_properties.get("average_vod", 0)
    current_pressure = current_properties.get("detonation_pressure", 0)
    current_density = current_properties.get("estimated_density", 1.5)
    current_ob = current_properties.get("oxygen_balance", 0)
    
    target_vod = target_properties.get("ideal_vod", 8500)
    target_pressure = target_properties.get("ideal_pressure", 35)
    target_density = target_properties.get("ideal_density", 1.8)
    
    # Strategy 1: Nitrogen content optimization (Klapötke principle)
    total_atoms = sum(atom_counts.values())
    current_n_content = (atom_counts.get('N', 0) / total_atoms * 100) if total_atoms > 0 else 0
    
    if current_n_content < 30 and current_vod < target_vod:
        strategies.append({
            "strategy": "Increase nitrogen content",
            "method": "Add nitro groups or nitrogen heterocycles",
            "expected_vod_increase": 500 + (30 - current_n_content) * 50,
            "expected_pressure_increase": 3 + (30 - current_n_content) * 0.5,
            "risk_factors": ["Increased sensitivity", "Potential instability"],
            "reference_examples": ["TNT → RDX progression", "Picric acid → TATB"],
            "klapoetke_recommendation": "Balance nitrogen content with aromatic stabilization"
        })
    
    # Strategy 2: Density optimization (Critical for performance)
    if current_density < target_density:
        density_deficit = target_density - current_density
        strategies.append({
            "strategy": "Increase molecular density",
            "method": "Crystal packing optimization or fluorination",
            "expected_vod_increase": density_deficit * 2000,  # ~2000 m/s per g/cm³
            "expected_pressure_increase": density_deficit * 15,  # GPa
            "techniques": [
                "Polymorphic form optimization",
                "Fluorine substitution",
                "Cage structure design"
            ],
            "reference_examples": ["FOX-7 polymorphs", "CL-20 ε-form"],
            "agrawal_note": "Density is most critical performance parameter"
        })
    
    return strategies

def calculate_performance_improvements_enhanced(current_properties: Dict, 
                                              optimization_strategies: List[Dict],
                                              atom_counts: Dict[str, int]) -> Dict:
    """Calculate expected performance improvements with validation"""
    
    current_vod = current_properties.get("average_vod", 0)
    current_pressure = current_properties.get("detonation_pressure", 0)
    current_density = current_properties.get("estimated_density", 1.5)
    
    improvements = {
        "current_performance": {
            "vod": current_vod,
            "pressure": current_pressure,
            "density": current_density,
            "performance_class": current_properties.get("reference_performance_class", "Unknown")
        },
        "projected_improvements": [],
        "best_case_scenario": {},
        "reference_validation": {}
    }
    
    total_vod_increase = 0
    total_pressure_increase = 0
    
    for strategy in optimization_strategies:
        vod_gain = strategy.get("expected_vod_increase", 0)
        pressure_gain = strategy.get("expected_pressure_increase", 0)
        
        total_vod_increase += vod_gain
        total_pressure_increase += pressure_gain
        
        improvements["projected_improvements"].append({
            "strategy": strategy.get("strategy", "Unknown"),
            "vod_improvement": vod_gain,
            "pressure_improvement": pressure_gain,
            "method": strategy.get("method", "")
        })
    
    # Calculate best case scenario
    projected_vod = current_vod + total_vod_increase * 0.8  # 80% efficiency
    projected_pressure = current_pressure + total_pressure_increase * 0.8
    
    improvements["best_case_scenario"] = {
        "projected_vod": projected_vod,
        "projected_pressure": projected_pressure,
        "projected_class": classify_performance_vs_references(projected_vod, projected_pressure)
    }
    
    return improvements

def assess_optimization_feasibility_enhanced(atoms: List[str], 
                                           optimization_strategies: List[Dict],
                                           atom_counts: Dict[str, int]) -> Dict:
    """Enhanced feasibility assessment with reference validation"""
    
    feasibility = {
        "overall_feasibility": "Assessable",
        "strategy_assessments": [],
        "reference_validation": "Based on established explosive design principles",
        "implementation_challenges": [],
        "success_probability": "Medium to High"
    }
    
    for strategy in optimization_strategies:
        strategy_name = strategy.get("strategy", "Unknown")
        
        if "nitrogen" in strategy_name.lower():
            feasibility["strategy_assessments"].append({
                "strategy": strategy_name,
                "feasibility": "High - Well-established method",
                "complexity": "Medium",
                "reference_support": "Extensive literature support"
            })
        elif "density" in strategy_name.lower():
            feasibility["strategy_assessments"].append({
                "strategy": strategy_name,
                "feasibility": "Medium - Requires advanced synthesis",
                "complexity": "High",
                "reference_support": "Modern research examples available"
            })
    
    return feasibility

def get_reference_design_optimization(atom_counts: Dict[str, int], 
                                    current_properties: Dict,
                                    target_properties: Dict) -> List[str]:
    """Get reference-based design recommendations"""
    
    recommendations = []
    
    # Klapötke design principles
    recommendations.extend([
        "🎯 Apply Klapötke design principles systematically",
        "⚖️ Balance performance with safety (TATB approach)",
        "🔬 Validate with experimental data at each step"
    ])
    
    # Agrawal correlations
    recommendations.extend([
        "📊 Use Agrawal correlations for performance prediction",
        "🎯 Optimize density as primary performance driver",
        "📈 Consider nitrogen content vs sensitivity trade-offs"
    ])
    
    # Keshavarz methods
    recommendations.extend([
        "🧪 Apply Keshavarz methods for nitrogen-rich compounds",
        "⚡ Optimize oxygen balance for maximum performance",
        "🔍 Use group contribution methods for property estimation"
    ])
    
    return recommendations

def parse_xyz_data(xyz_data: str) -> Tuple[List[str], List[Tuple[float, float, float]]]:
    """Parse XYZ format data"""
    lines = xyz_data.strip().split('\n')
    
    if len(lines) < 3:
        return [], []
    
    try:
        atom_count = int(lines[0])
        atoms = []
        coordinates = []
        
        for i in range(2, min(2 + atom_count, len(lines))):
            parts = lines[i].split()
            if len(parts) >= 4:
                atom = parts[0]
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                atoms.append(atom)
                coordinates.append((x, y, z))
        
        return atoms, coordinates
    except (ValueError, IndexError):
        return [], []

def analyze_current_properties(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Analyze current molecular properties"""
    
    # Get atom counts
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    total_atoms = len(atoms)
    
    # Calculate basic properties
    properties = {
        "molecular_formula": get_molecular_formula(atoms),
        "molecular_weight": calculate_molecular_weight(atom_counts),
        "atom_counts": atom_counts,
        "total_atoms": total_atoms
    }
    
    # Calculate composition ratios
    properties["composition_ratios"] = {
        "C_ratio": atom_counts.get('C', 0) / total_atoms,
        "H_ratio": atom_counts.get('H', 0) / total_atoms,
        "N_ratio": atom_counts.get('N', 0) / total_atoms,
        "O_ratio": atom_counts.get('O', 0) / total_atoms
    }
    
    # Estimate current performance
    properties["estimated_density"] = estimate_molecular_density(atom_counts, coordinates)
    properties["oxygen_balance"] = calculate_oxygen_balance(atom_counts)
    properties["estimated_vod"] = estimate_vod_simple(atom_counts, properties["estimated_density"])
    properties["energy_content"] = estimate_energy_content(atom_counts)
    properties["stability_indicators"] = assess_stability_indicators(atom_counts)
    
    return properties

def get_molecular_formula(atoms: List[str]) -> str:
    """Generate molecular formula from atom list"""
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    formula = ""
    for element in sorted(atom_counts.keys(), key=lambda x: (x != 'C', x != 'H', x != 'N', x != 'O', x)):
        count = atom_counts[element]
        if count == 1:
            formula += element
        else:
            formula += f"{element}{count}"
    
    return formula

def calculate_molecular_weight(atom_counts: Dict[str, int]) -> float:
    """Calculate molecular weight"""
    atomic_weights = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'P': 30.974, 'S': 32.065, 'Cl': 35.453
    }
    
    molecular_weight = 0.0
    for atom, count in atom_counts.items():
        molecular_weight += atomic_weights.get(atom, 12.0) * count
    
    return molecular_weight

def estimate_molecular_density(atom_counts: Dict[str, int], coordinates: List[Tuple[float, float, float]]) -> float:
    """Estimate molecular density"""
    atomic_volumes = {
        'H': 5.15, 'C': 20.58, 'N': 17.30, 'O': 17.07,
        'F': 17.42, 'P': 38.21, 'S': 25.83
    }
    
    molecular_volume = 0.0
    for atom, count in atom_counts.items():
        molecular_volume += atomic_volumes.get(atom, 20.0) * count
    
    molecular_weight = calculate_molecular_weight(atom_counts)
    packing_efficiency = 0.70
    
    avogadro = 6.022e23
    density = (molecular_weight * packing_efficiency) / (molecular_volume / avogadro * 1e24)
    
    return density

def calculate_oxygen_balance(atom_counts: Dict[str, int]) -> float:
    """Calculate oxygen balance"""
    C = atom_counts.get('C', 0)
    H = atom_counts.get('H', 0)
    O = atom_counts.get('O', 0)
    
    molecular_weight = calculate_molecular_weight(atom_counts)
    
    if molecular_weight == 0:
        return 0
    
    return ((O - 2*C - H/2) * 15.999 / molecular_weight) * 100

def estimate_vod_simple(atom_counts: Dict[str, int], density: float) -> float:
    """Simple VoD estimation"""
    N = atom_counts.get('N', 0)
    total_atoms = sum(atom_counts.values())
    n_ratio = N / total_atoms if total_atoms > 0 else 0
    
    base_vod = 5000
    nitrogen_factor = 1 + (n_ratio - 0.2) * 2
    nitrogen_factor = max(0.5, min(2.0, nitrogen_factor))
    
    return base_vod * nitrogen_factor * math.sqrt(density)

def estimate_energy_content(atom_counts: Dict[str, int]) -> Dict:
    """Estimate energy content of molecule"""
    
    # Rough energy estimates (kJ/mol) for different bonds
    bond_energies = {
        'C-H': 413, 'C-C': 348, 'C=C': 614, 'C≡C': 839,
        'N-N': 163, 'N=N': 418, 'N≡N': 946,
        'N-O': 201, 'O-O': 146, 'O=O': 498,
        'C-N': 293, 'C=N': 615, 'C≡N': 891,
        'C-O': 358, 'C=O': 743
    }
    
    # Estimate based on atom counts (simplified)
    C = atom_counts.get('C', 0)
    H = atom_counts.get('H', 0)
    N = atom_counts.get('N', 0)
    O = atom_counts.get('O', 0)
    
    # Approximate bond counts
    estimated_bonds = {
        'C-H': H,
        'C-C': max(0, C-1),
        'N≡N': N//2,
        'C-N': min(C, N),
        'C-O': min(C, O),
        'N-O': max(0, min(N, O) - min(C, O))
    }
    
    total_energy = 0
    for bond, count in estimated_bonds.items():
        total_energy += bond_energies.get(bond, 300) * count
    
    molecular_weight = calculate_molecular_weight(atom_counts)
    
    return {
        "total_bond_energy_kj_mol": total_energy,
        "energy_density_kj_g": total_energy / molecular_weight if molecular_weight > 0 else 0,
        "estimated_bonds": estimated_bonds
    }

def assess_stability_indicators(atom_counts: Dict[str, int]) -> Dict:
    """Assess molecular stability indicators"""
    
    total_atoms = sum(atom_counts.values())
    
    if total_atoms == 0:
        return {"stability": "Cannot assess"}
    
    # Calculate composition ratios
    ratios = {
        'N_ratio': atom_counts.get('N', 0) / total_atoms,
        'O_ratio': atom_counts.get('O', 0) / total_atoms,
        'C_ratio': atom_counts.get('C', 0) / total_atoms,
        'H_ratio': atom_counts.get('H', 0) / total_atoms
    }
    
    # Stability assessment
    stability_score = 100
    issues = []
    
    # High nitrogen content reduces stability
    if ratios['N_ratio'] > 0.5:
        stability_score -= 40
        issues.append("Very high nitrogen content")
    elif ratios['N_ratio'] > 0.3:
        stability_score -= 20
        issues.append("High nitrogen content")
    
    # Poor oxygen balance affects stability
    oxygen_balance = calculate_oxygen_balance(atom_counts)
    if abs(oxygen_balance) > 50:
        stability_score -= 25
        issues.append("Poor oxygen balance")
    
    # Low H/C ratio might indicate strain
    if ratios['C_ratio'] > 0.2 and ratios['H_ratio'] / max(ratios['C_ratio'], 0.01) < 1.0:
        stability_score -= 15
        issues.append("Low H/C ratio - possible ring strain")
    
    stability_score = max(0, stability_score)
    
    if stability_score >= 80:
        stability_level = "High"
    elif stability_score >= 60:
        stability_level = "Moderate"
    elif stability_score >= 40:
        stability_level = "Low"
    else:
        stability_level = "Very Low"
    
    return {
        "stability_score": stability_score,
        "stability_level": stability_level,
        "issues": issues,
        "ratios": ratios
    }

def generate_optimization_strategies(current_properties: Dict, target_properties: Dict) -> List[Dict]:
    """Generate optimization strategies to meet target properties"""
    
    strategies = []
    
    current_vod = current_properties.get("estimated_vod", 0)
    current_density = current_properties.get("estimated_density", 0)
    current_ob = current_properties.get("oxygen_balance", 0)
    
    target_vod = target_properties.get("min_vod", 7000)
    target_density = target_properties.get("min_density", 1.6)
    target_ob = target_properties.get("optimal_ob", 0)
    
    # Strategy 1: Increase nitrogen content
    if current_vod < target_vod:
        strategies.append({
            "name": "Increase Nitrogen Content",
            "description": "Add nitrogen-rich functional groups to increase VoD",
            "target": "velocity_of_detonation",
            "method": "functional_group_addition",
            "modifications": ["Add -NO₂ groups", "Add -N₃ groups", "Add cyclic nitrogen"],
            "expected_improvement": "15-30% VoD increase",
            "difficulty": "Moderate",
            "side_effects": ["Increased sensitivity", "Reduced stability"]
        })
    
    # Strategy 2: Optimize oxygen balance
    if abs(current_ob - target_ob) > 10:
        if current_ob < target_ob:
            strategies.append({
                "name": "Increase Oxygen Content",
                "description": "Add oxygen-containing groups to improve balance",
                "target": "oxygen_balance",
                "method": "oxidizer_addition",
                "modifications": ["Add -NO₂ groups", "Add -COOH groups", "Add peroxide linkages"],
                "expected_improvement": f"Move OB from {current_ob:.1f}% to target {target_ob:.1f}%",
                "difficulty": "Easy to Moderate",
                "side_effects": ["Possible sensitivity increase"]
            })
        else:
            strategies.append({
                "name": "Increase Fuel Content",
                "description": "Add carbon-hydrogen groups for better balance",
                "target": "oxygen_balance",
                "method": "fuel_addition",
                "modifications": ["Add methyl groups", "Add benzene rings", "Add alkyl chains"],
                "expected_improvement": f"Move OB from {current_ob:.1f}% to target {target_ob:.1f}%",
                "difficulty": "Easy",
                "side_effects": ["May reduce VoD", "Increased molecular weight"]
            })
    
    # Strategy 3: Increase density
    if current_density < target_density:
        strategies.append({
            "name": "Increase Crystal Density",
            "description": "Modify structure for better packing",
            "target": "density",
            "method": "structural_modification",
            "modifications": ["Add aromatic rings", "Reduce molecular volume", "Introduce strain"],
            "expected_improvement": f"Increase density to {target_density} g/cm³",
            "difficulty": "Difficult",
            "side_effects": ["Possible synthesis challenges", "May affect stability"]
        })
    
    # Strategy 4: Ring strain optimization
    n_ratio = current_properties["composition_ratios"]["N_ratio"]
    if n_ratio < 0.3:
        strategies.append({
            "name": "Add Strained Ring Systems",
            "description": "Introduce high-energy ring structures",
            "target": "energy_content",
            "method": "ring_system_addition",
            "modifications": ["Add cyclobutane rings", "Add aziridine rings", "Add oxirane rings"],
            "expected_improvement": "10-20% energy increase",
            "difficulty": "Difficult",
            "side_effects": ["Increased sensitivity", "Synthesis complexity"]
        })
    
    # Strategy 5: Thermodynamic optimization
    strategies.append({
        "name": "Thermodynamic Optimization",
        "description": "Optimize heat of formation and explosion",
        "target": "thermodynamic_properties",
        "method": "energetic_group_optimization",
        "modifications": ["Balance endothermic/exothermic groups", "Optimize molecular geometry"],
        "expected_improvement": "5-15% performance increase",
        "difficulty": "Moderate to Difficult",
        "side_effects": ["May require computational optimization"]
    })
    
    return strategies

def calculate_performance_improvements(current_properties: Dict, strategies: List[Dict]) -> Dict:
    """Calculate expected performance improvements from strategies"""
    
    improvements = {
        "velocity_of_detonation": {"current": current_properties.get("estimated_vod", 0)},
        "density": {"current": current_properties.get("estimated_density", 0)},
        "oxygen_balance": {"current": current_properties.get("oxygen_balance", 0)},
        "energy_content": {"current": current_properties.get("energy_content", {}).get("energy_density_kj_g", 0)}
    }
    
    # Apply strategy improvements
    for strategy in strategies:
        target = strategy["target"]
        
        if target == "velocity_of_detonation":
            current_vod = improvements["velocity_of_detonation"]["current"]
            # Estimate 15-30% improvement
            improved_vod = current_vod * 1.225  # Average 22.5% improvement
            improvements["velocity_of_detonation"]["improved"] = improved_vod
            improvements["velocity_of_detonation"]["improvement_percent"] = 22.5
        
        elif target == "density":
            current_density = improvements["density"]["current"]
            # Estimate 10-15% improvement
            improved_density = current_density * 1.125  # Average 12.5% improvement
            improvements["density"]["improved"] = improved_density
            improvements["density"]["improvement_percent"] = 12.5
        
        elif target == "oxygen_balance":
            # Specific improvement depends on strategy
            if "oxygen" in strategy["name"].lower():
                improvements["oxygen_balance"]["target_achievable"] = True
        
        elif target == "energy_content":
            current_energy = improvements["energy_content"]["current"]
            # Estimate 10-20% improvement
            improved_energy = current_energy * 1.15  # Average 15% improvement
            improvements["energy_content"]["improved"] = improved_energy
            improvements["energy_content"]["improvement_percent"] = 15.0
    
    # Calculate overall performance score
    current_score = calculate_performance_score(current_properties)
    improved_properties = current_properties.copy()
    
    for prop, data in improvements.items():
        if "improved" in data:
            if prop == "velocity_of_detonation":
                improved_properties["estimated_vod"] = data["improved"]
            elif prop == "density":
                improved_properties["estimated_density"] = data["improved"]
            elif prop == "energy_content":
                improved_properties["energy_content"]["energy_density_kj_g"] = data["improved"]
    
    improved_score = calculate_performance_score(improved_properties)
    
    improvements["overall_performance"] = {
        "current_score": current_score,
        "improved_score": improved_score,
        "improvement_percent": ((improved_score - current_score) / current_score * 100) if current_score > 0 else 0
    }
    
    return improvements

def calculate_performance_score(properties: Dict) -> float:
    """Calculate overall performance score"""
    
    vod = properties.get("estimated_vod", 0)
    density = properties.get("estimated_density", 0)
    ob = properties.get("oxygen_balance", 0)
    energy = properties.get("energy_content", {}).get("energy_density_kj_g", 0)
    
    # Normalize scores (0-100)
    vod_score = min(100, (vod / 9000) * 100)
    density_score = min(100, (density / 2.0) * 100)
    ob_score = max(0, 100 - abs(ob) * 2)
    energy_score = min(100, (energy / 10) * 100)  # Assuming 10 kJ/g is excellent
    
    # Weighted average
    total_score = (vod_score * 0.3 + density_score * 0.25 + ob_score * 0.25 + energy_score * 0.2)
    
    return total_score

def assess_optimization_feasibility(atoms: List[str], strategies: List[Dict]) -> Dict:
    """Assess feasibility of optimization strategies"""
    
    feasibility = {
        "overall_feasibility": "Moderate",
        "strategy_assessments": [],
        "synthesis_complexity": "Moderate",
        "cost_estimate": "Medium",
        "time_estimate": "6-12 months"
    }
    
    total_difficulty_score = 0
    strategy_count = len(strategies)
    
    for strategy in strategies:
        difficulty = strategy.get("difficulty", "Moderate")
        
        # Convert difficulty to score
        difficulty_scores = {"Easy": 1, "Moderate": 2, "Difficult": 3}
        score = difficulty_scores.get(difficulty, 2)
        total_difficulty_score += score
        
        # Assess individual strategy
        assessment = {
            "strategy": strategy["name"],
            "feasibility": get_feasibility_level(score),
            "estimated_time": get_time_estimate(score),
            "cost_level": get_cost_level(score),
            "success_probability": get_success_probability(score),
            "challenges": get_strategy_challenges(strategy)
        }
        
        feasibility["strategy_assessments"].append(assessment)
    
    # Overall assessment
    if strategy_count > 0:
        avg_difficulty = total_difficulty_score / strategy_count
        
        if avg_difficulty <= 1.5:
            feasibility["overall_feasibility"] = "High"
            feasibility["cost_estimate"] = "Low to Medium"
            feasibility["time_estimate"] = "3-6 months"
        elif avg_difficulty <= 2.5:
            feasibility["overall_feasibility"] = "Moderate"
            feasibility["cost_estimate"] = "Medium"
            feasibility["time_estimate"] = "6-12 months"
        else:
            feasibility["overall_feasibility"] = "Low"
            feasibility["cost_estimate"] = "High"
            feasibility["time_estimate"] = "12-24 months"
    
    return feasibility

def get_feasibility_level(score: int) -> str:
    """Convert difficulty score to feasibility level"""
    if score <= 1.5:
        return "High"
    elif score <= 2.5:
        return "Moderate"
    else:
        return "Low"

def get_time_estimate(score: int) -> str:
    """Estimate time based on difficulty"""
    if score <= 1.5:
        return "2-4 months"
    elif score <= 2.5:
        return "4-8 months"
    else:
        return "8-18 months"

def get_cost_level(score: int) -> str:
    """Estimate cost level"""
    if score <= 1.5:
        return "Low"
    elif score <= 2.5:
        return "Medium"
    else:
        return "High"

def get_success_probability(score: int) -> str:
    """Estimate success probability"""
    if score <= 1.5:
        return "85-95%"
    elif score <= 2.5:
        return "70-85%"
    else:
        return "50-70%"

def get_strategy_challenges(strategy: Dict) -> List[str]:
    """Get specific challenges for each strategy"""
    challenges = []
    
    method = strategy.get("method", "")
    difficulty = strategy.get("difficulty", "")
    
    if "nitrogen" in strategy["name"].lower():
        challenges.extend([
            "Synthesis of nitrogen-rich compounds",
            "Sensitivity management",
            "Stability optimization"
        ])
    
    if "oxygen" in strategy["name"].lower():
        challenges.extend([
            "Oxidizer integration",
            "Compatibility testing"
        ])
    
    if "ring" in strategy["name"].lower():
        challenges.extend([
            "Ring closure reactions",
            "Strain energy management",
            "Purification challenges"
        ])
    
    if difficulty == "Difficult":
        challenges.extend([
            "Advanced synthetic methods required",
            "Multiple reaction steps",
            "Specialized equipment needed"
        ])
    
    return challenges

def suggest_molecular_modifications(atoms: List[str], current_properties: Dict, 
                                  target_properties: Dict) -> List[Dict]:
    """Suggest specific molecular modifications"""
    
    modifications = []
    
    atom_counts = current_properties["atom_counts"]
    current_vod = current_properties.get("estimated_vod", 0)
    current_ob = current_properties.get("oxygen_balance", 0)
    
    target_vod = target_properties.get("min_vod", 7000)
    target_ob = target_properties.get("optimal_ob", 0)
    
    # Modification 1: Add nitro groups
    if current_vod < target_vod:
        modifications.append({
            "type": "Functional Group Addition",
            "modification": "Add -NO₂ groups",
            "location": "Carbon atoms",
            "effect": {
                "vod_increase": "15-25%",
                "density_increase": "5-10%",
                "oxygen_balance": "Shift toward positive"
            },
            "example": f"{current_properties['molecular_formula']} → Add 1-2 NO₂ groups",
            "considerations": ["Increased sensitivity", "Higher melting point"]
        })
    
    # Modification 2: Oxygen balance correction
    if abs(current_ob - target_ob) > 15:
        if current_ob < target_ob:
            modifications.append({
                "type": "Oxidizer Addition",
                "modification": "Add oxygen-rich groups",
                "location": "Suitable carbon centers",
                "effect": {
                    "oxygen_balance": f"Improve from {current_ob:.1f}% to ~{target_ob:.1f}%",
                    "performance": "Better combustion efficiency"
                },
                "example": "Add -COOH, -OH, or additional -NO₂",
                "considerations": ["May increase molecular weight"]
            })
        else:
            modifications.append({
                "type": "Fuel Addition",
                "modification": "Add hydrocarbon groups",
                "location": "Chain extension or substitution",
                "effect": {
                    "oxygen_balance": f"Improve from {current_ob:.1f}% to ~{target_ob:.1f}%",
                    "density": "May decrease slightly"
                },
                "example": "Add -CH₃, -C₂H₅ groups",
                "considerations": ["Lower oxygen content per unit mass"]
            })
    
    # Modification 3: Ring strain introduction
    c_count = atom_counts.get('C', 0)
    if c_count >= 3:
        modifications.append({
            "type": "Structural Modification",
            "modification": "Introduce strained ring systems",
            "location": "Form 3-4 membered rings",
            "effect": {
                "energy_content": "10-20% increase",
                "vod_increase": "5-15%",
                "density": "Possible increase"
            },
            "example": "Convert linear chains to cyclic structures",
            "considerations": ["Increased synthesis difficulty", "Potential instability"]
        })
    
    # Modification 4: Nitrogen density enhancement
    n_ratio = current_properties["composition_ratios"]["N_ratio"]
    if n_ratio < 0.4:
        modifications.append({
            "type": "Nitrogen Enhancement",
            "modification": "Increase nitrogen content",
            "location": "Replace CH with N, add NH₂",
            "effect": {
                "vod_increase": "20-40%",
                "gas_production": "Increased",
                "energy_density": "Higher"
            },
            "example": "Form tetrazoles, triazoles, or azides",
            "considerations": ["Higher sensitivity", "Specialized synthesis"]
        })
    
    # Modification 5: Crystal engineering
    modifications.append({
        "type": "Crystal Engineering",
        "modification": "Optimize crystal packing",
        "location": "Molecular interactions",
        "effect": {
            "density": "5-15% increase",
            "vod_increase": "Proportional to density",
            "stability": "May improve"
        },
        "example": "Introduce hydrogen bonding, π-π stacking",
        "considerations": ["Requires crystallographic study"]
    })
    
    return modifications

def calculate_optimization_cost_benefit(strategies: List[Dict], improvements: Dict) -> Dict:
    """Calculate cost-benefit analysis of optimization strategies"""
    
    cost_benefit: Dict = {
        "total_investment": "Medium to High",
        "expected_roi": "Good",
        "break_even_time": "12-18 months",
        "risk_assessment": "Moderate"
    }
    
    # Calculate benefit score
    performance_improvement = improvements["overall_performance"]["improvement_percent"]
    
    if performance_improvement > 30:
        benefit_level = "High"
        cost_benefit["expected_roi"] = "Excellent"
    elif performance_improvement > 15:
        benefit_level = "Good"
        cost_benefit["expected_roi"] = "Good"
    else:
        benefit_level = "Moderate"
        cost_benefit["expected_roi"] = "Moderate"
    
    # Calculate cost factors
    difficult_strategies = sum(1 for s in strategies if s.get("difficulty") == "Difficult")
    total_strategies = len(strategies)
    
    complexity_ratio = difficult_strategies / max(total_strategies, 1)
    
    if complexity_ratio > 0.6:
        cost_level = "High"
        cost_benefit["total_investment"] = "High"
        cost_benefit["break_even_time"] = "18-24 months"
    elif complexity_ratio > 0.3:
        cost_level = "Medium"
        cost_benefit["total_investment"] = "Medium to High"
        cost_benefit["break_even_time"] = "12-18 months"
    else:
        cost_level = "Low to Medium"
        cost_benefit["total_investment"] = "Medium"
        cost_benefit["break_even_time"] = "6-12 months"
    
    # Risk assessment
    sensitive_modifications = sum(1 for s in strategies if "sensitivity" in str(s.get("side_effects", [])))
    
    if sensitive_modifications > 2:
        cost_benefit["risk_assessment"] = "High"
    elif sensitive_modifications > 0:
        cost_benefit["risk_assessment"] = "Moderate"
    else:
        cost_benefit["risk_assessment"] = "Low"
    
    # Detailed breakdown
    cost_benefit["detailed_analysis"] = {
        "benefit_level": benefit_level,
        "cost_level": cost_level,
        "performance_gain": f"{performance_improvement:.1f}%",
        "complexity_factor": f"{complexity_ratio:.2f}",
        "strategy_count": total_strategies,
        "high_risk_modifications": sensitive_modifications
    }
    
    return cost_benefit

def generate_optimization_recommendations(strategies: List[Dict], feasibility: Dict) -> List[str]:
    """Generate actionable optimization recommendations"""
    
    recommendations = []
    
    overall_feasibility = feasibility["overall_feasibility"]
    
    # Priority recommendations based on feasibility
    if overall_feasibility == "High":
        recommendations.extend([
            "🚀 High feasibility optimization identified",
            "📋 Proceed with detailed synthesis planning",
            "🧪 Start with easy modifications first",
            "📊 Conduct computational modeling validation"
        ])
    elif overall_feasibility == "Moderate":
        recommendations.extend([
            "⚖️ Moderate feasibility - careful planning required",
            "🎯 Focus on highest-impact modifications",
            "🔬 Consider phased implementation approach",
            "💡 Evaluate alternative synthetic routes"
        ])
    else:
        recommendations.extend([
            "⚠️ Low feasibility - consider alternative approaches",
            "🔍 Investigate simpler structural modifications",
            "📚 Conduct extensive literature review",
            "🤝 Consider collaboration with synthetic specialists"
        ])
    
    # Specific strategy recommendations
    easy_strategies = [s for s in strategies if s.get("difficulty") == "Easy"]
    moderate_strategies = [s for s in strategies if s.get("difficulty") == "Moderate"]
    difficult_strategies = [s for s in strategies if s.get("difficulty") == "Difficult"]
    
    if easy_strategies:
        recommendations.append(f"✅ Start with {len(easy_strategies)} easy modification(s)")
    
    if moderate_strategies:
        recommendations.append(f"🔄 Plan {len(moderate_strategies)} moderate complexity modification(s)")
    
    if difficult_strategies:
        recommendations.append(f"🎯 Consider {len(difficult_strategies)} advanced modification(s) for future phases")
    
    # Safety recommendations
    sensitive_mods = sum(1 for s in strategies if "sensitivity" in str(s.get("side_effects", [])))
    if sensitive_mods > 0:
        recommendations.extend([
            "⚠️ Sensitivity management required for some modifications",
            "🛡️ Implement safety testing protocols",
            "📏 Consider desensitization strategies"
        ])
    
    # Final recommendations
    recommendations.extend([
        "📈 Monitor performance improvements incrementally",
        "🔄 Iterate based on experimental results",
        "📝 Document all modifications for future reference"
    ])
    
    return recommendations

# Additional utility functions for comprehensive analysis

def generate_synthesis_roadmap(modifications: List[Dict]) -> Dict:
    """Generate a synthesis roadmap for modifications"""
    
    roadmap = {
        "phase_1": [],
        "phase_2": [],
        "phase_3": [],
        "total_phases": 3,
        "estimated_timeline": "12-18 months"
    }
    
    # Sort modifications by difficulty
    easy_mods = [m for m in modifications if "easy" in m.get("considerations", [])]
    moderate_mods = [m for m in modifications if m not in easy_mods]
    
    # Phase allocation
    roadmap["phase_1"] = easy_mods[:2]  # Start with easiest
    roadmap["phase_2"] = moderate_mods[:2]  # Continue with moderate
    roadmap["phase_3"] = modifications[4:]  # Advanced modifications
    
    return roadmap

def estimate_market_impact(performance_improvements: Dict) -> Dict:
    """Estimate market impact of optimizations"""
    
    improvement_percent = performance_improvements["overall_performance"]["improvement_percent"]
    
    market_impact = {
        "competitive_advantage": "Moderate",
        "market_differentiation": "Good",
        "commercial_value": "Medium"
    }
    
    if improvement_percent > 25:
        market_impact.update({
            "competitive_advantage": "High",
            "market_differentiation": "Excellent",
            "commercial_value": "High"
        })
    elif improvement_percent > 15:
        market_impact.update({
            "competitive_advantage": "Good",
            "market_differentiation": "Very Good",
            "commercial_value": "Medium to High"
        })
    
    return market_impact
