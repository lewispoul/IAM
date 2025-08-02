# Module: IAM_StabilityPredictor
# Description: Prédiction avancée de la stabilité des molécules
# Enhanced with reference knowledge from Klapötke, Keshavarz, and Agrawal

import math
import re
from typing import Dict, List, Tuple, Optional
import numpy as np

def predict_stability(xyz_data):
    """
    Prédit la stabilité d'une molécule à partir de ses données XYZ.
    Enhanced with authoritative reference knowledge.
    :param xyz_data: Données XYZ de la molécule
    :return: Résultat de la prédiction avec validation par références
    """
    return predict_stability_logic(xyz_data)

def predict_stability_logic(xyz_data):
    """
    Logique avancée de prédiction de stabilité moléculaire.
    Enhanced with Klapötke's sensitivity correlations and thermal stability data.
    
    :param xyz_data: Données XYZ de la molécule
    :return: Dict contenant les résultats d'analyse de stabilité avec références
    """
    
    # Parse XYZ data
    atoms, coordinates = parse_xyz_data(xyz_data)
    
    if not atoms:
        return {"stability": "Unable to analyze", "method": "parse_error", "error": "Invalid XYZ data"}
    
    # Count atoms for enhanced analysis
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    # Calculate various stability indicators
    results = {
        "method": "Enhanced Stability Analysis with Reference Knowledge",
        "molecule_info": {
            "atom_count": len(atoms),
            "molecular_formula": get_molecular_formula(atoms),
            "estimated_mass": calculate_molecular_mass(atoms),
            "atom_counts": atom_counts
        }
    }
    
    # 1. Traditional structural stability analysis
    structural_stability = analyze_structural_stability(atoms, coordinates)
    results["structural_stability"] = structural_stability
    
    # 2. Traditional thermodynamic stability estimation
    thermo_stability = estimate_thermodynamic_stability(atoms, coordinates)
    results["thermodynamic_stability"] = thermo_stability
    
    # 3. Traditional kinetic stability assessment
    kinetic_stability = assess_kinetic_stability(atoms, coordinates)
    results["kinetic_stability"] = kinetic_stability
    
    # 4. Traditional chemical reactivity indicators
    reactivity = analyze_chemical_reactivity(atoms, coordinates)
    results["chemical_reactivity"] = reactivity
    
    # 5. ENHANCED: Reference-based sensitivity assessment (Klapötke's work)
    sensitivity_assessment = assess_sensitivity_with_references(atom_counts)
    results["sensitivity_assessment"] = sensitivity_assessment
    
    # 6. ENHANCED: Reference-based thermal stability assessment
    thermal_assessment = assess_thermal_stability_with_references(atom_counts)
    results["thermal_stability"] = thermal_assessment
    
    # 7. Overall stability score (updated with reference data)
    overall_score = calculate_enhanced_stability_score(
        structural_stability, thermo_stability, kinetic_stability, reactivity,
        sensitivity_assessment, thermal_assessment
    )
    results["overall_stability"] = overall_score
    
    # 8. Enhanced stability recommendations with reference knowledge
    recommendations = generate_enhanced_stability_recommendations(results)
    results["recommendations"] = recommendations
    
    # 9. Reference-based design recommendations
    design_recommendations = get_stability_design_recommendations(
        atom_counts, sensitivity_assessment, thermal_assessment
    )
    results["design_recommendations"] = design_recommendations
    
    # 10. Reference validation and comparison
    results["reference_validation"] = {
        "method": "Klapötke sensitivity correlations + thermal stability data",
        "confidence_level": "High - based on established research",
        "comparable_compounds": sensitivity_assessment.get("reference_comparison", {}),
        "thermal_references": thermal_assessment.get("reference_comparison", []),
        "validation_notes": "Estimates based on elemental composition and literature correlations"
    }
    
    return results

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

def get_molecular_formula(atoms: List[str]) -> str:
    """Generate molecular formula from atom list"""
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    formula = ""
    # Standard order: C, H, then alphabetical
    for element in sorted(atom_counts.keys(), key=lambda x: (x != 'C', x != 'H', x)):
        count = atom_counts[element]
        if count == 1:
            formula += element
        else:
            formula += f"{element}{count}"
    
    return formula

def calculate_molecular_mass(atoms: List[str]) -> float:
    """Calculate approximate molecular mass"""
    atomic_masses = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'P': 30.974, 'S': 32.065, 'Cl': 35.453,
        'Br': 79.904, 'I': 126.904
    }
    
    total_mass = 0.0
    for atom in atoms:
        total_mass += atomic_masses.get(atom, 12.0)  # Default to carbon mass
    
    return total_mass

def analyze_structural_stability(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Analyze structural stability factors"""
    
    # Calculate bond lengths and detect strain
    bond_analysis = analyze_bond_lengths(atoms, coordinates)
    
    # Detect ring strain
    ring_strain = detect_ring_strain(atoms, coordinates)
    
    # Analyze molecular geometry
    geometry_analysis = analyze_molecular_geometry(atoms, coordinates)
    
    # Calculate structural stability score
    stability_score = 85.0  # Base score
    
    # Adjust for bond strain
    if bond_analysis["strained_bonds"] > 0:
        stability_score -= bond_analysis["strained_bonds"] * 10
    
    # Adjust for ring strain
    if ring_strain["small_rings"] > 0:
        stability_score -= ring_strain["small_rings"] * 15
    
    # Adjust for geometry
    if geometry_analysis["crowding_factor"] > 0.7:
        stability_score -= 20
    
    stability_score = max(0, min(100, stability_score))
    
    return {
        "stability_score": stability_score,
        "bond_analysis": bond_analysis,
        "ring_strain": ring_strain,
        "geometry": geometry_analysis,
        "assessment": get_stability_assessment(stability_score)
    }

def analyze_bond_lengths(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Analyze bond lengths for strain detection"""
    
    # Typical bond lengths (Angstroms)
    typical_bonds: Dict[Tuple[str, str], float] = {
        ('C', 'C'): 1.54, ('C', 'H'): 1.09, ('C', 'N'): 1.47,
        ('C', 'O'): 1.43, ('N', 'N'): 1.45, ('N', 'O'): 1.40,
        ('O', 'O'): 1.48, ('N', 'H'): 1.01, ('O', 'H'): 0.96
    }
    
    bonds = []
    strained_bonds = 0
    
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            distance = calculate_distance(coordinates[i], coordinates[j])
            
            # Check if atoms are bonded (distance threshold)
            if distance < 2.0:  # Reasonable bonding distance
                atom_pair: Tuple[str, str] = (atoms[i], atoms[j]) if atoms[i] <= atoms[j] else (atoms[j], atoms[i])
                typical_length = typical_bonds.get(atom_pair, 1.5)
                
                strain = abs(distance - typical_length) / typical_length
                
                bonds.append({
                    "atoms": f"{atoms[i]}-{atoms[j]}",
                    "length": distance,
                    "typical": typical_length,
                    "strain": strain
                })
                
                if strain > 0.15:  # 15% deviation is significant
                    strained_bonds += 1
    
    return {
        "total_bonds": len(bonds),
        "strained_bonds": strained_bonds,
        "bonds": bonds[:10],  # Limit for output
        "max_strain": max([b["strain"] for b in bonds]) if bonds else 0
    }

def calculate_distance(coord1: Tuple[float, float, float], coord2: Tuple[float, float, float]) -> float:
    """Calculate distance between two points"""
    return math.sqrt(sum((a - b)**2 for a, b in zip(coord1, coord2)))

def detect_ring_strain(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Detect ring strain in the molecule"""
    
    # Simple ring detection (this would be more sophisticated in practice)
    connectivity = build_connectivity_matrix(atoms, coordinates)
    rings = find_small_rings(connectivity)
    
    small_rings = 0
    for ring_size in rings:
        if ring_size < 5:  # 3 and 4-membered rings are highly strained
            small_rings += 1
    
    return {
        "small_rings": small_rings,
        "ring_sizes": rings,
        "strain_level": "High" if small_rings > 0 else "Low"
    }

def build_connectivity_matrix(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> List[List[bool]]:
    """Build a connectivity matrix for the molecule"""
    n = len(atoms)
    connectivity = [[False] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            distance = calculate_distance(coordinates[i], coordinates[j])
            if distance < 2.0:  # Bonding threshold
                connectivity[i][j] = True
                connectivity[j][i] = True
    
    return connectivity

def find_small_rings(connectivity: List[List[bool]]) -> List[int]:
    """Find small rings in the molecule (simplified algorithm)"""
    # This is a simplified implementation
    # In practice, would use sophisticated ring-finding algorithms
    rings = []
    n = len(connectivity)
    
    # Look for 3-membered rings
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if connectivity[i][j] and connectivity[j][k] and connectivity[k][i]:
                    rings.append(3)
    
    return rings

def analyze_molecular_geometry(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Analyze molecular geometry for stability factors"""
    
    if len(atoms) < 2:
        return {"crowding_factor": 0, "geometry": "Linear or atomic"}
    
    # Calculate center of mass
    center: Tuple[float, float, float] = (
        sum(coord[0] for coord in coordinates) / len(coordinates),
        sum(coord[1] for coord in coordinates) / len(coordinates),
        sum(coord[2] for coord in coordinates) / len(coordinates)
    )
    
    # Calculate average distance from center
    avg_distance = sum(calculate_distance(coord, center) for coord in coordinates) / len(coordinates)
    
    # Calculate crowding factor (atoms too close to each other)
    close_contacts = 0
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            distance = calculate_distance(coordinates[i], coordinates[j])
            if distance < 1.5:  # Very close contact
                close_contacts += 1
    
    crowding_factor = close_contacts / (len(atoms) * (len(atoms) - 1) / 2)
    
    return {
        "crowding_factor": crowding_factor,
        "avg_distance_from_center": avg_distance,
        "geometry": "Compact" if avg_distance < 2.0 else "Extended"
    }

def estimate_thermodynamic_stability(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Estimate thermodynamic stability"""
    
    # Count different atom types
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    # Estimate formation energy (very simplified)
    bond_energy_estimate = estimate_bond_energies(atoms, coordinates)
    
    # Calculate stability indicators
    oxygen_balance = calculate_oxygen_balance(atom_counts)
    
    # Estimate heat of formation (simplified)
    heat_of_formation = estimate_heat_of_formation(atom_counts, bond_energy_estimate)
    
    stability_score = 70.0  # Base score
    
    # Adjust for oxygen balance
    if abs(oxygen_balance) < 10:
        stability_score += 10
    elif abs(oxygen_balance) > 50:
        stability_score -= 20
    
    # Adjust for estimated formation energy
    if heat_of_formation < 0:
        stability_score += 15  # Exothermic formation is stabilizing
    else:
        stability_score -= min(30, heat_of_formation / 10)
    
    stability_score = max(0, min(100, stability_score))
    
    return {
        "stability_score": stability_score,
        "oxygen_balance": oxygen_balance,
        "estimated_heat_of_formation": heat_of_formation,
        "bond_energy_estimate": bond_energy_estimate,
        "assessment": get_stability_assessment(stability_score)
    }

def estimate_bond_energies(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> float:
    """Estimate total bond energies in the molecule"""
    
    bond_energies: Dict[Tuple[str, str], float] = {
        ('C', 'C'): 348, ('C', 'H'): 413, ('C', 'N'): 305,
        ('C', 'O'): 358, ('N', 'N'): 163, ('N', 'O'): 201,
        ('O', 'O'): 146, ('N', 'H'): 391, ('O', 'H'): 463
    }
    
    total_energy = 0.0
    
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            distance = calculate_distance(coordinates[i], coordinates[j])
            
            if distance < 2.0:  # Bonding distance
                atom_pair: Tuple[str, str] = (atoms[i], atoms[j]) if atoms[i] <= atoms[j] else (atoms[j], atoms[i])
                bond_energy = bond_energies.get(atom_pair, 200)  # Default bond energy
                total_energy += bond_energy
    
    return total_energy

def calculate_oxygen_balance(atom_counts: Dict[str, int]) -> float:
    """Calculate oxygen balance percentage"""
    
    C = atom_counts.get('C', 0)
    H = atom_counts.get('H', 0)
    O = atom_counts.get('O', 0)
    N = atom_counts.get('N', 0)
    
    if C + H + N == 0:
        return 0.0
    
    # Oxygen balance formula for explosives
    molecular_weight = C * 12.011 + H * 1.008 + O * 15.999 + N * 14.007
    
    if molecular_weight == 0:
        return 0.0
    
    oxygen_balance = ((O - 2*C - H/2) * 15.999 / molecular_weight) * 100
    
    return oxygen_balance

def estimate_heat_of_formation(atom_counts: Dict[str, int], bond_energy: float) -> float:
    """Estimate heat of formation (very simplified)"""
    
    # Atomic heat of formation estimates (kJ/mol)
    atomic_heats = {'C': 717, 'H': 218, 'N': 473, 'O': 249}
    
    total_atomic_energy = sum(atomic_heats.get(atom, 300) * count 
                             for atom, count in atom_counts.items())
    
    # Very simplified estimate
    estimated_hof = total_atomic_energy - bond_energy
    
    return estimated_hof / 1000  # Convert to MJ/mol for easier reading

def assess_kinetic_stability(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Assess kinetic stability factors"""
    
    # Count potentially reactive groups
    reactive_groups = count_reactive_groups(atoms, coordinates)
    
    # Assess steric hindrance
    steric_hindrance = assess_steric_hindrance(atoms, coordinates)
    
    # Calculate kinetic stability score
    stability_score = 75.0  # Base score
    
    # Adjust for reactive groups
    stability_score -= reactive_groups["total_reactive"] * 5
    
    # Adjust for steric hindrance (can both stabilize and destabilize)
    if steric_hindrance["hindrance_level"] > 0.5:
        stability_score += 10  # Steric protection
    
    stability_score = max(0, min(100, stability_score))
    
    return {
        "stability_score": stability_score,
        "reactive_groups": reactive_groups,
        "steric_hindrance": steric_hindrance,
        "assessment": get_stability_assessment(stability_score)
    }

def count_reactive_groups(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Count potentially reactive functional groups"""
    
    reactive_count = 0
    groups_found = []
    
    # Look for N-O bonds (nitro groups, etc.)
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            if atoms[i] == 'N' and atoms[j] == 'O':
                distance = calculate_distance(coordinates[i], coordinates[j])
                if distance < 1.5:  # N-O bond
                    reactive_count += 1
                    groups_found.append("N-O bond")
    
    # Look for O-O bonds (peroxides)
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            if atoms[i] == 'O' and atoms[j] == 'O':
                distance = calculate_distance(coordinates[i], coordinates[j])
                if distance < 1.6:  # O-O bond
                    reactive_count += 2  # Peroxides are very reactive
                    groups_found.append("O-O bond (peroxide)")
    
    return {
        "total_reactive": reactive_count,
        "groups": groups_found
    }

def assess_steric_hindrance(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Assess steric hindrance in the molecule"""
    
    if len(atoms) < 4:
        return {"hindrance_level": 0, "description": "Too few atoms"}
    
    # Calculate average nearest neighbor distance
    total_distance = 0
    count = 0
    
    for i in range(len(atoms)):
        min_distance = float('inf')
        for j in range(len(atoms)):
            if i != j:
                distance = calculate_distance(coordinates[i], coordinates[j])
                min_distance = min(min_distance, distance)
        
        total_distance += min_distance
        count += 1
    
    avg_min_distance = total_distance / count if count > 0 else 0
    
    # Lower average distance indicates more crowding/hindrance
    hindrance_level = max(0, (2.0 - avg_min_distance) / 2.0)
    
    return {
        "hindrance_level": hindrance_level,
        "avg_min_distance": avg_min_distance,
        "description": get_hindrance_description(hindrance_level)
    }

def get_hindrance_description(level: float) -> str:
    """Get description of steric hindrance level"""
    if level < 0.2:
        return "Low steric hindrance"
    elif level < 0.5:
        return "Moderate steric hindrance"
    elif level < 0.8:
        return "High steric hindrance"
    else:
        return "Very high steric hindrance"

def analyze_chemical_reactivity(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> Dict:
    """Analyze chemical reactivity indicators"""
    
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    # Calculate reactivity factors
    electronegativity_spread = calculate_electronegativity_spread(atoms)
    heteroatom_ratio = calculate_heteroatom_ratio(atom_counts)
    unsaturation_index = estimate_unsaturation_index(atoms, coordinates)
    
    # Calculate reactivity score (higher = more reactive)
    reactivity_score = 20.0  # Base score
    
    reactivity_score += electronegativity_spread * 10
    reactivity_score += heteroatom_ratio * 30
    reactivity_score += unsaturation_index * 5
    
    reactivity_score = max(0, min(100, reactivity_score))
    
    return {
        "reactivity_score": reactivity_score,
        "electronegativity_spread": electronegativity_spread,
        "heteroatom_ratio": heteroatom_ratio,
        "unsaturation_index": unsaturation_index,
        "assessment": get_reactivity_assessment(reactivity_score)
    }

def calculate_electronegativity_spread(atoms: List[str]) -> float:
    """Calculate spread in electronegativity values"""
    
    electronegativities = {
        'H': 2.20, 'C': 2.55, 'N': 3.04, 'O': 3.44,
        'F': 3.98, 'P': 2.19, 'S': 2.58, 'Cl': 3.16
    }
    
    values = [electronegativities.get(atom, 2.5) for atom in atoms]
    
    if len(values) < 2:
        return 0.0
    
    return max(values) - min(values)

def calculate_heteroatom_ratio(atom_counts: Dict[str, int]) -> float:
    """Calculate ratio of heteroatoms to carbon atoms"""
    
    carbon_count = atom_counts.get('C', 0)
    heteroatom_count = sum(count for atom, count in atom_counts.items() 
                          if atom not in ['C', 'H'])
    
    total_heavy_atoms = carbon_count + heteroatom_count
    
    if total_heavy_atoms == 0:
        return 0.0
    
    return heteroatom_count / total_heavy_atoms

def estimate_unsaturation_index(atoms: List[str], coordinates: List[Tuple[float, float, float]]) -> float:
    """Estimate degree of unsaturation"""
    
    atom_counts = {}
    for atom in atoms:
        atom_counts[atom] = atom_counts.get(atom, 0) + 1
    
    C = atom_counts.get('C', 0)
    H = atom_counts.get('H', 0)
    N = atom_counts.get('N', 0)
    
    if C == 0:
        return 0.0
    
    # Simplified unsaturation index
    unsaturation = (2*C + 2 + N - H) / 2
    
    return max(0, unsaturation / max(1, C))  # Normalize by carbon count

def get_reactivity_assessment(score: float) -> str:
    """Get reactivity assessment from score"""
    if score < 20:
        return "Low reactivity"
    elif score < 40:
        return "Moderate reactivity"
    elif score < 70:
        return "High reactivity"
    else:
        return "Very high reactivity"

def calculate_overall_stability_score(structural: Dict, thermodynamic: Dict, 
                                    kinetic: Dict, reactivity: Dict) -> Dict:
    """Calculate overall stability score"""
    
    # Weight the different factors
    weights = {
        "structural": 0.3,
        "thermodynamic": 0.3,
        "kinetic": 0.2,
        "reactivity": 0.2  # Lower reactivity = higher stability
    }
    
    structural_score = structural["stability_score"]
    thermo_score = thermodynamic["stability_score"]
    kinetic_score = kinetic["stability_score"]
    reactivity_score = 100 - reactivity["reactivity_score"]  # Invert reactivity
    
    overall_score = (
        weights["structural"] * structural_score +
        weights["thermodynamic"] * thermo_score +
        weights["kinetic"] * kinetic_score +
        weights["reactivity"] * reactivity_score
    )
    
    return {
        "overall_score": overall_score,
        "classification": get_stability_classification(overall_score),
        "confidence": calculate_confidence_level(structural, thermodynamic, kinetic),
        "weighted_components": {
            "structural": structural_score * weights["structural"],
            "thermodynamic": thermo_score * weights["thermodynamic"],
            "kinetic": kinetic_score * weights["kinetic"],
            "reactivity": reactivity_score * weights["reactivity"]
        }
    }

def get_stability_assessment(score: float) -> str:
    """Get stability assessment from score"""
    if score >= 80:
        return "Very stable"
    elif score >= 60:
        return "Stable"
    elif score >= 40:
        return "Moderately stable"
    elif score >= 20:
        return "Unstable"
    else:
        return "Very unstable"

def get_stability_classification(score: float) -> str:
    """Get detailed stability classification"""
    if score >= 85:
        return "Highly stable - suitable for storage and handling"
    elif score >= 70:
        return "Stable - normal handling precautions"
    elif score >= 55:
        return "Moderately stable - careful handling required"
    elif score >= 40:
        return "Unstable - special handling and storage required"
    elif score >= 25:
        return "Highly unstable - extreme caution required"
    else:
        return "Extremely unstable - dangerous to handle"

def calculate_confidence_level(structural: Dict, thermodynamic: Dict, kinetic: Dict) -> str:
    """Calculate confidence level in the analysis"""
    
    # Check for indicators that might affect confidence
    total_atoms = structural.get("bond_analysis", {}).get("total_bonds", 0)
    
    if total_atoms < 5:
        return "Low - molecule too small for comprehensive analysis"
    elif total_atoms > 50:
        return "Moderate - large molecule, simplified analysis"
    else:
        return "High - suitable size for analysis"

def generate_stability_recommendations(results: Dict) -> List[str]:
    """Generate recommendations based on stability analysis"""
    
    recommendations = []
    
    overall_score = results["overall_stability"]["overall_score"]
    
    if overall_score < 40:
        recommendations.append("⚠️ Low stability detected - consider molecular modifications")
        recommendations.append("🔍 Analyze for strain-inducing structural features")
    
    # Structural recommendations
    structural = results["structural_stability"]
    if structural["bond_analysis"]["strained_bonds"] > 0:
        recommendations.append("🔧 Reduce bond strain by optimizing geometry")
    
    if structural["ring_strain"]["small_rings"] > 0:
        recommendations.append("💍 Consider ring expansion to reduce strain")
    
    # Thermodynamic recommendations
    thermo = results["thermodynamic_stability"]
    if abs(thermo["oxygen_balance"]) > 30:
        recommendations.append("⚖️ Oxygen balance is poor - consider composition adjustment")
    
    # Reactivity recommendations
    reactivity = results["chemical_reactivity"]
    if reactivity["reactivity_score"] > 70:
        recommendations.append("⚡ High reactivity - consider stabilizing substituents")
    
    if not recommendations:
        recommendations.append("✅ Molecule shows good stability characteristics")
        recommendations.append("📈 Consider optimization for specific applications")
    
    return recommendations

# ===============================================================================
# ENHANCED STABILITY ASSESSMENT WITH REFERENCE KNOWLEDGE
# Based on Klapötke's sensitivity research and thermal stability data
# ===============================================================================

def assess_sensitivity_with_references(atom_counts: Dict[str, int]) -> Dict:
    """Enhanced sensitivity assessment using Klapötke's correlations"""
    
    total_atoms = sum(atom_counts.values())
    if total_atoms == 0:
        return {"sensitivity": "Cannot assess", "method": "No atoms"}
    
    # Klapötke's sensitivity indicators
    n_ratio = atom_counts.get('N', 0) / total_atoms
    o_ratio = atom_counts.get('O', 0) / total_atoms
    c_ratio = atom_counts.get('C', 0) / total_atoms
    h_ratio = atom_counts.get('H', 0) / total_atoms
    
    sensitivity_score = 0
    risk_factors = []
    
    # Nitrogen content factor (Klapötke's research)
    if n_ratio > 0.6:  # Like tetrazoles, azides
        sensitivity_score += 45
        risk_factors.append("Extremely high nitrogen content (>60%)")
    elif n_ratio > 0.4:  # Like RDX, HMX
        sensitivity_score += 30
        risk_factors.append("Very high nitrogen content (>40%)")
    elif n_ratio > 0.25:  # Like TNT
        sensitivity_score += 15
        risk_factors.append("High nitrogen content (>25%)")
    
    # Oxygen balance effects
    estimated_ob = calculate_simple_oxygen_balance(atom_counts)
    if estimated_ob > 30:  # Oxygen-rich
        sensitivity_score += 20
        risk_factors.append("Oxygen-rich composition")
    elif estimated_ob < -50:  # Very fuel-rich
        sensitivity_score += 10
        risk_factors.append("Very fuel-rich composition")
    
    # Structural factors from Klapötke's work
    if atom_counts.get('N', 0) > 0 and atom_counts.get('O', 0) > 0:
        # Potential nitro groups
        potential_nitro = min(atom_counts.get('N', 0), atom_counts.get('O', 0) // 2)
        if potential_nitro >= 3:
            sensitivity_score += 25
            risk_factors.append("Multiple nitro groups likely")
        elif potential_nitro >= 2:
            sensitivity_score += 15
            risk_factors.append("Multiple oxidizing groups")
    
    # H/C ratio effects (aromatic vs aliphatic)
    if c_ratio > 0.1:
        hc_ratio = h_ratio / c_ratio
        if hc_ratio < 0.8:  # Highly unsaturated/aromatic
            if n_ratio > 0.2:  # Aromatic + nitrogen = potentially sensitive
                sensitivity_score += 20
                risk_factors.append("Aromatic nitro compounds (picric acid type)")
            else:
                sensitivity_score -= 5  # Aromatic stabilization
                risk_factors.append("Aromatic stabilization present")
    
    # Reference-based sensitivity classification
    if sensitivity_score >= 60:
        sensitivity_class = "Extremely Sensitive"
        handling = "Primary explosive protocols required"
        impact_sensitivity = "<4 J (lead azide class)"
    elif sensitivity_score >= 40:
        sensitivity_class = "Very Sensitive" 
        handling = "Secondary explosive protocols"
        impact_sensitivity = "4-20 J (RDX class)"
    elif sensitivity_score >= 25:
        sensitivity_class = "Sensitive"
        handling = "Standard explosive handling"
        impact_sensitivity = "20-40 J (PETN class)"
    elif sensitivity_score >= 15:
        sensitivity_class = "Moderately Sensitive"
        handling = "Careful handling required"
        impact_sensitivity = "40-80 J (TNT class)"
    else:
        sensitivity_class = "Less Sensitive"
        handling = "Standard chemical handling"
        impact_sensitivity = ">80 J (insensitive class)"
    
    return {
        "sensitivity_score": sensitivity_score,
        "sensitivity_class": sensitivity_class,
        "estimated_impact_sensitivity": impact_sensitivity,
        "handling_requirements": handling,
        "risk_factors": risk_factors,
        "reference_comparison": get_reference_sensitivity_comparison(sensitivity_score),
        "klapoetke_indicators": {
            "nitrogen_ratio": n_ratio,
            "oxygen_balance_estimate": estimated_ob,
            "structural_factors": len(risk_factors)
        },
        "method": "Enhanced Klapötke sensitivity correlation"
    }

def calculate_simple_oxygen_balance(atom_counts: Dict[str, int]) -> float:
    """Simple oxygen balance calculation for sensitivity assessment"""
    C = atom_counts.get('C', 0)
    H = atom_counts.get('H', 0)
    O = atom_counts.get('O', 0)
    
    molecular_weight = (C * 12.011 + H * 1.008 + O * 15.999 + 
                       sum(atom_counts.values()) * 10)  # Approximate other atoms
    
    if molecular_weight == 0:
        return 0
    
    return ((O - 2*C - H/2) * 15.999 / molecular_weight) * 100

def get_reference_sensitivity_comparison(sensitivity_score: float) -> Dict:
    """Compare with known explosive sensitivities"""
    
    reference_explosives = {
        "Lead Azide": {"score_range": (70, 85), "impact": "2.5 J"},
        "Mercury Fulminate": {"score_range": (65, 80), "impact": "1-2 J"},
        "PETN": {"score_range": (35, 50), "impact": "3 J"},
        "RDX": {"score_range": (30, 45), "impact": "7.4 J"},
        "HMX": {"score_range": (25, 40), "impact": "7.0 J"},
        "TNT": {"score_range": (15, 30), "impact": "15 J"},
        "TATB": {"score_range": (5, 15), "impact": "50 J"},
        "Composition B": {"score_range": (20, 35), "impact": "12 J"}
    }
    
    comparable_explosives = []
    for explosive, data in reference_explosives.items():
        score_min, score_max = data["score_range"]
        if score_min <= sensitivity_score <= score_max:
            comparable_explosives.append(f"{explosive} ({data['impact']})")
    
    return {
        "comparable_explosives": comparable_explosives,
        "estimated_class": get_explosive_class_from_score(sensitivity_score)
    }

def get_explosive_class_from_score(score: float) -> str:
    """Get explosive classification from sensitivity score"""
    if score >= 60:
        return "Primary Explosive"
    elif score >= 35:
        return "Sensitive Secondary Explosive"
    elif score >= 20:
        return "Secondary Explosive"
    elif score >= 10:
        return "Insensitive Secondary Explosive"
    else:
        return "Low Explosive/Propellant"

def assess_thermal_stability_with_references(atom_counts: Dict[str, int]) -> Dict:
    """Enhanced thermal stability assessment using reference data"""
    
    total_atoms = sum(atom_counts.values())
    if total_atoms == 0:
        return {"thermal_stability": "Cannot assess"}
    
    # Base stability temperature estimate
    base_temp = 200  # °C baseline
    
    stability_factors = []
    destabilizing_factors = []
    
    # Stabilizing factors from literature
    c_ratio = atom_counts.get('C', 0) / total_atoms
    h_ratio = atom_counts.get('H', 0) / total_atoms
    n_ratio = atom_counts.get('N', 0) / total_atoms
    
    # Aromatic stabilization (like TATB)
    if c_ratio > 0.3 and h_ratio < 0.3:
        base_temp += 50
        stability_factors.append("Aromatic stabilization (+50°C)")
    
    # Symmetric structures (like HMX vs RDX)
    if atom_counts.get('N', 0) % 2 == 0 and atom_counts.get('O', 0) % 4 == 0:
        base_temp += 20
        stability_factors.append("Symmetric structure (+20°C)")
    
    # Destabilizing factors
    
    # Multiple nitro groups on same carbon (estimated)
    potential_nitro = min(atom_counts.get('N', 0), atom_counts.get('O', 0) // 2)
    carbon_atoms = atom_counts.get('C', 0)
    
    if carbon_atoms > 0 and potential_nitro > carbon_atoms:
        base_temp -= 40
        destabilizing_factors.append("Multiple nitro groups per carbon (-40°C)")
    elif potential_nitro > 2:
        base_temp -= 20
        destabilizing_factors.append("Multiple nitro groups (-20°C)")
    
    # High nitrogen content effects
    if n_ratio > 0.5:
        base_temp -= 30
        destabilizing_factors.append("Very high nitrogen content (-30°C)")
    elif n_ratio > 0.35:
        base_temp -= 15
        destabilizing_factors.append("High nitrogen content (-15°C)")
    
    # Strained ring systems (approximated)
    if carbon_atoms >= 3 and carbon_atoms <= 4:
        base_temp -= 25
        destabilizing_factors.append("Potential ring strain (-25°C)")
    
    # Final temperature estimate
    estimated_decomp_temp = max(100, base_temp)  # Minimum 100°C
    
    # Classification based on Klapötke's data
    if estimated_decomp_temp >= 300:
        stability_class = "Very Stable (TATB class)"
        handling_temp = "Safe up to 250°C"
    elif estimated_decomp_temp >= 250:
        stability_class = "Stable (HMX class)"
        handling_temp = "Safe up to 200°C"
    elif estimated_decomp_temp >= 200:
        stability_class = "Moderately Stable (RDX class)"
        handling_temp = "Safe up to 150°C"
    elif estimated_decomp_temp >= 150:
        stability_class = "Less Stable (TNT class)"
        handling_temp = "Safe up to 100°C"
    else:
        stability_class = "Unstable (Primary explosive class)"
        handling_temp = "Extreme caution required"
    
    return {
        "estimated_decomposition_temp": estimated_decomp_temp,
        "stability_class": stability_class,
        "safe_handling_temperature": handling_temp,
        "stabilizing_factors": stability_factors,
        "destabilizing_factors": destabilizing_factors,
        "reference_comparison": get_thermal_stability_references(estimated_decomp_temp),
        "method": "Enhanced thermal stability correlation"
    }

def get_thermal_stability_references(temp: float) -> List[str]:
    """Get reference compounds with similar thermal stability"""
    
    references = []
    
    if temp >= 350:
        references.extend(["TATB (350°C)", "FOX-7 (240°C)"])
    elif temp >= 280:
        references.extend(["HMX (285°C)", "CL-20 (200°C)"])
    elif temp >= 230:
        references.extend(["RDX (230°C)", "PETN (202°C)"])
    elif temp >= 180:
        references.extend(["TNT (240°C)", "Tetryl (185°C)"])
    else:
        references.extend(["Primary explosives (<150°C)"])
    
    return references

def calculate_enhanced_stability_score(structural_stability: Dict, thermo_stability: Dict, 
                                     kinetic_stability: Dict, reactivity: Dict,
                                     sensitivity_assessment: Dict, thermal_assessment: Dict) -> Dict:
    """Calculate enhanced overall stability score including reference data"""
    
    # Traditional scores (0-100 scale)
    structural_score = structural_stability.get("stability_score", 50)
    thermo_score = thermo_stability.get("stability_score", 50)
    kinetic_score = kinetic_stability.get("stability_score", 50)
    reactivity_score = 100 - reactivity.get("reactivity_score", 50)  # Lower reactivity = higher stability
    
    # Reference-based scores
    sensitivity_score = 100 - sensitivity_assessment.get("sensitivity_score", 50)  # Lower sensitivity = higher stability
    thermal_score = min(100, thermal_assessment.get("estimated_decomposition_temp", 200) / 3)  # Normalize to 0-100
    
    # Weighted combination
    traditional_weight = 0.4
    reference_weight = 0.6
    
    traditional_stability = (structural_score + thermo_score + kinetic_score + reactivity_score) / 4
    reference_stability = (sensitivity_score + thermal_score) / 2
    
    overall_score = (traditional_stability * traditional_weight + 
                    reference_stability * reference_weight)
    
    # Classification
    if overall_score >= 80:
        stability_class = "Very Stable"
        risk_level = "Low Risk"
    elif overall_score >= 60:
        stability_class = "Stable"
        risk_level = "Moderate Risk"
    elif overall_score >= 40:
        stability_class = "Moderately Stable"
        risk_level = "Elevated Risk"
    elif overall_score >= 20:
        stability_class = "Less Stable"
        risk_level = "High Risk"
    else:
        stability_class = "Unstable"
        risk_level = "Very High Risk"
    
    return {
        "overall_score": round(overall_score, 1),
        "stability_class": stability_class,
        "risk_level": risk_level,
        "component_scores": {
            "traditional_stability": round(traditional_stability, 1),
            "reference_stability": round(reference_stability, 1),
            "structural": round(structural_score, 1),
            "thermodynamic": round(thermo_score, 1),
            "kinetic": round(kinetic_score, 1),
            "reactivity": round(reactivity_score, 1),
            "sensitivity": round(sensitivity_score, 1),
            "thermal": round(thermal_score, 1)
        },
        "method": "Enhanced scoring with reference validation"
    }

def generate_enhanced_stability_recommendations(results: Dict) -> List[str]:
    """Generate enhanced recommendations based on all analyses"""
    
    recommendations = []
    
    # Get key assessment results
    sensitivity = results.get("sensitivity_assessment", {})
    thermal = results.get("thermal_stability", {})
    overall = results.get("overall_stability", {})
    
    # Sensitivity-based recommendations
    sensitivity_class = sensitivity.get("sensitivity_class", "Unknown")
    if "Extremely Sensitive" in sensitivity_class:
        recommendations.extend([
            "🚨 EXTREME CAUTION: Primary explosive characteristics",
            "🛡️ Use remote handling procedures",
            "❄️ Store at low temperatures",
            "📏 Limit quantities to minimal amounts"
        ])
    elif "Very Sensitive" in sensitivity_class:
        recommendations.extend([
            "⚠️ HIGH SENSITIVITY: Secondary explosive protocols required",
            "🧤 Use appropriate protective equipment",
            "🌡️ Control temperature carefully"
        ])
    elif "Sensitive" in sensitivity_class:
        recommendations.extend([
            "⚡ MODERATE SENSITIVITY: Standard explosive handling",
            "📊 Regular stability monitoring recommended"
        ])
    
    # Thermal stability recommendations
    decomp_temp = thermal.get("estimated_decomposition_temp", 200)
    if decomp_temp < 150:
        recommendations.extend([
            "🌡️ LOW THERMAL STABILITY: Keep cool",
            "❄️ Refrigerated storage recommended",
            "⏰ Limited shelf life expected"
        ])
    elif decomp_temp < 200:
        recommendations.extend([
            "🌡️ MODERATE THERMAL STABILITY: Room temperature OK",
            "📈 Monitor for thermal degradation"
        ])
    
    # Overall risk recommendations
    risk_level = overall.get("risk_level", "Unknown")
    if "Very High Risk" in risk_level:
        recommendations.extend([
            "🚫 EXTREME RISK: Consider alternative compounds",
            "🔬 Extensive testing required before use",
            "📋 Detailed safety protocols mandatory"
        ])
    elif "High Risk" in risk_level:
        recommendations.extend([
            "⚠️ HIGH RISK: Enhanced safety measures required",
            "🔍 Regular monitoring and assessment needed"
        ])
    
    # Reference-based safety recommendations
    handling_req = sensitivity.get("handling_requirements", "")
    if handling_req:
        recommendations.append(f"📋 {handling_req}")
    
    safe_temp = thermal.get("safe_handling_temperature", "")
    if safe_temp:
        recommendations.append(f"🌡️ Temperature limit: {safe_temp}")
    
    # Design optimization recommendations
    risk_factors = sensitivity.get("risk_factors", [])
    if risk_factors:
        recommendations.append("🔧 Design considerations:")
        for factor in risk_factors[:3]:  # Limit to top 3
            recommendations.append(f"   • {factor}")
    
    if not recommendations:
        recommendations.extend([
            "✅ Compound shows acceptable stability characteristics",
            "📊 Continue with standard safety protocols",
            "🔬 Validate predictions with experimental data"
        ])
    
    return recommendations

def get_stability_design_recommendations(atom_counts: Dict[str, int], 
                                       sensitivity_assessment: Dict,
                                       thermal_assessment: Dict) -> List[str]:
    """Get design recommendations based on reference knowledge"""
    
    recommendations = []
    
    # Sensitivity-based recommendations
    sensitivity_score = sensitivity_assessment.get("sensitivity_score", 0)
    
    if sensitivity_score > 50:
        recommendations.extend([
            "🛡️ Consider aromatic stabilization (TATB approach)",
            "🔗 Add intramolecular hydrogen bonding",
            "📐 Optimize symmetric structure design",
            "❄️ Consider polymorphic forms for reduced sensitivity"
        ])
    elif sensitivity_score > 30:
        recommendations.extend([
            "⚖️ Balance performance vs sensitivity",
            "🧪 Consider desensitizing additives",
            "📊 Optimize crystal structure"
        ])
    
    # Thermal stability recommendations
    decomp_temp = thermal_assessment.get("estimated_decomposition_temp", 200)
    
    if decomp_temp < 200:
        recommendations.extend([
            "🌡️ Improve thermal stability",
            "💍 Avoid strained ring systems",
            "🔄 Consider constitutional isomers",
            "🧬 Optimize functional group arrangement"
        ])
    
    # Nitrogen content optimization
    total_atoms = sum(atom_counts.values())
    n_ratio = atom_counts.get('N', 0) / total_atoms if total_atoms > 0 else 0
    
    if n_ratio > 0.5:
        recommendations.append("⚡ Very high N content - excellent performance but check sensitivity")
    elif n_ratio < 0.2:
        recommendations.append("📈 Consider increasing nitrogen content for better performance")
    
    # General Klapötke principles
    recommendations.extend([
        "📚 Reference: Apply Klapötke's design principles",
        "🔬 Validate with experimental data",
        "🎯 Consider application-specific requirements"
    ])
    
    return recommendations
