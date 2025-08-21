#!/usr/bin/env python3
"""
IAM_PerformancePredictor.py
============================
Module de prédiction des performances énergétiques pour IAM:
- Vitesse de détonation (VoD)
- Pression Chapman-Jouguet (Pcj)
- Enthalpie de formation/détonation
- Sensibilités

Méthodes:
- Formules empiriques (Kamlet-Jacobs, Keshavarz)
- Modèles ML (GPR, Random Forest, etc.)

Auteur: IAM Project Team
Version: 2.0 (Juillet 2025)
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import warnings

# Machine Learning
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    print("⚠️ scikit-learn non disponible - ML désactivé")
    SKLEARN_AVAILABLE = False


class IAM_PerformancePredictor:
    """
    Prédicteur de performances énergétiques moléculaires
    """
    
    def __init__(self, knowledge_dir: str = "IAM_Knowledge"):
        """
        Initialise le prédicteur
        
        Args:
            knowledge_dir: Dossier base de connaissances
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        
        # Modèles ML (si disponibles)
        self.ml_models = {}
        self.scalers = {}
        
        # Base de données interne
        self.experimental_data = self._load_experimental_database()
    
    def _load_experimental_database(self) -> pd.DataFrame:
        """
        Charge base de données expérimentale
        """
        db_file = self.knowledge_dir / "experimental_explosives.csv"
        
        if db_file.exists():
            try:
                return pd.read_csv(db_file)
            except Exception as e:
                print(f"⚠️ Erreur chargement DB: {e}")
        
        # Base de données par défaut (quelques explosifs connus)
        default_data = {
            'name': ['TNT', 'RDX', 'HMX', 'PETN', 'Tetryl', 'Picric Acid'],
            'formula': ['C7H5N3O6', 'C3H6N6O6', 'C4H8N8O8', 'C5H8N4O12', 'C7H5N5O8', 'C6H3N3O7'],
            'density_gcc': [1.654, 1.82, 1.91, 1.77, 1.73, 1.763],
            'oxygen_balance': [-73.96, -21.61, -21.61, -10.13, -47.35, -45.41],
            'heat_formation_kjmol': [67.4, 92.3, 75.0, -538.9, 12.1, -217.1],
            'vod_ms': [6900, 8750, 9100, 8350, 7570, 7350],
            'pcj_gpa': [19.0, 34.0, 39.0, 33.0, 25.0, 24.0],
            'impact_sensitivity_j': [15.0, 7.5, 7.0, 3.0, 0.4, 5.0]
        }
        
        df = pd.DataFrame(default_data)
        
        # Sauvegarde
        df.to_csv(db_file, index=False)
        print(f"✅ Base de données créée: {db_file}")
        
        return df
    
    def calculate_molecular_properties(self, formula: str, molar_mass: float = None) -> Dict[str, float]:
        """
        Calcule propriétés moléculaires de base
        
        Args:
            formula: Formule moléculaire (ex: "C2H6N4O4")
            molar_mass: Masse molaire (calculée si None)
            
        Returns:
            Dictionnaire des propriétés
        """
        # Parsing formule simpliste
        elements = self._parse_molecular_formula(formula)
        
        # Masses atomiques
        atomic_masses = {
            'C': 12.011, 'H': 1.008, 'N': 14.007, 'O': 15.999,
            'F': 18.998, 'Cl': 35.453, 'S': 32.066
        }
        
        # Calcul masse molaire si non fournie
        if molar_mass is None:
            molar_mass = sum(atomic_masses.get(elem, 0) * count 
                           for elem, count in elements.items())
        
        # Nombre d'atomes
        total_atoms = sum(elements.values())
        
        # Balance oxygène (%)
        oxygen_balance = self._calculate_oxygen_balance(elements)
        
        # Densité estimée (empirique)
        estimated_density = self._estimate_density(elements, molar_mass)
        
        return {
            'molar_mass': molar_mass,
            'total_atoms': total_atoms,
            'carbon_count': elements.get('C', 0),
            'hydrogen_count': elements.get('H', 0),
            'nitrogen_count': elements.get('N', 0),
            'oxygen_count': elements.get('O', 0),
            'oxygen_balance': oxygen_balance,
            'estimated_density': estimated_density
        }
    
    def _parse_molecular_formula(self, formula: str) -> Dict[str, int]:
        """Parse simple de formule moléculaire"""
        import re
        
        elements = {}
        
        # Pattern: élément + nombre (optionnel)
        pattern = r'([A-Z][a-z]?)(\d*)'
        matches = re.findall(pattern, formula)
        
        for element, count_str in matches:
            count = int(count_str) if count_str else 1
            elements[element] = elements.get(element, 0) + count
        
        return elements
    
    def _calculate_oxygen_balance(self, elements: Dict[str, int]) -> float:
        """
        Calcul balance oxygène (%)
        OB% = (2*O - H - 2*C) * 16 / MW * 100
        """
        C = elements.get('C', 0)
        H = elements.get('H', 0)
        O = elements.get('O', 0)
        
        if C == 0 and H == 0 and O == 0:
            return 0.0
        
        # Masse molaire approximative
        mw = C * 12 + H * 1 + O * 16 + elements.get('N', 0) * 14
        
        if mw == 0:
            return 0.0
        
        ob = (2 * O - H - 2 * C) * 16 / mw * 100
        return round(ob, 2)
    
    def _estimate_density(self, elements: Dict[str, int], molar_mass: float) -> float:
        """
        Estimation densité basée sur composition atomique
        """
        # Formule empirique simpliste
        C = elements.get('C', 0)
        H = elements.get('H', 0)
        N = elements.get('N', 0)
        O = elements.get('O', 0)
        
        total = C + H + N + O
        if total == 0:
            return 1.0
        
        # Contribution pondérée (empirique)
        density_contrib = (
            C * 0.08 +    # Carbone: contribution faible
            H * 0.02 +    # Hydrogène: très faible
            N * 0.15 +    # Azote: contribution élevée
            O * 0.12      # Oxygène: contribution moyenne-élevée
        )
        
        # Densité de base + contribution
        base_density = 1.2 + density_contrib * (molar_mass / 100)
        
        return round(min(max(base_density, 0.8), 2.5), 3)
    
    def predict_kamlet_jacobs(self, density: float, heat_formation: float, 
                            molar_mass: float, elements: Dict[str, int]) -> Dict[str, float]:
        """
        Prédictions Kamlet-Jacobs (formules empiriques)
        
        Args:
            density: Densité (g/cm³)
            heat_formation: Enthalpie formation (kJ/mol)
            molar_mass: Masse molaire
            elements: Composition atomique
            
        Returns:
            VoD et Pcj prédites
        """
        # Paramètres Kamlet-Jacobs
        C = elements.get('C', 0)
        H = elements.get('H', 0)
        N = elements.get('N', 0)
        O = elements.get('O', 0)
        
        # Heat of explosion approximative (kJ/g)
        # Simplification: -ΔHf / MW (conversion approximative)
        q_cal_g = max(-heat_formation / molar_mass, 0.1)  # Éviter valeurs négatives
        
        # Volume gazeux (approximation Kamlet-Jacobs)
        # N_products = estimation produits gazeux
        n_gas = (C + H/4 + N/2)  # CO2 + H2O + N2 approximatif
        n_gas_per_g = n_gas / molar_mass * 1000  # moles/g * 1000
        
        # Kamlet-Jacobs VoD
        phi = n_gas_per_g * (q_cal_g ** 0.5)
        vod_kmj = 1.01 * (density ** 0.5) * phi  # km/s
        vod_ms = vod_kmj * 1000  # m/s
        
        # Kamlet-Jacobs Pcj
        pcj_kbar = 15.58 * (density ** 2) * phi
        pcj_gpa = pcj_kbar / 10  # GPa
        
        return {
            'vod_kamlet_jacobs_ms': round(vod_ms, 0),
            'pcj_kamlet_jacobs_gpa': round(pcj_gpa, 1),
            'phi_parameter': round(phi, 3),
            'heat_explosion_approx_kjg': round(q_cal_g, 2)
        }
    
    def predict_keshavarz(self, elements: Dict[str, int], density: float) -> Dict[str, float]:
        """
        Prédictions Keshavarz (formules empiriques améliorées)
        """
        C = elements.get('C', 0)
        H = elements.get('H', 0)
        N = elements.get('N', 0)
        O = elements.get('O', 0)
        
        # Keshavarz VoD (version simplifiée)
        # D = A * (NM0)^B * (ρ^C)
        # Où NM0 = moyenne géométrique des atomes
        
        total_atoms = C + H + N + O
        if total_atoms == 0:
            return {'vod_keshavarz_ms': 0, 'pcj_keshavarz_gpa': 0}
        
        # Paramètre NM0 (simplifié)
        if N > 0 and O > 0:
            nm0 = (N * O) ** 0.5 / total_atoms * 100
        else:
            nm0 = total_atoms
        
        # Coefficients Keshavarz approximatifs
        A = 1.124
        B = 0.5
        C = 0.5
        
        vod_kesh = A * (nm0 ** B) * (density ** C) * 1000  # m/s
        
        # Pcj Keshavarz (empirique)
        pcj_kesh = 0.365 * (density ** 1.8) * (nm0 ** 0.7)
        
        return {
            'vod_keshavarz_ms': round(vod_kesh, 0),
            'pcj_keshavarz_gpa': round(pcj_kesh, 1),
            'nm0_parameter': round(nm0, 3)
        }
    
    def predict_ml_models(self, features: List[float]) -> Dict[str, float]:
        """
        Prédictions par modèles ML (si entrainés)
        """
        if not SKLEARN_AVAILABLE:
            return {'ml_status': 'sklearn_unavailable'}
        
        predictions = {}
        
        for property_name, model in self.ml_models.items():
            try:
                # Normalisation
                if property_name in self.scalers:
                    features_scaled = self.scalers[property_name].transform([features])
                else:
                    features_scaled = [features]
                
                pred = model.predict(features_scaled)[0]
                predictions[f"{property_name}_ml"] = round(pred, 2)
                
            except Exception as e:
                predictions[f"{property_name}_ml_error"] = str(e)
        
        return predictions
    
    def full_prediction(self, molecular_formula: str, density: float = None, 
                       heat_formation: float = None) -> Dict[str, Any]:
        """
        Pipeline complet de prédiction
        
        Args:
            molecular_formula: Formule (ex: "C2H6N4O4")
            density: Densité g/cm³ (estimée si None)
            heat_formation: ΔHf kJ/mol (estimée si None)
            
        Returns:
            Prédictions complètes
        """
        results = {
            'molecular_formula': molecular_formula,
            'prediction_methods': []
        }
        
        try:
            # 1. Propriétés moléculaires
            mol_props = self.calculate_molecular_properties(molecular_formula)
            results.update(mol_props)
            results['prediction_methods'].append('✅ Propriétés moléculaires')
            
            # 2. Paramètres par défaut si manquants
            if density is None:
                density = mol_props['estimated_density']
                results['density_source'] = 'estimated'
            else:
                results['density_source'] = 'provided'
            
            results['density_gcc'] = density
            
            if heat_formation is None:
                # Estimation très grossière basée sur composition
                elements = self._parse_molecular_formula(molecular_formula)
                heat_formation = self._estimate_heat_formation(elements)
                results['heat_formation_source'] = 'estimated'
            else:
                results['heat_formation_source'] = 'provided'
            
            results['heat_formation_kjmol'] = heat_formation
            
            # 3. Prédictions Kamlet-Jacobs
            elements = self._parse_molecular_formula(molecular_formula)
            kj_pred = self.predict_kamlet_jacobs(
                density, heat_formation, mol_props['molar_mass'], elements
            )
            results.update(kj_pred)
            results['prediction_methods'].append('✅ Kamlet-Jacobs')
            
            # 4. Prédictions Keshavarz
            kesh_pred = self.predict_keshavarz(elements, density)
            results.update(kesh_pred)
            results['prediction_methods'].append('✅ Keshavarz')
            
            # 5. ML si disponible
            if SKLEARN_AVAILABLE and self.ml_models:
                features = [
                    density, mol_props['molar_mass'], mol_props['oxygen_balance'],
                    mol_props['nitrogen_count'], mol_props['oxygen_count']
                ]
                ml_pred = self.predict_ml_models(features)
                results.update(ml_pred)
                results['prediction_methods'].append('✅ ML Models')
            
            # 6. Résumé final
            results['summary'] = {
                'vod_range_ms': [
                    results.get('vod_kamlet_jacobs_ms', 0),
                    results.get('vod_keshavarz_ms', 0)
                ],
                'pcj_range_gpa': [
                    results.get('pcj_kamlet_jacobs_gpa', 0),
                    results.get('pcj_keshavarz_gpa', 0)
                ]
            }
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            results['prediction_methods'].append(f'❌ Erreur: {e}')
            return results
    
    def _estimate_heat_formation(self, elements: Dict[str, int]) -> float:
        """
        Estimation très approximative de l'enthalpie de formation
        """
        # Contributions atomiques approximatives (kJ/mol)
        atomic_contrib = {
            'C': 20.0,    # Contribution carbone
            'H': -10.0,   # Hydrogène stabilisant
            'N': 50.0,    # Azote déstabilisant
            'O': 30.0     # Oxygène déstabilisant
        }
        
        total_contrib = sum(atomic_contrib.get(elem, 0) * count 
                          for elem, count in elements.items())
        
        return total_contrib
    
    def train_ml_models(self) -> Dict[str, str]:
        """
        Entraîne modèles ML sur base de données expérimentale
        """
        if not SKLEARN_AVAILABLE:
            return {'status': 'sklearn_unavailable'}
        
        if self.experimental_data.empty:
            return {'status': 'no_data'}
        
        df = self.experimental_data.copy()
        
        # Features
        feature_cols = ['density_gcc', 'oxygen_balance', 'heat_formation_kjmol']
        if not all(col in df.columns for col in feature_cols):
            return {'status': 'missing_columns'}
        
        X = df[feature_cols].fillna(0)
        
        training_results = {}
        
        # Entraîner pour VoD
        if 'vod_ms' in df.columns:
            y_vod = df['vod_ms'].dropna()
            X_vod = X.loc[y_vod.index]
            
            if len(y_vod) >= 3:  # Minimum pour entraînement
                try:
                    # Random Forest
                    rf_vod = RandomForestRegressor(n_estimators=10, random_state=42)
                    rf_vod.fit(X_vod, y_vod)
                    self.ml_models['vod'] = rf_vod
                    
                    # Scaler
                    scaler_vod = StandardScaler()
                    scaler_vod.fit(X_vod)
                    self.scalers['vod'] = scaler_vod
                    
                    training_results['vod'] = 'success'
                except Exception as e:
                    training_results['vod'] = f'error: {e}'
        
        # Entraîner pour Pcj
        if 'pcj_gpa' in df.columns:
            y_pcj = df['pcj_gpa'].dropna()
            X_pcj = X.loc[y_pcj.index]
            
            if len(y_pcj) >= 3:
                try:
                    rf_pcj = RandomForestRegressor(n_estimators=10, random_state=42)
                    rf_pcj.fit(X_pcj, y_pcj)
                    self.ml_models['pcj'] = rf_pcj
                    
                    scaler_pcj = StandardScaler()
                    scaler_pcj.fit(X_pcj)
                    self.scalers['pcj'] = scaler_pcj
                    
                    training_results['pcj'] = 'success'
                except Exception as e:
                    training_results['pcj'] = f'error: {e}'
        
        return training_results


# Test si exécuté directement
if __name__ == "__main__":
    print("🔥 Test IAM_PerformancePredictor")
    print("=" * 50)
    
    predictor = IAM_PerformancePredictor()
    
    # Test prédiction TNT
    formula_tnt = "C7H5N3O6"
    print(f"Test avec TNT: {formula_tnt}")
    
    results = predictor.full_prediction(formula_tnt, density=1.654, heat_formation=67.4)
    
    print("\nRésultats prédiction:")
    for method in results.get('prediction_methods', []):
        print(f"  {method}")
    
    print(f"\nVoD Kamlet-Jacobs: {results.get('vod_kamlet_jacobs_ms', 'N/A')} m/s")
    print(f"VoD Keshavarz: {results.get('vod_keshavarz_ms', 'N/A')} m/s")
    print(f"Pcj Kamlet-Jacobs: {results.get('pcj_kamlet_jacobs_gpa', 'N/A')} GPa")
    
    # Test entraînement ML
    print("\n🤖 Test entraînement ML:")
    ml_results = predictor.train_ml_models()
    for target, status in ml_results.items():
        print(f"  {target}: {status}")
