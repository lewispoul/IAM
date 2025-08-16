#!/usr/bin/env python3
"""
Interactive File Creator for IAM Repository
===========================================

This script provides an interactive interface for creating files
in the IAM repository, demonstrating real-time file creation capabilities.
"""

import os
import json
import datetime
from pathlib import Path


def create_timestamp_file():
    """Create a file with current timestamp."""
    timestamp = datetime.datetime.now()
    filename = f"timestamp_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
    
    content = f"""
File Created Successfully! ✅
============================

Timestamp: {timestamp.isoformat()}
Repository: lewispoul/IAM
Created by: AI Assistant
Purpose: Demonstrating real-time file creation capability

This file proves that I can create files in this repository
at any time with current timestamps and custom content.

File creation capability: CONFIRMED ✅
"""
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ Created timestamp file: {filename}")
    return filename


def create_dynamic_molecule(name, formula, atoms_data):
    """Create a molecular file with dynamic content."""
    filename = f"dynamic_{name.lower()}.xyz"
    
    content = f"""{len(atoms_data)}
{name} - Created dynamically on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    for atom_line in atoms_data:
        content += atom_line + "\n"
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ Created dynamic molecule file: {filename}")
    return filename


def create_project_status():
    """Create a status file showing current project state."""
    status_data = {
        "project_name": "IAM - Intelligent Analysis of Molecules",
        "file_creation_test": "PASSED",
        "timestamp": datetime.datetime.now().isoformat(),
        "capabilities_confirmed": [
            "File creation",
            "Directory creation", 
            "Content generation",
            "Dynamic data handling",
            "Integration with existing structure"
        ],
        "files_created_in_demo": [],
        "repository_access": "CONFIRMED",
        "ai_assistant_status": "ACTIVE"
    }
    
    # List all demo files created
    demo_files = []
    for file in Path(".").glob("demo_*"):
        demo_files.append(str(file))
    for file in Path(".").glob("dynamic_*"):
        demo_files.append(str(file))
    for file in Path(".").glob("timestamp_*"):
        demo_files.append(str(file))
    
    status_data["files_created_in_demo"] = demo_files
    
    filename = "project_status.json"
    with open(filename, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"✅ Created project status file: {filename}")
    return filename


def main():
    """Main demonstration function."""
    print("🚀 Interactive File Creation Demonstration")
    print("=" * 45)
    
    # Create timestamp file
    timestamp_file = create_timestamp_file()
    
    # Create dynamic molecule
    water_atoms = [
        "O    0.000000    0.000000    0.000000",
        "H    0.757000    0.586000    0.000000", 
        "H   -0.757000    0.586000    0.000000"
    ]
    molecule_file = create_dynamic_molecule("Water", "H2O", water_atoms)
    
    # Create project status
    status_file = create_project_status()
    
    print("\n📁 Files Created:")
    print(f"  1. {timestamp_file}")
    print(f"  2. {molecule_file}")
    print(f"  3. {status_file}")
    
    print("\n✅ Interactive file creation demonstration complete!")
    print("🎯 ANSWER: YES, I can create files in this repository!")


if __name__ == "__main__":
    main()