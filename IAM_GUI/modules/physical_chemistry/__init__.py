# Physical Chemistry Modules Package
# Contains modules for physical chemistry analysis and computations

__version__ = "1.0.0"

# Import main classes for easy access
try:
    from .molecular_orbitals import MolecularOrbitalAnalyzer
    from .enhanced_molecular_orbitals import EnhancedMolecularOrbitalAnalyzer
    from .professional_molecular_orbitals import ProfessionalMolecularOrbitalAnalyzer
    
    __all__ = [
        'MolecularOrbitalAnalyzer',
        'EnhancedMolecularOrbitalAnalyzer', 
        'ProfessionalMolecularOrbitalAnalyzer'
    ]
except ImportError as e:
    print(f"Warning: Some physical chemistry modules could not be imported: {e}")
    __all__ = []
