import subprocess
import os

def run_xtb(xyz_file):
    """
    Lancement du calcul XTB pour un fichier xyz donné.
    """
    if not os.path.isfile(xyz_file):
        raise FileNotFoundError(f"Le fichier {xyz_file} n'existe pas.")
    
    command = ["xtb", xyz_file, "--opt", "--gfn2"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print("❌ XTB a échoué.")
        print(result.stderr)
    else:
        print("✅ XTB terminé avec succès.")
        print(result.stdout)

    return result.stdout.decode("utf-8") if result.returncode == 0 else None


def parse_xtb_output(output):
    """
    Parse les résultats de XTB pour extraire l'énergie totale et le gap HOMO–LUMO.
    """
    lines = output.splitlines()
    data = {}

    for line in lines:
        if "TOTAL ENERGY" in line:
            try:
                energy = float(line.split()[3])
                data["total_energy_hartree"] = energy
                print(f"✅ Énergie totale : {energy} Hartree")
            except ValueError:
                print("❌ Erreur lors de la lecture de l'énergie totale.")

        if "HOMO–LUMO GAP" in line or "HOMO-LUMO GAP" in line:
            try:
                gap = float(line.split()[3])
                data["homo_lumo_gap_ev"] = gap
                print(f"🦋 Gap HOMO–LUMO : {gap} eV")
            except ValueError:
                print("❌ Erreur lors de la lecture du gap HOMO–LUMO.")

    return data


def analyze_molecule(xyz_file):
    """
    Fonction principale pour analyser une molécule.
    """
    output = run_xtb(xyz_file)
    if output:
        parsed = parse_xtb_output(output)
        return parsed
    return {}


if __name__ == "__main__":
    # Tester avec un fichier xyz spécifique
    try:
        result = analyze_molecule("test.xyz")
        print(f"📈 Données extraites: {result}")
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")
