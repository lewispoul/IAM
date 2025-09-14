"""
Advanced Molecular Orbitals Visualizer
IAM Physical Chemistry Educational Tools - Enhanced Version

This module provides advanced orbital visualization capabilities including
isosurface rendering, orbital density plots, and enhanced educational content.
"""

import numpy as np
import json
import tempfile
import os
import subprocess
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import re
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Import base module
from .molecular_orbitals import MolecularOrbitalAnalyzer, MolecularOrbitalResults, OrbitalData


@dataclass
class EnhancedOrbitalData:
    """Enhanced orbital data with visualization information"""
    orbital_index: int
    energy: float
    occupation: float
    orbital_type: str
    symmetry: Optional[str] = None
    coefficients: Optional[List[float]] = None
    isosurface_data: Optional[Dict] = None
    density_plot: Optional[str] = None  # Base64 encoded plot
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EnhancedOrbitalResults:
    """Enhanced results with advanced visualization data"""
    success: bool
    homo_energy: float = 0.0
    lumo_energy: float = 0.0
    homo_lumo_gap: float = 0.0
    total_energy: float = 0.0
    dipole_moment: float = 0.0
    orbitals: List[EnhancedOrbitalData] = None
    visualization_data: Dict[str, Any] = None
    educational_analysis: Dict[str, Any] = None
    orbital_isosurfaces: Dict[str, Any] = None
    density_plots: Dict[str, str] = None  # Base64 encoded plots
    comparison_data: Dict[str, Any] = None
    method: str = "xtb"
    error: str = ""
    
    def __post_init__(self):
        if self.orbitals is None:
            self.orbitals = []
        if self.orbital_isosurfaces is None:
            self.orbital_isosurfaces = {}
        if self.density_plots is None:
            self.density_plots = {}
        if self.comparison_data is None:
            self.comparison_data = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['orbitals'] = [orbital.to_dict() for orbital in self.orbitals]
        return result


class EnhancedMolecularOrbitalAnalyzer(MolecularOrbitalAnalyzer):
    """
    Enhanced molecular orbital analyzer with advanced visualization capabilities
    
    New features:
    - Orbital isosurface generation
    - Density plots and contour maps
    - Enhanced educational content
    - Molecular comparisons
    - Export capabilities
    """
    
    def __init__(self, work_dir: str = None, cache_enabled: bool = True):
        """
        Initialize the enhanced analyzer
        
        Args:
            work_dir: Working directory for calculations
            cache_enabled: Enable caching of calculation results
        """
        super().__init__(work_dir)
        self.cache_enabled = cache_enabled
        self.cache_dir = os.path.join(self.work_dir, 'orbital_cache')
        if cache_enabled and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Enhanced visualization settings
        self.isosurface_values = [0.02, 0.05, 0.1]  # Different isosurface levels
        self.plot_settings = {
            'dpi': 150,
            'figsize': (10, 8),
            'colormap': 'RdYlBu_r',
            'style': 'seaborn-v0_8'
        }
    
    def analyze_with_enhancements(self, xyz_content: str, method: str = "xtb",
                                charge: int = 0, multiplicity: int = 1,
                                generate_isosurfaces: bool = True,
                                generate_density_plots: bool = True,
                                compare_molecules: List[str] = None) -> EnhancedOrbitalResults:
        """
        Enhanced analysis with advanced visualization
        
        Args:
            xyz_content: XYZ format molecular coordinates
            method: Calculation method
            charge: Molecular charge
            multiplicity: Spin multiplicity
            generate_isosurfaces: Generate 3D isosurface data
            generate_density_plots: Generate 2D density plots
            compare_molecules: List of molecules for comparison
            
        Returns:
            EnhancedOrbitalResults with advanced visualization data
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(xyz_content, method, charge, multiplicity)
            cached_result = self._load_from_cache(cache_key) if self.cache_enabled else None
            
            if cached_result:
                print("📋 Using cached orbital analysis results")
                return cached_result
            
            # Run base analysis
            base_results = self.analyze_from_xyz(
                xyz_content, method, charge, multiplicity, include_orbitals=True
            )
            
            if not base_results.success:
                return EnhancedOrbitalResults(
                    success=False,
                    error=base_results.error
                )
            
            # Parse coordinates for advanced visualization
            coordinates = self._parse_xyz(xyz_content)
            if not coordinates:
                return EnhancedOrbitalResults(
                    success=False,
                    error="Invalid XYZ coordinates for enhanced analysis"
                )
            
            # Enhanced orbital analysis
            enhanced_orbitals = self._create_enhanced_orbitals(base_results.orbitals)
            
            # Generate advanced visualizations
            isosurface_data = {}
            density_plots = {}
            
            if generate_isosurfaces:
                isosurface_data = self._generate_orbital_isosurfaces(
                    coordinates, enhanced_orbitals
                )
            
            if generate_density_plots:
                density_plots = self._generate_density_plots(
                    coordinates, enhanced_orbitals
                )
            
            # Enhanced educational analysis
            enhanced_education = self._generate_enhanced_educational_content(
                base_results, coordinates
            )
            
            # Molecular comparisons
            comparison_data = {}
            if compare_molecules:
                comparison_data = self._generate_molecular_comparisons(
                    base_results, compare_molecules
                )
            
            # Create enhanced results
            enhanced_results = EnhancedOrbitalResults(
                success=True,
                homo_energy=base_results.homo_energy,
                lumo_energy=base_results.lumo_energy,
                homo_lumo_gap=base_results.homo_lumo_gap,
                total_energy=base_results.total_energy,
                dipole_moment=base_results.dipole_moment,
                orbitals=enhanced_orbitals,
                visualization_data=base_results.visualization_data,
                educational_analysis=enhanced_education,
                orbital_isosurfaces=isosurface_data,
                density_plots=density_plots,
                comparison_data=comparison_data,
                method=method
            )
            
            # Cache results
            if self.cache_enabled:
                self._save_to_cache(cache_key, enhanced_results)
            
            return enhanced_results
            
        except Exception as e:
            return EnhancedOrbitalResults(
                success=False,
                error=f"Enhanced orbital analysis error: {str(e)}"
            )
    
    def _create_enhanced_orbitals(self, base_orbitals: List[OrbitalData]) -> List[EnhancedOrbitalData]:
        """Convert base orbitals to enhanced orbitals with additional data"""
        enhanced_orbitals = []
        
        for orbital in base_orbitals:
            enhanced_orbital = EnhancedOrbitalData(
                orbital_index=orbital.orbital_index,
                energy=orbital.energy,
                occupation=orbital.occupation,
                orbital_type=orbital.orbital_type,
                symmetry=orbital.symmetry,
                coefficients=self._generate_mock_coefficients(),  # Would be real from quantum calculation
                isosurface_data=None,  # Will be filled later
                density_plot=None      # Will be filled later
            )
            enhanced_orbitals.append(enhanced_orbital)
        
        return enhanced_orbitals
    
    def _generate_mock_coefficients(self) -> List[float]:
        """Generate mock orbital coefficients for demonstration"""
        # In real implementation, these would come from the quantum calculation
        n_basis = np.random.randint(20, 100)
        coefficients = np.random.normal(0, 0.5, n_basis)
        # Normalize
        coefficients = coefficients / np.linalg.norm(coefficients)
        return coefficients.tolist()
    
    def _generate_orbital_isosurfaces(self, coordinates: List[Tuple], 
                                    orbitals: List[EnhancedOrbitalData]) -> Dict[str, Any]:
        """Generate 3D isosurface data for orbital visualization"""
        isosurface_data = {}
        
        # Focus on HOMO and LUMO for now
        homo_orbital = next((orb for orb in orbitals if orb.symmetry == 'HOMO'), None)
        lumo_orbital = next((orb for orb in orbitals if orb.symmetry == 'LUMO'), None)
        
        key_orbitals = {}
        if homo_orbital:
            key_orbitals['HOMO'] = homo_orbital
        if lumo_orbital:
            key_orbitals['LUMO'] = lumo_orbital
        
        for orbital_name, orbital in key_orbitals.items():
            try:
                # Generate mock 3D grid for orbital density
                grid_size = 32
                x_range = np.linspace(-5, 5, grid_size)
                y_range = np.linspace(-5, 5, grid_size)
                z_range = np.linspace(-5, 5, grid_size)
                
                X, Y, Z = np.meshgrid(x_range, y_range, z_range)
                
                # Mock orbital density calculation
                # In real implementation, this would be calculated from basis functions
                orbital_density = self._calculate_mock_orbital_density(
                    X, Y, Z, coordinates, orbital.coefficients
                )
                
                # Generate isosurface data for different levels
                isosurfaces = {}
                for iso_value in self.isosurface_values:
                    isosurfaces[f'iso_{iso_value}'] = {
                        'value': iso_value,
                        'vertices': self._extract_isosurface_vertices(orbital_density, iso_value),
                        'color': self.orbital_colors.get(orbital_name.lower(), '#FF0000')
                    }
                
                isosurface_data[orbital_name] = {
                    'orbital_index': orbital.orbital_index,
                    'energy': orbital.energy,
                    'isosurfaces': isosurfaces,
                    'grid_info': {
                        'size': grid_size,
                        'x_range': [x_range[0], x_range[-1]],
                        'y_range': [y_range[0], y_range[-1]],
                        'z_range': [z_range[0], z_range[-1]]
                    }
                }
                
            except Exception as e:
                print(f"Warning: Failed to generate isosurface for {orbital_name}: {e}")
                continue
        
        return isosurface_data
    
    def _calculate_mock_orbital_density(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                                      coordinates: List[Tuple], coefficients: List[float]) -> np.ndarray:
        """Calculate mock orbital density on 3D grid"""
        density = np.zeros_like(X)
        
        # Simple Gaussian-based mock calculation
        for i, (element, x0, y0, z0) in enumerate(coordinates):
            # Atomic contribution to orbital
            coeff = coefficients[i % len(coefficients)] if coefficients else 1.0
            sigma = 1.0  # Gaussian width
            
            r_squared = (X - x0)**2 + (Y - y0)**2 + (Z - z0)**2
            atomic_contribution = coeff * np.exp(-r_squared / (2 * sigma**2))
            density += atomic_contribution
        
        # Add some orbital character (p-orbital like lobes)
        if len(coordinates) > 1:
            # Simple p-orbital approximation
            density *= Z  # Give it some directional character
        
        return density
    
    def _extract_isosurface_vertices(self, density: np.ndarray, iso_value: float) -> List[List[float]]:
        """Extract vertices for isosurface at given value"""
        # This is a simplified version - real implementation would use marching cubes
        vertices = []
        
        # Find approximate isosurface points
        threshold_mask = np.abs(density - iso_value) < 0.01
        indices = np.where(threshold_mask)
        
        # Sample vertices (limit to reasonable number)
        max_vertices = 1000
        step = max(1, len(indices[0]) // max_vertices)
        
        for i in range(0, len(indices[0]), step):
            x_idx, y_idx, z_idx = indices[0][i], indices[1][i], indices[2][i]
            # Convert indices to actual coordinates
            x = -5 + (x_idx / density.shape[0]) * 10
            y = -5 + (y_idx / density.shape[1]) * 10
            z = -5 + (z_idx / density.shape[2]) * 10
            vertices.append([float(x), float(y), float(z)])
        
        return vertices
    
    def _generate_density_plots(self, coordinates: List[Tuple],
                              orbitals: List[EnhancedOrbitalData]) -> Dict[str, str]:
        """Generate 2D density plots for key orbitals"""
        density_plots = {}
        
        try:
            plt.style.use(self.plot_settings['style'])
        except:
            pass  # Fallback if style not available
        
        # Focus on HOMO and LUMO
        key_orbitals = {
            'HOMO': next((orb for orb in orbitals if orb.symmetry == 'HOMO'), None),
            'LUMO': next((orb for orb in orbitals if orb.symmetry == 'LUMO'), None)
        }
        
        for orbital_name, orbital in key_orbitals.items():
            if orbital is None:
                continue
                
            try:
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
                    2, 2, figsize=self.plot_settings['figsize'], 
                    dpi=self.plot_settings['dpi']
                )
                
                # Generate 2D slices of orbital density
                self._plot_orbital_slice(ax1, coordinates, orbital, 'XY', z=0)
                self._plot_orbital_slice(ax2, coordinates, orbital, 'XZ', y=0)
                self._plot_orbital_slice(ax3, coordinates, orbital, 'YZ', x=0)
                
                # Radial distribution
                self._plot_radial_distribution(ax4, coordinates, orbital)
                
                plt.suptitle(f'{orbital_name} Orbital Analysis\nEnergy: {orbital.energy * 27.2114:.2f} eV', 
                           fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', 
                           dpi=self.plot_settings['dpi'])
                buffer.seek(0)
                plot_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                density_plots[orbital_name] = plot_base64
                
                plt.close(fig)
                
            except Exception as e:
                print(f"Warning: Failed to generate density plot for {orbital_name}: {e}")
                continue
        
        return density_plots
    
    def _plot_orbital_slice(self, ax, coordinates: List[Tuple], orbital: EnhancedOrbitalData,
                          plane: str, **slice_params):
        """Plot 2D slice of orbital density"""
        # Generate 2D grid for the specified plane
        grid_size = 50
        extent = 5  # Angstroms
        
        if plane == 'XY':
            x_range = np.linspace(-extent, extent, grid_size)
            y_range = np.linspace(-extent, extent, grid_size)
            X, Y = np.meshgrid(x_range, y_range)
            Z = np.full_like(X, slice_params.get('z', 0))
            ax.set_xlabel('X (Å)')
            ax.set_ylabel('Y (Å)')
            
        elif plane == 'XZ':
            x_range = np.linspace(-extent, extent, grid_size)
            z_range = np.linspace(-extent, extent, grid_size)
            X, Z = np.meshgrid(x_range, z_range)
            Y = np.full_like(X, slice_params.get('y', 0))
            ax.set_xlabel('X (Å)')
            ax.set_ylabel('Z (Å)')
            
        elif plane == 'YZ':
            y_range = np.linspace(-extent, extent, grid_size)
            z_range = np.linspace(-extent, extent, grid_size)
            Y, Z = np.meshgrid(y_range, z_range)
            X = np.full_like(Y, slice_params.get('x', 0))
            ax.set_xlabel('Y (Å)')
            ax.set_ylabel('Z (Å)')
        
        # Calculate density on 2D slice
        density_2d = self._calculate_mock_orbital_density(X, Y, Z, coordinates, orbital.coefficients)
        
        # Plot contours
        contour = ax.contourf(X if plane != 'YZ' else Y, 
                             Y if plane == 'XY' else Z,
                             density_2d, 
                             levels=20, 
                             cmap=self.plot_settings['colormap'],
                             alpha=0.8)
        
        # Add molecular structure overlay
        for element, x, y, z in coordinates:
            if plane == 'XY':
                plot_x, plot_y = x, y
            elif plane == 'XZ':
                plot_x, plot_y = x, z
            elif plane == 'YZ':
                plot_x, plot_y = y, z
            
            color = self._get_element_color(element)
            ax.scatter(plot_x, plot_y, c=color, s=200, 
                      edgecolors='black', linewidth=2, zorder=10)
            ax.annotate(element, (plot_x, plot_y), xytext=(5, 5), 
                       textcoords='offset points', fontweight='bold')
        
        ax.set_title(f'{plane} plane')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    def _plot_radial_distribution(self, ax, coordinates: List[Tuple], orbital: EnhancedOrbitalData):
        """Plot radial distribution of orbital density"""
        # Calculate center of molecule
        if coordinates:
            center_x = np.mean([coord[1] for coord in coordinates])
            center_y = np.mean([coord[2] for coord in coordinates])
            center_z = np.mean([coord[3] for coord in coordinates])
        else:
            center_x = center_y = center_z = 0
        
        # Radial points
        r_max = 5.0
        r_points = np.linspace(0, r_max, 100)
        
        # Calculate radial density
        radial_density = []
        for r in r_points:
            # Sample points on sphere at distance r
            n_samples = 50
            phi = np.random.uniform(0, 2*np.pi, n_samples)
            theta = np.random.uniform(0, np.pi, n_samples)
            
            x_sphere = center_x + r * np.sin(theta) * np.cos(phi)
            y_sphere = center_y + r * np.sin(theta) * np.sin(phi)
            z_sphere = center_z + r * np.cos(theta)
            
            # Calculate average density at this radius
            densities = []
            for x, y, z in zip(x_sphere, y_sphere, z_sphere):
                density = self._calculate_mock_orbital_density(
                    np.array([x]), np.array([y]), np.array([z]),
                    coordinates, orbital.coefficients
                )[0]
                densities.append(abs(density))
            
            radial_density.append(np.mean(densities))
        
        ax.plot(r_points, radial_density, linewidth=2, 
                color=self.orbital_colors.get(orbital.symmetry.lower() if orbital.symmetry else 'occupied', '#0066CC'))
        ax.fill_between(r_points, radial_density, alpha=0.3)
        ax.set_xlabel('Distance from center (Å)')
        ax.set_ylabel('|Orbital density|')
        ax.set_title('Radial Distribution')
        ax.grid(True, alpha=0.3)
    
    def _get_element_color(self, element: str) -> str:
        """Get color for element visualization"""
        colors = {
            'H': 'white', 'C': 'gray', 'N': 'blue', 'O': 'red',
            'S': 'yellow', 'P': 'orange', 'F': 'green', 'Cl': 'green',
            'Br': 'brown', 'I': 'purple'
        }
        return colors.get(element, 'pink')
    
    def _generate_enhanced_educational_content(self, base_results: MolecularOrbitalResults,
                                             coordinates: List[Tuple]) -> Dict[str, Any]:
        """Generate enhanced educational analysis"""
        base_education = base_results.educational_analysis or {}
        
        # Add advanced concepts
        enhanced_education = base_education.copy()
        
        # Molecular geometry analysis
        enhanced_education['geometry_analysis'] = self._analyze_molecular_geometry(coordinates)
        
        # Orbital hybridization
        enhanced_education['hybridization_analysis'] = self._analyze_hybridization(coordinates, base_results)
        
        # Advanced reactivity predictions
        enhanced_education['advanced_reactivity'] = self._predict_advanced_reactivity(base_results)
        
        # Spectroscopic predictions
        enhanced_education['spectroscopy_predictions'] = self._predict_spectroscopic_properties(base_results)
        
        return enhanced_education
    
    def _analyze_molecular_geometry(self, coordinates: List[Tuple]) -> Dict[str, Any]:
        """Analyze molecular geometry and symmetry"""
        if len(coordinates) < 2:
            return {"geometry": "atomic", "symmetry": "spherical"}
        
        n_atoms = len(coordinates)
        
        # Simple geometry classification
        if n_atoms == 2:
            geometry = "linear"
            symmetry = "D∞h" if coordinates[0][0] == coordinates[1][0] else "C∞v"
        elif n_atoms == 3:
            # Calculate angle to determine if linear or bent
            geometry = "trigonal" if self._is_planar(coordinates) else "bent"
            symmetry = "D3h" if geometry == "trigonal" else "C2v"
        elif n_atoms == 4:
            geometry = "tetrahedral" if self._is_tetrahedral(coordinates) else "planar"
            symmetry = "Td" if geometry == "tetrahedral" else "D4h"
        else:
            geometry = "complex"
            symmetry = "C1"
        
        return {
            "geometry": geometry,
            "symmetry": symmetry,
            "n_atoms": n_atoms,
            "analysis": f"Molécule {geometry} avec symétrie {symmetry}"
        }
    
    def _is_planar(self, coordinates: List[Tuple]) -> bool:
        """Check if molecule is planar"""
        if len(coordinates) < 4:
            return True
        
        # Take first 4 atoms and check if they're coplanar
        points = np.array([[coord[1], coord[2], coord[3]] for coord in coordinates[:4]])
        
        # Calculate normal vector to plane formed by first 3 points
        v1 = points[1] - points[0]
        v2 = points[2] - points[0]
        normal = np.cross(v1, v2)
        
        # Check if 4th point lies in the plane
        v3 = points[3] - points[0]
        distance = abs(np.dot(v3, normal)) / np.linalg.norm(normal)
        
        return distance < 0.1  # Threshold for planarity
    
    def _is_tetrahedral(self, coordinates: List[Tuple]) -> bool:
        """Check if 4-atom molecule is tetrahedral"""
        if len(coordinates) != 4:
            return False
        
        points = np.array([[coord[1], coord[2], coord[3]] for coord in coordinates])
        
        # Calculate all pairwise distances
        distances = []
        for i in range(4):
            for j in range(i+1, 4):
                dist = np.linalg.norm(points[i] - points[j])
                distances.append(dist)
        
        # In perfect tetrahedron, all distances should be equal
        distances = np.array(distances)
        return np.std(distances) / np.mean(distances) < 0.1  # 10% tolerance
    
    def _analyze_hybridization(self, coordinates: List[Tuple], 
                             results: MolecularOrbitalResults) -> Dict[str, str]:
        """Analyze orbital hybridization"""
        hybridization = {}
        
        # Simple hybridization prediction based on geometry
        for i, (element, x, y, z) in enumerate(coordinates):
            if element == 'C':
                # Count bonds (simplified)
                bond_count = self._count_bonds(i, coordinates)
                
                if bond_count == 4:
                    hybridization[f"{element}{i+1}"] = "sp³ (tétraédrique)"
                elif bond_count == 3:
                    hybridization[f"{element}{i+1}"] = "sp² (trigonal)"
                elif bond_count == 2:
                    hybridization[f"{element}{i+1}"] = "sp (linéaire)"
                else:
                    hybridization[f"{element}{i+1}"] = "indéterminé"
        
        return hybridization
    
    def _count_bonds(self, atom_index: int, coordinates: List[Tuple]) -> int:
        """Count bonds for an atom (simplified distance-based)"""
        bonds = 0
        atom_pos = np.array([coordinates[atom_index][1], coordinates[atom_index][2], coordinates[atom_index][3]])
        
        for i, (element, x, y, z) in enumerate(coordinates):
            if i != atom_index:
                other_pos = np.array([x, y, z])
                distance = np.linalg.norm(atom_pos - other_pos)
                
                # Simple bond distance thresholds
                if distance < 1.8:  # Typical bond distance threshold
                    bonds += 1
        
        return bonds
    
    def _predict_advanced_reactivity(self, results: MolecularOrbitalResults) -> Dict[str, str]:
        """Advanced reactivity predictions"""
        gap_eV = results.homo_lumo_gap * 27.2114
        
        predictions = {
            "nucleophilic_attack": "HOMO détermine les sites nucléophiles",
            "electrophilic_attack": "LUMO détermine les sites électrophiles",
            "radical_reactivity": f"Gap {gap_eV:.1f} eV suggère {'haute' if gap_eV < 4 else 'faible'} réactivité radicalaire",
            "thermal_stability": f"Stabilité thermique {'faible' if gap_eV < 3 else 'élevée'} basée sur le gap",
            "photochemistry": f"Transitions électroniques {'faciles' if gap_eV < 5 else 'difficiles'} ({gap_eV:.1f} eV)"
        }
        
        return predictions
    
    def _predict_spectroscopic_properties(self, results: MolecularOrbitalResults) -> Dict[str, str]:
        """Predict spectroscopic properties"""
        gap_eV = results.homo_lumo_gap * 27.2114
        
        # UV-Vis prediction
        if gap_eV < 3.0:
            uv_vis = f"Absorption dans le visible (λ ≈ {1240/gap_eV:.0f} nm)"
        elif gap_eV < 4.0:
            uv_vis = f"Absorption UV proche (λ ≈ {1240/gap_eV:.0f} nm)"
        else:
            uv_vis = f"Absorption UV lointain (λ ≈ {1240/gap_eV:.0f} nm)"
        
        return {
            "uv_vis": uv_vis,
            "fluorescence": "Possible si gap < 4 eV et peu de vibrations" if gap_eV < 4 else "Peu probable",
            "ir_active": "Transitions vibrationnelles actives en IR",
            "raman_active": "Transitions vibrationnelles actives en Raman"
        }
    
    def _generate_molecular_comparisons(self, results: MolecularOrbitalResults,
                                      compare_molecules: List[str]) -> Dict[str, Any]:
        """Generate comparison data with other molecules"""
        comparisons = {}
        
        # This would typically involve running calculations on comparison molecules
        # For now, provide theoretical comparisons
        
        reference_gaps = {
            "benzene": 5.5,
            "methane": 12.6,
            "water": 7.5,
            "ethylene": 7.8,
            "formaldehyde": 6.2
        }
        
        current_gap = results.homo_lumo_gap * 27.2114
        
        for molecule in compare_molecules:
            if molecule.lower() in reference_gaps:
                ref_gap = reference_gaps[molecule.lower()]
                comparison = {
                    "molecule": molecule,
                    "gap_eV": ref_gap,
                    "gap_difference": current_gap - ref_gap,
                    "reactivity_comparison": "Plus réactif" if current_gap < ref_gap else "Moins réactif",
                    "stability_comparison": "Moins stable" if current_gap < ref_gap else "Plus stable"
                }
                comparisons[molecule] = comparison
        
        return comparisons
    
    def _generate_cache_key(self, xyz_content: str, method: str, charge: int, multiplicity: int) -> str:
        """Generate cache key for results"""
        import hashlib
        content = f"{xyz_content}_{method}_{charge}_{multiplicity}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _save_to_cache(self, cache_key: str, results: EnhancedOrbitalResults):
        """Save results to cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            with open(cache_file, 'w') as f:
                json.dump(results.to_dict(), f)
        except Exception as e:
            print(f"Warning: Failed to save to cache: {e}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[EnhancedOrbitalResults]:
        """Load results from cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct enhanced orbitals
                enhanced_orbitals = []
                for orb_data in data.get('orbitals', []):
                    enhanced_orbitals.append(EnhancedOrbitalData(**orb_data))
                
                data['orbitals'] = enhanced_orbitals
                return EnhancedOrbitalResults(**data)
        except Exception as e:
            print(f"Warning: Failed to load from cache: {e}")
        
        return None
    
    def export_orbital_data(self, results: EnhancedOrbitalResults, 
                           format: str = 'json', filename: str = None) -> str:
        """Export orbital analysis results"""
        if filename is None:
            filename = f"orbital_analysis_{format}"
        
        if format == 'json':
            output_file = f"{filename}.json"
            with open(output_file, 'w') as f:
                json.dump(results.to_dict(), f, indent=2)
        
        elif format == 'csv':
            import pandas as pd
            output_file = f"{filename}.csv"
            
            # Create orbital data DataFrame
            orbital_data = []
            for orbital in results.orbitals:
                orbital_data.append({
                    'Index': orbital.orbital_index,
                    'Energy_eV': orbital.energy * 27.2114,
                    'Energy_Hartree': orbital.energy,
                    'Occupation': orbital.occupation,
                    'Type': orbital.orbital_type,
                    'Symmetry': orbital.symmetry
                })
            
            df = pd.DataFrame(orbital_data)
            df.to_csv(output_file, index=False)
        
        return output_file
    
    def generate_orbital_report(self, results: EnhancedOrbitalResults, 
                              include_plots: bool = True) -> str:
        """Generate comprehensive orbital analysis report"""
        
        report_lines = [
            "# ANALYSE DES ORBITALES MOLÉCULAIRES",
            "# Rapport généré par IAM Physical Chemistry",
            "=" * 60,
            "",
            f"## RÉSULTATS PRINCIPAUX",
            f"HOMO: {results.homo_energy * 27.2114:.3f} eV",
            f"LUMO: {results.lumo_energy * 27.2114:.3f} eV", 
            f"Gap HOMO-LUMO: {results.homo_lumo_gap * 27.2114:.3f} eV",
            f"Énergie totale: {results.total_energy:.6f} Hartree",
            f"Moment dipolaire: {results.dipole_moment:.3f} Debye",
            "",
            f"## ORBITALES DÉTAILLÉES",
        ]
        
        for orbital in results.orbitals:
            report_lines.append(
                f"Orbitale {orbital.orbital_index}: "
                f"{orbital.energy * 27.2114:.3f} eV, "
                f"occupation {orbital.occupation:.1f}, "
                f"type {orbital.orbital_type}"
            )
        
        if results.educational_analysis:
            report_lines.extend([
                "",
                "## ANALYSE ÉDUCATIVE",
                ""
            ])
            
            for section, content in results.educational_analysis.items():
                report_lines.append(f"### {section.replace('_', ' ').title()}")
                if isinstance(content, dict):
                    for key, value in content.items():
                        report_lines.append(f"- {key}: {value}")
                else:
                    report_lines.append(f"- {content}")
                report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # Save report
        report_file = f"orbital_report_{results.method}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_file
