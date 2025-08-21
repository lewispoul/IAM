#!/usr/bin/env python3
"""
IAM_MoleculeEngine.py
====================
Pipeline principal de calcul moléculaire pour IAM:
SMILES/MOL → .xyz via RDKit → optimisation XTB → extraction résultats

Modules: rdkit, openbabel, xtb, numpy, pandas, json
Auteur: IAM Project Team
Version: 2.0 (Juillet 2025)
"""

import os
import subprocess
import tempfile
import json
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Union

# RDKit imports
from rdkit import Chem
from rdkit.Chem import AllChem, rdDepictor, rdDistGeom, rdForceFieldHelpers
import pandas as pd
import numpy as np


class IAM_MoleculeEngine:
    """
    Moteur principal de calcul moléculaire IAM
    """
    
    def __init__(self, results_dir: str = "IAM_Results", knowledge_dir: str = "IAM_Knowledge"):
        """
        Initialise le moteur IAM
        
        Args:
            results_dir: Dossier pour sauvegarder les résultats
            knowledge_dir: Dossier de la base de connaissances
        """
        self.results_dir = Path(results_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.knowledge_dir.mkdir(exist_ok=True)
        
        # Vérifier XTB
        self._check_xtb_availability()
    
    def _check_xtb_availability(self):
        """Vérifie que XTB est disponible"""
        try:
            result = subprocess.run(["xtb", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ XTB disponible:", result.stdout.split('\n')[0])
            else:
                print("⚠️ XTB trouvé mais erreur:", result.stderr)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ XTB non trouvé dans PATH")
    
    def smiles_to_mol(self, smiles: str, add_hydrogens: bool = True) -> Chem.Mol:
        """
        Convertit SMILES vers molécule RDKit
        
        Args:
            smiles: String SMILES
            add_hydrogens: Ajouter hydrogènes explicites
            
        Returns:
            Molécule RDKit
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"SMILES invalide: {smiles}")
        
        if add_hydrogens:
            mol = Chem.AddHs(mol)
        
        return mol
    
    def mol_to_xyz(self, mol: Chem.Mol, optimize_3d: bool = True) -> str:
        """
        Génère coordonnées 3D et convertit en format XYZ
        
        Args:
            mol: Molécule RDKit
            optimize_3d: Optimiser géométrie avec UFF
            
        Returns:
            String XYZ
        """
        # Génération 3D
        try:
            # ETKDG pour coordonnées initiales
            params = rdDistGeom.ETKDGv3() if hasattr(rdDistGeom, "ETKDGv3") else rdDistGeom.ETKDG()
            result = rdDistGeom.EmbedMolecule(mol, params)
            
            if result != 0:
                # Fallback
                rdDistGeom.EmbedMolecule(mol)
            
            if optimize_3d:
                # Optimisation UFF
                try:
                    rdForceFieldHelpers.UFFOptimizeMolecule(mol)
                except:
                    # Fallback MMFF
                    try:
                        rdForceFieldHelpers.MMFFOptimizeMolecule(mol)
                    except:
                        print("⚠️ Optimisation forcefield échouée")
            
            # Conversion XYZ
            xyz_block = Chem.MolToXYZBlock(mol)
            return xyz_block
            
        except Exception as e:
            raise RuntimeError(f"Erreur génération 3D: {e}")
    
    def run_xtb_calculation(self, xyz_content: str, job_name: str = "molecule", 
                          method: str = "gfn2", optimize: bool = True) -> Dict[str, Any]:
        """
        Lance calcul XTB sur molécule XYZ
        
        Args:
            xyz_content: Contenu fichier XYZ
            job_name: Nom du job
            method: Méthode XTB (gfn0, gfn1, gfn2)
            optimize: Optimisation géométrique
            
        Returns:
            Dictionnaire des résultats
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Fichier XYZ d'entrée
            xyz_file = temp_path / f"{job_name}.xyz"
            xyz_file.write_text(xyz_content)
            
            # Commande XTB
            cmd = ["xtb", str(xyz_file), "--json"]
            
            if optimize:
                cmd.append("--opt")
            
            if method == "gfn0":
                cmd.extend(["--gfn", "0"])
            elif method == "gfn1":
                cmd.extend(["--gfn", "1"])
            else:  # gfn2 par défaut
                cmd.extend(["--gfn", "2"])
            
            # Exécution
            try:
                result = subprocess.run(
                    cmd, cwd=temp_dir, capture_output=True, 
                    text=True, timeout=300  # 5 min timeout
                )
                
                # Extraction résultats
                results = {
                    "job_name": job_name,
                    "method": method,
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
                # JSON XTB si disponible
                json_file = temp_path / "xtbout.json"
                if json_file.exists():
                    try:
                        with open(json_file) as f:
                            xtb_data = json.load(f)
                        results["xtb_json"] = xtb_data
                        
                        # Extraction données clés
                        if "total energy" in xtb_data:
                            results["total_energy_hartree"] = xtb_data["total energy"]
                        
                        if "HOMO-LUMO gap/eV" in xtb_data:
                            results["homo_lumo_gap_ev"] = xtb_data["HOMO-LUMO gap/eV"]
                            
                    except Exception as e:
                        results["json_error"] = str(e)
                
                # XYZ optimisé si disponible
                opt_xyz = temp_path / "xtbopt.xyz"
                if opt_xyz.exists():
                    results["optimized_xyz"] = opt_xyz.read_text()
                
                return results
                
            except subprocess.TimeoutExpired:
                return {
                    "job_name": job_name,
                    "success": False,
                    "error": "Timeout XTB (>5min)"
                }
            except Exception as e:
                return {
                    "job_name": job_name,
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
    
    def full_pipeline(self, input_data: Union[str, Chem.Mol], 
                     job_name: str = "molecule", 
                     input_type: str = "smiles") -> Dict[str, Any]:
        """
        Pipeline complet: Input → XYZ → XTB → Résultats
        
        Args:
            input_data: SMILES string ou molécule RDKit
            job_name: Nom du job
            input_type: "smiles" ou "mol"
            
        Returns:
            Résultats complets
        """
        results = {
            "job_name": job_name,
            "input_type": input_type,
            "pipeline_steps": []
        }
        
        try:
            # 1. Conversion vers RDKit Mol
            if input_type == "smiles":
                mol = self.smiles_to_mol(input_data)
                results["smiles"] = input_data
                results["pipeline_steps"].append("✅ SMILES → RDKit Mol")
            else:
                mol = input_data
                results["pipeline_steps"].append("✅ RDKit Mol input")
            
            # 2. Génération XYZ 3D
            xyz_content = self.mol_to_xyz(mol)
            results["initial_xyz"] = xyz_content
            results["pipeline_steps"].append("✅ Génération XYZ 3D")
            
            # 3. Calcul XTB
            xtb_results = self.run_xtb_calculation(xyz_content, job_name)
            results.update(xtb_results)
            
            if xtb_results["success"]:
                results["pipeline_steps"].append("✅ Calcul XTB réussi")
            else:
                results["pipeline_steps"].append("❌ Calcul XTB échoué")
            
            # 4. Sauvegarde
            self._save_results(results)
            results["pipeline_steps"].append("✅ Résultats sauvegardés")
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            results["traceback"] = traceback.format_exc()
            results["pipeline_steps"].append(f"❌ Erreur: {e}")
            return results
    
    def _save_results(self, results: Dict[str, Any]):
        """
        Sauvegarde résultats dans IAM_Results/
        """
        job_name = results.get("job_name", "unknown")
        
        # Fichier JSON principal
        json_file = self.results_dir / f"{job_name}_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # XYZ initial si disponible
        if "initial_xyz" in results:
            xyz_file = self.results_dir / f"{job_name}_initial.xyz"
            xyz_file.write_text(results["initial_xyz"])
        
        # XYZ optimisé si disponible
        if "optimized_xyz" in results:
            opt_file = self.results_dir / f"{job_name}_optimized.xyz"
            opt_file.write_text(results["optimized_xyz"])


# Fonctions utilitaires pour rétrocompatibilité
def generate_xyz_from_smiles(smiles: str, output_path: str):
    """
    Fonction legacy pour génération XYZ depuis SMILES
    """
    engine = IAM_MoleculeEngine()
    mol = engine.smiles_to_mol(smiles)
    xyz_content = engine.mol_to_xyz(mol)
    
    with open(output_path, 'w') as f:
        f.write(xyz_content)


def run_xtb_on_file(xyz_path: str) -> Dict[str, Any]:
    """
    Fonction legacy pour calcul XTB sur fichier
    """
    engine = IAM_MoleculeEngine()
    
    with open(xyz_path) as f:
        xyz_content = f.read()
    
    job_name = Path(xyz_path).stem
    return engine.run_xtb_calculation(xyz_content, job_name)


def full_molecule_workflow(smiles: str, name: str) -> Dict[str, Any]:
    """
    Fonction legacy pour workflow complet
    """
    engine = IAM_MoleculeEngine()
    return engine.full_pipeline(smiles, name, "smiles")


# Test rapide si exécuté directement
if __name__ == "__main__":
    print("🧪 Test IAM_MoleculeEngine")
    print("=" * 40)
    
    engine = IAM_MoleculeEngine()
    
    # Test SMILES → XTB
    test_smiles = "CCO"  # Ethanol
    print(f"Test avec SMILES: {test_smiles}")
    
    results = engine.full_pipeline(test_smiles, "ethanol_test")
    
    print("\nRésultats:")
    for step in results.get("pipeline_steps", []):
        print(f"  {step}")
    
    if results.get("success"):
        print(f"✅ Succès! Énergie: {results.get('total_energy_hartree', 'N/A')} Hartree")
        if "homo_lumo_gap_ev" in results:
            print(f"   Gap HOMO-LUMO: {results['homo_lumo_gap_ev']} eV")
    else:
        print(f"❌ Échec: {results.get('error', 'Erreur inconnue')}")
