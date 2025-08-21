#!/usr/bin/env python3
"""
Ce module corrige les fichiers MOL défectueux générés par INDIGO afin qu'ils soient compatibles avec RDKit.

Problèmes à corriger :
- Le header de la ligne 1 est souvent non standard (ex: '-INDIGO-07222523152D'), ce qui fait échouer RDKit.
- La ligne de comptage (ligne 4) contient parfois des formats invalides (ex: ' 4  4  0.  0.') qui provoquent l'erreur :
  ValueError: Cannot convert ' 0.' to unsigned int
- RDKit est strict : Chem.MolFromMolBlock(mol_block) retourne None si le format est incorrect.

Objectif :
- Écrire une fonction `fix_mol_indigo(mol_str: str) -> str` qui :
  1. Remplace les 3 premières lignes (header) par un format standard :
     - ligne 1 : 'MOL'
     - ligne 2 : '  IAM'
     - ligne 3 : ''
  2. Corrige la ligne de comptage (ligne 4) pour que les nombres soient des entiers valides.
     - Extraire le nombre d'atomes et de liaisons (souvent les deux premiers champs)
     - Les forcer à être des `int`, sans points flottants.
     - Reformater la ligne avec padding fixe (3 chiffres chacun) et finissant par 'V2000'

Cette fonction sera utilisée juste avant `Chem.MolFromMolBlock()` dans un backend Flask.

Ajoute aussi une vérification `if len(lines) < 4` pour éviter les fichiers mal formés.

Retourne la string corrigée (joinée par '\\n').
"""

import re
from rdkit import Chem

def fix_mol_indigo(mol_str: str) -> str:
    """
    Corrige les fichiers MOL INDIGO pour les rendre compatibles avec RDKit.
    Version SIMPLIFIÉE et ROBUSTE
    """
    lines = mol_str.strip().split('\n')
    
    if len(lines) < 4:
        raise ValueError(f"Fichier MOL trop court: {len(lines)} lignes")
    
    # Header standard
    lines[0] = 'Molecule'
    lines[1] = '  IAM'  
    lines[2] = ''
    
    # Ligne de comptage - extraction manuelle des deux premiers nombres
    counts_line = lines[3].strip()
    
    # Méthode robuste: split et prendre les premiers éléments numériques
    parts = counts_line.split()
    num_atoms = 0
    num_bonds = 0
    
    for part in parts:
        try:
            if '.' in part:
                # Convertir float vers int
                num = int(float(part))
            else:
                num = int(part)
            
            if num_atoms == 0:
                num_atoms = num
            elif num_bonds == 0:
                num_bonds = num 
                break
        except ValueError:
            continue
    
    if num_atoms == 0:
        raise ValueError(f"Impossible d'extraire le nombre d'atomes de: '{counts_line}'")
    
    # Reformater ligne de comptage avec format strict
    lines[3] = f"{num_atoms:3d}{num_bonds:3d}  0  0  0  0            999 V2000"
    
    return '\n'.join(lines)


def test_fix_mol_indigo():
    """Test de la fonction avec des exemples problématiques"""
    
    # Test 1: Fichier INDIGO typique qui échoue - EXEMPLE COMPLET
    indigo_mol = """-INDIGO-07222523152D

  5  5  0  0  0  0  0  0  0  0999 V2000
    3.5800   -2.9499    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.1200   -2.4496    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.6603   -2.9499    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.6603   -4.4502    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.1200   -4.9506    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  1  1  0  0  0  0
M  END"""

    print("🧪 Test fix_mol_indigo() - Version simplifiée")
    print("=" * 50)
    
    # DEBUG: Afficher la structure originale
    print("DEBUG - Structure MOL originale:")
    for i, line in enumerate(indigo_mol.split('\n')):
        print(f"   Ligne {i}: '{line}'")
    
    try:
        # Test avant correction
        print("1. Test AVANT correction:")
        mol_before = Chem.MolFromMolBlock(indigo_mol, sanitize=False)
        print(f"   RDKit result: {mol_before}")
        
        # Correction
        fixed_mol = fix_mol_indigo(indigo_mol)
        print("\\n2. MOL corrigé (header seulement):")
        print("   " + "\\n   ".join(fixed_mol.split('\\n')[:6]))  # Affiche les 6 premières lignes
        
        # Test après correction
        print("\\n3. Test APRÈS correction:")
        mol_after = Chem.MolFromMolBlock(fixed_mol, sanitize=False)
        print(f"   RDKit result: {mol_after}")
        
        if mol_after:
            print(f"   ✅ Succès! {mol_after.GetNumAtoms()} atomes, {mol_after.GetNumBonds()} liaisons")
            
            # Test conversion XYZ
            try:
                xyz = Chem.MolToXYZBlock(mol_after)
                print(f"   ✅ Conversion XYZ réussie: {len(xyz)} caractères")
            except Exception as e:
                print(f"   ⚠️ Conversion XYZ échouée: {e}")
        else:
            print("   ❌ Échec: RDKit retourne encore None")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Cas simple avec water molecule
    print("\\n4. Test avec molécule simple (water):")
    simple_mol = """-INDIGO-Simple

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END"""
    
    try:
        fixed_simple = fix_mol_indigo(simple_mol)
        mol_simple = Chem.MolFromMolBlock(fixed_simple, sanitize=False)
        if mol_simple:
            print(f"   ✅ Water molecule: {mol_simple.GetNumAtoms()} atomes")
        else:
            print("   ❌ Water molecule: échec")
    except Exception as e:
        print(f"   ❌ Water molecule: {e}")

if __name__ == "__main__":
    test_fix_mol_indigo()
