# Module: IAM_StabilityPredictor
# Description: Prédiction de la stabilité des molécules

def predict_stability(xyz_data):
    """
    Prédit la stabilité d'une molécule à partir de ses données XYZ.
    :param xyz_data: Données XYZ de la molécule
    :return: Résultat de la prédiction
    """
    return predict_stability_logic(xyz_data)

def predict_stability_logic(xyz_data):
    """
    Prédit la stabilité d'une molécule à partir de ses données XYZ.
    :param xyz_data: Données XYZ de la molécule
    :return: Résultat de la prédiction
    """
    return f"Stabilité estimée pour {len(xyz_data.splitlines())} atomes"
