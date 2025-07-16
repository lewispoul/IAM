#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

def run_xtb(xyz_file):
    # Vérifie d'abord si le fichier est dans le dossier courant
    if not os.path.isfile(xyz_file):
        # Tente ensuite de le trouver dans ~/IAM/tools/xtb/
        fallback_path = os.path.expanduser(f"~/IAM/tools/xtb/{xyz_file}")
        if os.path.isfile(fallback_path):
            xyz_file = fallback_path
        else:
            raise FileNotFoundError(f"❌ Le fichier {xyz_file} n'existe pas.")

    print(f"🔬 Calcul XTB en cours pour {xyz_file}...")
    command = ["xtb", xyz_file, "--opt", "--gfn2"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print("❌ XTB a échoué.")
        print(result.stderr.decode())
    else:
        print("✅ XTB terminé avec succès.")
        print_output_summary(result.stdout.decode())

def print_output_summary(output):
    lines = output.splitlines()
    data = {}

    for line in lines:
        if "TOTAL ENERGY" in line:
            try:
                data["total_energy_hartree"] = float(line.split()[3])
                print(f"🟢 Énergie totale : {data['total_energy_hartree']} Hartree")
            except Exception:
                print("⚠️ Impossible d’extraire l’énergie totale.")
        if "HOMO-LUMO GAP" in line:
            try:
                data["homo_lumo_gap_ev"] = float(line.split()[4])
                print(f"🌈 Gap HOMO–LUMO : {data['homo_lumo_gap_ev']} eV")
            except Exception:
                print("⚠️ Impossible d’extraire le gap HOMO–LUMO.")

    print(f"📊 Données extraites : {data}")

def analyze_molecule(xyz_file):
    output = run_xtb(xyz_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : ./xtb.py molecule.xyz")
        sys.exit(1)
    analyze_molecule(sys.argv[1])
