#!/usr/bin/env python3
"""
File Creator Utility for IAM Project
====================================

This utility demonstrates the capability to create files programmatically 
in the IAM repository. It provides functions to create various types of 
files commonly used in the molecular chemistry analysis workflow.

Author: AI Assistant
Date: 2025-01-16
Project: IAM - Intelligent Analysis of Molecules
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class IAMFileCreator:
    """Utility class for creating files in the IAM project structure."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the file creator with a base path.
        
        Args:
            base_path: Base directory for file creation (default: current directory)
        """
        self.base_path = Path(base_path)
        self.created_files = []
        
    def create_molecule_file(self, filename: str, content: str, file_type: str = "xyz") -> bool:
        """
        Create a molecular structure file.
        
        Args:
            filename: Name of the file (without extension)
            content: Content of the molecular file
            file_type: Type of file (xyz, mol, sdf, pdb)
            
        Returns:
            bool: True if file created successfully, False otherwise
        """
        try:
            file_path = self.base_path / f"{filename}.{file_type}"
            with open(file_path, 'w') as f:
                f.write(content)
            self.created_files.append(str(file_path))
            print(f"✅ Created molecular file: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating molecular file: {e}")
            return False
    
    def create_analysis_result(self, molecule_name: str, results: Dict[str, Any]) -> bool:
        """
        Create a JSON file with analysis results.
        
        Args:
            molecule_name: Name of the molecule
            results: Dictionary containing analysis results
            
        Returns:
            bool: True if file created successfully, False otherwise
        """
        try:
            # Create IAM_Results directory if it doesn't exist
            results_dir = self.base_path / "IAM_Results"
            results_dir.mkdir(exist_ok=True)
            
            # Add metadata to results
            results_with_meta = {
                "molecule_name": molecule_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "created_by": "IAM File Creator Utility",
                "results": results
            }
            
            file_path = results_dir / f"{molecule_name}_analysis.json"
            with open(file_path, 'w') as f:
                json.dump(results_with_meta, f, indent=2)
            
            self.created_files.append(str(file_path))
            print(f"✅ Created analysis result: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating analysis result: {e}")
            return False
    
    def create_script_file(self, script_name: str, script_content: str, 
                          script_type: str = "py") -> bool:
        """
        Create a script file in the IAM_Scripts directory.
        
        Args:
            script_name: Name of the script (without extension)
            script_content: Content of the script
            script_type: Type of script (py, sh, etc.)
            
        Returns:
            bool: True if file created successfully, False otherwise
        """
        try:
            # Create IAM_Scripts directory if it doesn't exist
            scripts_dir = self.base_path / "IAM_Scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            file_path = scripts_dir / f"{script_name}.{script_type}"
            with open(file_path, 'w') as f:
                f.write(script_content)
                
            # Make script executable if it's a shell script
            if script_type in ['sh', 'bash']:
                os.chmod(file_path, 0o755)
            
            self.created_files.append(str(file_path))
            print(f"✅ Created script file: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating script file: {e}")
            return False
    
    def create_config_file(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Create a configuration file.
        
        Args:
            config_name: Name of the configuration file
            config_data: Configuration data dictionary
            
        Returns:
            bool: True if file created successfully, False otherwise
        """
        try:
            file_path = self.base_path / f"{config_name}.json"
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.created_files.append(str(file_path))
            print(f"✅ Created config file: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating config file: {e}")
            return False
    
    def create_documentation(self, doc_name: str, content: str, doc_type: str = "md") -> bool:
        """
        Create a documentation file.
        
        Args:
            doc_name: Name of the documentation file
            content: Content of the documentation
            doc_type: Type of documentation (md, txt, rst)
            
        Returns:
            bool: True if file created successfully, False otherwise
        """
        try:
            # Create docs directory if it doesn't exist
            docs_dir = self.base_path / "docs"
            docs_dir.mkdir(exist_ok=True)
            
            file_path = docs_dir / f"{doc_name}.{doc_type}"
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.created_files.append(str(file_path))
            print(f"✅ Created documentation: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating documentation: {e}")
            return False
    
    def list_created_files(self) -> List[str]:
        """
        Get a list of all files created by this instance.
        
        Returns:
            List of file paths created
        """
        return self.created_files.copy()
    
    def demonstrate_capabilities(self) -> None:
        """
        Demonstrate various file creation capabilities.
        """
        print("🚀 Demonstrating IAM File Creation Capabilities")
        print("=" * 50)
        
        # Create sample molecular structure
        methane_xyz = """5
Methane molecule
C    0.000000    0.000000    0.000000
H    0.628736    0.628736    0.628736
H   -0.628736   -0.628736    0.628736
H    0.628736   -0.628736   -0.628736
H   -0.628736    0.628736   -0.628736
"""
        self.create_molecule_file("demo_methane", methane_xyz, "xyz")
        
        # Create sample analysis results
        sample_results = {
            "molecular_formula": "CH4",
            "molecular_weight": 16.043,
            "energy": -40.4782,
            "dipole_moment": 0.0,
            "homo_lumo_gap": 12.5,
            "stability_score": 0.95
        }
        self.create_analysis_result("demo_methane", sample_results)
        
        # Create sample script
        sample_script = '''#!/usr/bin/env python3
"""
Demo script created by IAM File Creator Utility
"""

print("This is a demonstration script!")
print("File creation capability confirmed.")

def hello_iam():
    return "Hello from IAM!"

if __name__ == "__main__":
    print(hello_iam())
'''
        self.create_script_file("demo_script", sample_script)
        
        # Create sample configuration
        sample_config = {
            "xtb_path": "/usr/local/bin/xtb",
            "temp_dir": "/tmp/iam_temp",
            "max_atoms": 1000,
            "default_method": "GFN2-xTB",
            "output_format": "json"
        }
        self.create_config_file("demo_config", sample_config)
        
        # Create sample documentation
        sample_doc = """# File Creation Demonstration

This document was created to demonstrate the file creation capabilities 
within the IAM repository.

## What was created:
- Molecular structure files (.xyz)
- Analysis result files (.json)
- Script files (.py)
- Configuration files (.json)
- Documentation files (.md)

## Conclusion:
✅ File creation capability has been successfully demonstrated!
"""
        self.create_documentation("file_creation_demo", sample_doc)
        
        print("\n📋 Summary of Created Files:")
        for i, file_path in enumerate(self.created_files, 1):
            print(f"  {i}. {file_path}")
        
        print(f"\n🎉 Successfully created {len(self.created_files)} files!")
        print("✅ File creation capability confirmed in IAM repository!")


def main():
    """Main function to demonstrate file creation capabilities."""
    creator = IAMFileCreator()
    creator.demonstrate_capabilities()


if __name__ == "__main__":
    main()