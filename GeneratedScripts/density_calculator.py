import re
from collections import defaultdict

def parse_chemical_formula(formula):
    """
    Parse la formule chimique pour obtenir un dictionnaire des éléments et de leurs quantités.

    Args:
        formula (str): La formule chimique de l'explosif.

    Returns:
        dict: Un dictionnaire avec les éléments comme clés et leurs quantités comme valeurs.
    """
    try:
        pattern = r'([A-Z][a-z]*)(\d*)'
        matches = re.findall(pattern, formula)
        composition = defaultdict(int)
        for element, count in matches:
            composition[element] += int(count) if count else 1
        return dict(composition)
    except Exception as e:
        raise ValueError(f"Erreur lors de l'analyse de la formule chimique: {str(e)}")

def calculate_molar_mass(composition):
    """
    Calcule la masse molaire à partir de la composition chimique.

    Args:
        composition (dict): Un dictionnaire des éléments et de leurs quantités.

    Returns:
        float: La masse molaire de la substance.
    """
    atomic_masses = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'S': 32.06, 'Cl': 35.45, 'F': 18.998, 'Br': 79.904,
        # Ajouter d'autres éléments si nécessaire
    }
    try:
        molar_mass = sum(atomic_masses[element] * count for element, count in composition.items())
        return molar_mass
    except KeyError as e:
        raise ValueError(f"Élément inconnu dans la composition: {str(e)}")

def kamlet_jacobs_density(molar_mass, composition):
    """
    Calcule la densité cristalline en utilisant l'équation de Kamlet-Jacobs.

    Args:
        molar_mass (float): La masse molaire de l'explosif.
        composition (dict): La composition chimique de l'explosif.

    Returns:
        float: La densité cristalline prédite.
    """
    try:
        n_c = composition.get('C', 0)
        n_h = composition.get('H', 0)
        n_o = composition.get('O', 0)
        n_n = composition.get('N', 0)

        # Paramètres de l'équation de Kamlet-Jacobs
        rho_0 = 1.8  # Densité de référence pour les explosifs (g/cm^3)
        k = 1.0  # Constante empirique

        # Calcul de la densité
        density = rho_0 + k * (n_c + n_h + n_o + n_n) / molar_mass
        return density
    except Exception as e:
        raise ValueError(f"Erreur lors du calcul de la densité: {str(e)}")

def density_calculator_main(input_data):
    """
    Module qui calcule la densité d'un explosif à partir de sa formule chimique et de sa structure moléculaire. Utilise l'équation de Kamlet-Jacobs et les masses atomiques standards pour prédire la densité cristalline.
    
    Args:
        input_data (str): La formule chimique de l'explosif.
    
    Returns:
        dict: Résultats du traitement
    """
    try:
        composition = parse_chemical_formula(input_data)
        molar_mass = calculate_molar_mass(composition)
        density = kamlet_jacobs_density(molar_mass, composition)
        result = {"success": True, "density": density, "molar_mass": molar_mass, "composition": composition}
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test rapide
    test_data = "C3H6N6O6"  # Exemple de formule chimique pour RDX
    print(density_calculator_main(test_data))