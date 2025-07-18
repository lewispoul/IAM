"""
Molecular Orbitals Analysis Module
IAM Physical Chemistry Educational Tools

This module provides tools for analyzing and visualizing molecular orbitals,
HOMO-LUMO gaps, and electronic structure properties for educational purposes.

Reference: Modern Quantum Chemistry - Szabo & Ostlund
Educational framework for understanding molecular electronic structure.
"""

import numpy as np
import json
import tempfile
import os
import subprocess
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import re


@dataclass
class OrbitalData:
    """Container for molecular orbital information"""
    orbital_index: int
    energy: float
    occupation: float
    orbital_type: str  # 'alpha', 'beta', or 'restricted'
    symmetry: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MolecularOrbitalResults:
    """Container for molecular orbital analysis results"""
    success: bool
    homo_energy: float = 0.0
    lumo_energy: float = 0.0
    homo_lumo_gap: float = 0.0
    total_energy: float = 0.0
    dipole_moment: float = 0.0
    orbitals: List[OrbitalData] = None
    visualization_data: Dict[str, Any] = None
    method: str = "xtb"
    error: str = ""
    educational_analysis: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.orbitals is None:
            self.orbitals = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['orbitals'] = [orbital.to_dict() for orbital in self.orbitals]
        return result


class MolecularOrbitalAnalyzer:
    """
    Analyze and visualize molecular orbitals and electronic structure
    
    Educational features:
    - HOMO/LUMO analysis and visualization
    - Energy gap calculations and interpretation
    - Orbital symmetry analysis
    - Electronic structure visualization
    - Reactivity predictions based on frontier orbitals
    """
    
    def __init__(self, work_dir: str = None):
        """
        Initialize the molecular orbital analyzer
        
        Args:
            work_dir: Working directory for calculations (default: temp)
        """
        self.work_dir = work_dir or tempfile.gettempdir()
        self.last_results = None
        
        # Orbital visualization colors (standard chemistry colors)
        self.orbital_colors = {
            'homo': '#FF4444',      # Red for HOMO
            'lumo': '#4444FF',      # Blue for LUMO
            'occupied': '#44AA44',  # Green for occupied
            'virtual': '#FFAA44',   # Orange for virtual
            'core': '#666666'       # Gray for core orbitals
        }
    
    def analyze_from_xyz(self, xyz_content: str, method: str = "xtb",
                        charge: int = 0, multiplicity: int = 1,
                        include_orbitals: bool = True) -> MolecularOrbitalResults:
        """
        Analyze molecular orbitals from XYZ coordinates
        
        Args:
            xyz_content: XYZ format molecular coordinates
            method: Calculation method ("xtb", "xtb-gfn1", "xtb-gfn2")
            charge: Molecular charge
            multiplicity: Spin multiplicity
            include_orbitals: Whether to include detailed orbital data
            
        Returns:
            MolecularOrbitalResults object with analysis data
        """
        try:
            # Validate input
            if not xyz_content.strip():
                return MolecularOrbitalResults(
                    success=False, 
                    error="Empty XYZ coordinates provided"
                )
            
            # Parse XYZ to extract coordinates
            coordinates = self._parse_xyz(xyz_content)
            if not coordinates:
                return MolecularOrbitalResults(
                    success=False,
                    error="Invalid XYZ format"
                )
            
            # Run quantum calculation with orbital analysis
            calc_results = self._run_xtb_orbital_calculation(
                xyz_content, method, charge, multiplicity, include_orbitals
            )
            
            if not calc_results["success"]:
                return MolecularOrbitalResults(
                    success=False,
                    error=f"XTB calculation failed: {calc_results.get('error', 'Unknown error')}"
                )
            
            # Analyze orbital data
            orbital_analysis = self._analyze_orbital_data(calc_results)
            
            # Generate visualization data
            viz_data = self._prepare_orbital_visualization(coordinates, orbital_analysis)
            
            # Educational analysis
            educational_content = self._generate_educational_analysis(orbital_analysis)
            
            # Create results object
            results = MolecularOrbitalResults(
                success=True,
                homo_energy=orbital_analysis["homo_energy"],
                lumo_energy=orbital_analysis["lumo_energy"],
                homo_lumo_gap=orbital_analysis["homo_lumo_gap"],
                total_energy=orbital_analysis["total_energy"],
                dipole_moment=orbital_analysis.get("dipole_moment", 0.0),
                orbitals=orbital_analysis["orbitals"],
                visualization_data=viz_data,
                method=method,
                educational_analysis=educational_content
            )
            
            self.last_results = results
            return results
            
        except Exception as e:
            return MolecularOrbitalResults(
                success=False,
                error=f"Orbital analysis error: {str(e)}"
            )
    
    def analyze_from_smiles(self, smiles: str, method: str = "xtb") -> MolecularOrbitalResults:
        """
        Analyze molecular orbitals from SMILES string
        
        Args:
            smiles: SMILES representation of molecule
            method: Calculation method
            
        Returns:
            MolecularOrbitalResults object
        """
        try:
            # Convert SMILES to XYZ using RDKit if available
            try:
                from rdkit import Chem
                from rdkit.Chem import AllChem
                
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    return MolecularOrbitalResults(
                        success=False,
                        error="Invalid SMILES string"
                    )
                
                mol = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol, randomSeed=42)
                AllChem.MMFFOptimizeMolecule(mol)
                
                # Convert to XYZ
                xyz_content = self._mol_to_xyz(mol)
                
            except ImportError:
                return MolecularOrbitalResults(
                    success=False,
                    error="RDKit not available for SMILES conversion"
                )
            
            return self.analyze_from_xyz(xyz_content, method)
            
        except Exception as e:
            return MolecularOrbitalResults(
                success=False,
                error=f"SMILES conversion error: {str(e)}"
            )
    
    def _parse_xyz(self, xyz_content: str) -> List[Tuple[str, float, float, float]]:
        """Parse XYZ coordinates from string"""
        try:
            lines = xyz_content.strip().split('\n')
            if len(lines) < 3:
                return []
            
            n_atoms = int(lines[0])
            coordinates = []
            
            for i in range(2, 2 + n_atoms):
                if i >= len(lines):
                    break
                
                parts = lines[i].split()
                if len(parts) >= 4:
                    element = parts[0]
                    x, y, z = map(float, parts[1:4])
                    coordinates.append((element, x, y, z))
            
            return coordinates
            
        except (ValueError, IndexError):
            return []
    
    def _run_xtb_orbital_calculation(self, xyz_content: str, method: str,
                                   charge: int, multiplicity: int,
                                   include_orbitals: bool) -> Dict:
        """Run XTB calculation with orbital analysis"""
        
        # Create temporary XYZ file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write(xyz_content)
            xyz_file = f.name
        
        try:
            # Prepare XTB command for orbital analysis
            xtb_method = method.replace("xtb-", "").replace("xtb", "gfn2")
            
            cmd = [
                'xtb', xyz_file,
                '--opt', 'normal',
                '--chrg', str(charge),
                '--uhf', str(multiplicity - 1),
                '--gfn', xtb_method[-1] if xtb_method in ['gfn1', 'gfn2'] else '2',
                '--verbose'
            ]
            
            # Add orbital output if requested
            if include_orbitals:
                cmd.extend(['--molden', '--wbo'])  # Generate orbital file and bond orders
            
            # Run calculation
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.work_dir,
                timeout=180  # Increased timeout for orbital calculations
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"XTB failed: {result.stderr}"
                }
            
            # Parse output and orbital files
            parsed_results = self._parse_xtb_orbital_output(result.stdout, self.work_dir)
            
            return parsed_results
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "XTB orbital calculation timed out"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "XTB not found. Please install xtb: conda install -c conda-forge xtb"
            }
        finally:
            # Cleanup temporary files
            if os.path.exists(xyz_file):
                os.unlink(xyz_file)
    
    def _parse_xtb_orbital_output(self, output: str, work_dir: str) -> Dict:
        """Parse XTB output to extract orbital information"""
        try:
            lines = output.split('\n')
            results = {"success": True, "orbitals_data": []}
            
            # Parse main energy values
            for line in lines:
                line = line.strip()
                
                # Total energy
                if 'TOTAL ENERGY' in line:
                    try:
                        energy = float(line.split()[-2])
                        results['total_energy'] = energy
                    except (ValueError, IndexError):
                        pass
                
                # HOMO-LUMO gap
                elif 'HOMO-LUMO GAP' in line:
                    try:
                        gap_eV = float(line.split()[-2])
                        results['homo_lumo_gap_eV'] = gap_eV
                        results['homo_lumo_gap_hartree'] = gap_eV / 27.2114  # Convert to Hartree
                    except (ValueError, IndexError):
                        pass
                
                # Dipole moment
                elif 'Mol. dipole' in line:
                    try:
                        dipole = float(line.split()[-2])
                        results['dipole_moment'] = dipole
                    except (ValueError, IndexError):
                        pass
                
                # Frontier orbital energies (if present)
                elif 'HOMO' in line and 'eV' in line:
                    try:
                        homo_eV = float(re.search(r'HOMO.*?(-?\d+\.?\d*)', line).group(1))
                        results['homo_energy_eV'] = homo_eV
                        results['homo_energy_hartree'] = homo_eV / 27.2114
                    except (AttributeError, ValueError):
                        pass
                
                elif 'LUMO' in line and 'eV' in line:
                    try:
                        lumo_eV = float(re.search(r'LUMO.*?(-?\d+\.?\d*)', line).group(1))
                        results['lumo_energy_eV'] = lumo_eV
                        results['lumo_energy_hartree'] = lumo_eV / 27.2114
                    except (AttributeError, ValueError):
                        pass
            
            # Try to read orbital file if generated
            orbital_file = os.path.join(work_dir, 'molden.input')
            if os.path.exists(orbital_file):
                orbital_data = self._parse_molden_file(orbital_file)
                results.update(orbital_data)
                # Cleanup
                os.unlink(orbital_file)
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse XTB orbital output: {str(e)}"
            }
    
    def _parse_molden_file(self, molden_file: str) -> Dict:
        """Parse Molden file to extract detailed orbital information"""
        try:
            with open(molden_file, 'r') as f:
                content = f.read()
            
            orbital_data = {"detailed_orbitals": []}
            
            # Parse molecular orbital section
            if '[MO]' in content:
                mo_section = content.split('[MO]')[1]
                orbital_blocks = mo_section.split('Sym=')
                
                for i, block in enumerate(orbital_blocks[1:], 1):  # Skip first empty block
                    try:
                        lines = block.strip().split('\n')
                        
                        # Extract orbital properties
                        symmetry = lines[0].split()[0] if lines else "unknown"
                        
                        energy = None
                        occupation = None
                        
                        for line in lines[:10]:  # Check first few lines for energy/occupation
                            if 'Ene=' in line:
                                energy = float(line.split('Ene=')[1].split()[0])
                            elif 'Occup=' in line:
                                occupation = float(line.split('Occup=')[1].split()[0])
                        
                        if energy is not None and occupation is not None:
                            orbital_data["detailed_orbitals"].append({
                                "index": i,
                                "energy": energy,
                                "occupation": occupation,
                                "symmetry": symmetry
                            })
                    
                    except (ValueError, IndexError):
                        continue
            
            return orbital_data
            
        except Exception as e:
            return {"orbital_parse_error": str(e)}
    
    def _analyze_orbital_data(self, calc_results: Dict) -> Dict:
        """Analyze orbital data to extract key information"""
        
        # Basic energy data
        total_energy = calc_results.get('total_energy', 0.0)
        gap_hartree = calc_results.get('homo_lumo_gap_hartree', 0.0)
        gap_eV = calc_results.get('homo_lumo_gap_eV', 0.0)
        dipole = calc_results.get('dipole_moment', 0.0)
        
        # Orbital energies
        homo_hartree = calc_results.get('homo_energy_hartree', 0.0)
        lumo_hartree = calc_results.get('lumo_energy_hartree', 0.0)
        
        # Process detailed orbitals if available
        orbitals = []
        detailed_orbitals = calc_results.get('detailed_orbitals', [])
        
        for orbital_data in detailed_orbitals:
            orbital_type = 'occupied' if orbital_data['occupation'] > 0.1 else 'virtual'
            
            orbitals.append(OrbitalData(
                orbital_index=orbital_data['index'],
                energy=orbital_data['energy'],
                occupation=orbital_data['occupation'],
                orbital_type=orbital_type,
                symmetry=orbital_data.get('symmetry', 'unknown')
            ))
        
        # If no detailed orbitals, create simplified HOMO/LUMO representation
        if not orbitals and homo_hartree != 0.0:
            orbitals = [
                OrbitalData(
                    orbital_index=-1,  # HOMO
                    energy=homo_hartree,
                    occupation=2.0,
                    orbital_type='occupied',
                    symmetry='HOMO'
                ),
                OrbitalData(
                    orbital_index=0,   # LUMO
                    energy=lumo_hartree,
                    occupation=0.0,
                    orbital_type='virtual',
                    symmetry='LUMO'
                )
            ]
        
        return {
            "total_energy": total_energy,
            "homo_energy": homo_hartree,
            "lumo_energy": lumo_hartree,
            "homo_lumo_gap": gap_hartree,
            "homo_lumo_gap_eV": gap_eV,
            "dipole_moment": dipole,
            "orbitals": orbitals,
            "n_electrons": sum(orbital.occupation for orbital in orbitals if orbital.occupation > 0),
            "n_orbitals": len(orbitals)
        }
    
    def _prepare_orbital_visualization(self, coordinates: List[Tuple], 
                                     orbital_analysis: Dict) -> Dict:
        """Prepare data for orbital visualization"""
        
        # Energy level diagram data
        orbitals = orbital_analysis["orbitals"]
        
        # Sort orbitals by energy
        sorted_orbitals = sorted(orbitals, key=lambda x: x.energy)
        
        # Prepare energy level diagram
        energy_levels = []
        for orbital in sorted_orbitals:
            color = self._get_orbital_color(orbital)
            
            energy_levels.append({
                "energy": orbital.energy,
                "occupation": orbital.occupation,
                "type": orbital.orbital_type,
                "color": color,
                "label": f"Orbital {orbital.orbital_index}",
                "symmetry": orbital.symmetry
            })
        
        # HOMO-LUMO gap visualization
        homo_lumo_data = self._prepare_homo_lumo_diagram(orbital_analysis)
        
        # Molecular structure for overlay
        molecule_data = {
            "coordinates": coordinates,
            "bonds": self._estimate_bonds(coordinates)
        }
        
        # Educational diagrams
        educational_plots = self._prepare_educational_plots(orbital_analysis)
        
        visualization_data = {
            "energy_levels": energy_levels,
            "homo_lumo_diagram": homo_lumo_data,
            "molecule": molecule_data,
            "educational_plots": educational_plots,
            "orbital_colors": self.orbital_colors
        }
        
        return visualization_data
    
    def _get_orbital_color(self, orbital: OrbitalData) -> str:
        """Get appropriate color for orbital visualization"""
        if orbital.symmetry == 'HOMO':
            return self.orbital_colors['homo']
        elif orbital.symmetry == 'LUMO':
            return self.orbital_colors['lumo']
        elif orbital.occupation > 0.1:
            return self.orbital_colors['occupied']
        else:
            return self.orbital_colors['virtual']
    
    def _prepare_homo_lumo_diagram(self, orbital_analysis: Dict) -> Dict:
        """Prepare HOMO-LUMO gap diagram data"""
        
        homo_energy = orbital_analysis["homo_energy"]
        lumo_energy = orbital_analysis["lumo_energy"]
        gap_eV = orbital_analysis["homo_lumo_gap_eV"]
        
        return {
            "homo": {
                "energy": homo_energy,
                "energy_eV": homo_energy * 27.2114,
                "label": "HOMO",
                "color": self.orbital_colors['homo']
            },
            "lumo": {
                "energy": lumo_energy,
                "energy_eV": lumo_energy * 27.2114,
                "label": "LUMO",
                "color": self.orbital_colors['lumo']
            },
            "gap": {
                "value_hartree": orbital_analysis["homo_lumo_gap"],
                "value_eV": gap_eV,
                "interpretation": self._interpret_homo_lumo_gap(gap_eV)
            }
        }
    
    def _interpret_homo_lumo_gap(self, gap_eV: float) -> str:
        """Provide educational interpretation of HOMO-LUMO gap"""
        if gap_eV < 1.0:
            return "Très petit gap - Conducteur métallique ou semi-conducteur"
        elif gap_eV < 3.0:
            return "Gap modéré - Semi-conducteur, photoactivité possible"
        elif gap_eV < 5.0:
            return "Gap moyen - Molécule stable, réactivité modérée"
        elif gap_eV < 8.0:
            return "Grand gap - Molécule très stable, faible réactivité"
        else:
            return "Gap très grand - Molécule extrêmement stable, quasi-inerte"
    
    def _estimate_bonds(self, coordinates: List[Tuple]) -> List[Tuple[int, int]]:
        """Estimate molecular bonds based on distances"""
        bonds = []
        
        # Bond distance thresholds (Angstroms)
        bond_thresholds = {
            ('H', 'H'): 1.0, ('H', 'C'): 1.3, ('H', 'N'): 1.2, ('H', 'O'): 1.1,
            ('C', 'C'): 1.8, ('C', 'N'): 1.6, ('C', 'O'): 1.5,
            ('N', 'N'): 1.6, ('N', 'O'): 1.5, ('O', 'O'): 1.6
        }
        
        for i, (elem1, x1, y1, z1) in enumerate(coordinates):
            for j, (elem2, x2, y2, z2) in enumerate(coordinates[i+1:], i+1):
                distance = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
                
                # Get bond threshold
                pair = tuple(sorted([elem1, elem2]))
                threshold = bond_thresholds.get(pair, 2.0)  # Default threshold
                
                if distance < threshold:
                    bonds.append((i, j))
        
        return bonds
    
    def _prepare_educational_plots(self, orbital_analysis: Dict) -> Dict:
        """Prepare educational visualization data"""
        
        gap_eV = orbital_analysis["homo_lumo_gap_eV"]
        
        # Reactivity prediction based on frontier orbitals
        nucleophilicity = max(0, 10 - abs(orbital_analysis["homo_energy"] * 27.2114))
        electrophilicity = max(0, abs(orbital_analysis["lumo_energy"] * 27.2114))
        
        return {
            "reactivity_radar": {
                "nucleophilicity": nucleophilicity,
                "electrophilicity": electrophilicity,
                "stability": min(gap_eV * 2, 10),
                "polarizability": max(0, 10 - gap_eV),
                "hardness": gap_eV
            },
            "gap_comparison": {
                "this_molecule": gap_eV,
                "typical_ranges": {
                    "metals": 0.0,
                    "semiconductors": 1.5,
                    "insulators": 5.0,
                    "noble_gases": 15.0
                }
            }
        }
    
    def _generate_educational_analysis(self, orbital_analysis: Dict) -> Dict:
        """Generate educational analysis and explanations"""
        
        gap_eV = orbital_analysis["homo_lumo_gap_eV"]
        homo_energy = orbital_analysis["homo_energy"] * 27.2114  # Convert to eV
        lumo_energy = orbital_analysis["lumo_energy"] * 27.2114
        
        return {
            "frontier_orbital_analysis": {
                "homo_character": self._analyze_homo_character(homo_energy),
                "lumo_character": self._analyze_lumo_character(lumo_energy),
                "gap_significance": self._interpret_homo_lumo_gap(gap_eV)
            },
            "reactivity_predictions": {
                "nucleophilic_sites": "HOMO domine - sites riches en électrons",
                "electrophilic_sites": "LUMO domine - sites pauvres en électrons",
                "overall_reactivity": self._predict_reactivity(gap_eV)
            },
            "learning_objectives": [
                "Comprendre l'origine des orbitales moléculaires",
                "Interpréter le gap HOMO-LUMO",
                "Prédire la réactivité chimique",
                "Visualiser la structure électronique"
            ],
            "key_concepts": {
                "frontier_orbitals": "HOMO et LUMO contrôlent la réactivité chimique",
                "gap_energy": "Plus le gap est petit, plus la molécule est réactive",
                "orbital_symmetry": "La symétrie détermine les interactions permises",
                "electron_density": "La densité électronique guide les attaques chimiques"
            }
        }
    
    def _analyze_homo_character(self, homo_eV: float) -> str:
        """Analyze HOMO energy character"""
        if homo_eV > -3.0:
            return "HOMO très haut - Excellent donneur d'électrons"
        elif homo_eV > -6.0:
            return "HOMO modéré - Bon donneur d'électrons"
        elif homo_eV > -9.0:
            return "HOMO bas - Donneur d'électrons faible"
        else:
            return "HOMO très bas - Donneur d'électrons très faible"
    
    def _analyze_lumo_character(self, lumo_eV: float) -> str:
        """Analyze LUMO energy character"""
        if lumo_eV < -1.0:
            return "LUMO très bas - Excellent accepteur d'électrons"
        elif lumo_eV < 1.0:
            return "LUMO modéré - Bon accepteur d'électrons"
        elif lumo_eV < 3.0:
            return "LUMO haut - Accepteur d'électrons faible"
        else:
            return "LUMO très haut - Accepteur d'électrons très faible"
    
    def _predict_reactivity(self, gap_eV: float) -> str:
        """Predict overall molecular reactivity"""
        if gap_eV < 2.0:
            return "Très réactif - Réactions faciles dans conditions douces"
        elif gap_eV < 4.0:
            return "Modérément réactif - Réactions dans conditions normales"
        elif gap_eV < 6.0:
            return "Peu réactif - Réactions nécessitent activation"
        else:
            return "Très stable - Réactions difficiles, conditions drastiques"
    
    def _mol_to_xyz(self, mol) -> str:
        """Convert RDKit molecule to XYZ format"""
        try:
            conf = mol.GetConformer()
            n_atoms = mol.GetNumAtoms()
            
            xyz_lines = [str(n_atoms), "Generated by IAM Molecular Orbital Analyzer"]
            
            for i in range(n_atoms):
                atom = mol.GetAtomWithIdx(i)
                pos = conf.GetAtomPosition(i)
                symbol = atom.GetSymbol()
                
                xyz_lines.append(f"{symbol:2s} {pos.x:12.6f} {pos.y:12.6f} {pos.z:12.6f}")
            
            return "\n".join(xyz_lines)
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert molecule to XYZ: {str(e)}")
    
    def get_theory_explanation(self) -> str:
        """Get formatted theory explanation for display"""
        return """
# Orbitales Moléculaires - Base Théorique

## Introduction
Les orbitales moléculaires résultent de la combinaison linéaire des orbitales atomiques (LCAO). 
Elles décrivent la distribution de probabilité des électrons dans une molécule.

## Concepts Clés

### HOMO et LUMO
- **HOMO** (Highest Occupied Molecular Orbital) : Orbitale occupée la plus haute en énergie
- **LUMO** (Lowest Unoccupied Molecular Orbital) : Orbitale virtuelle la plus basse en énergie
- **Gap HOMO-LUMO** : Différence d'énergie entre HOMO et LUMO

### Signification du Gap
- **Gap petit** (< 3 eV) : Molécule réactive, transitions électroniques faciles
- **Gap moyen** (3-6 eV) : Stabilité modérée, réactivité normale
- **Gap grand** (> 6 eV) : Molécule très stable, peu réactive

### Théorie des Orbitales Frontières
Les orbitales HOMO et LUMO contrôlent la réactivité chimique :
- **HOMO** : Site de donation d'électrons (nucléophile)
- **LUMO** : Site d'acceptation d'électrons (électrophile)

## Applications
- Prédiction de la réactivité chimique
- Design de matériaux électroniques
- Compréhension des propriétés optiques
- Analyse de la stabilité moléculaire

## Références
- Fukui, K. (1982) - Théorie des orbitales frontières (Prix Nobel)
- Woodward-Hoffmann - Règles de conservation de symétrie orbitalaire
- Szabo & Ostlund - Modern Quantum Chemistry
"""
