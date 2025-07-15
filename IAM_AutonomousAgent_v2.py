"""
IAM Autonomous Agent v2.0
Plateforme autonome intelligente avec chat et génération de modules IA
"""

import os
import json
import logging
import subprocess
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI


# Configuration
app = Flask(__name__)
CORS(app, origins=["*"], allow_headers=["*"], methods=["*"],
     supports_credentials=True)


class IAMAutonomousAgent:
    """Agent autonome intelligent pour la génération et test de modules"""
    
    def __init__(self):
        # Configuration OpenAI
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  ATTENTION: OPENAI_API_KEY non définie.")
            print("📋 Mode DÉMO activé - génération de code statique disponible.")
            self.client = None
            self.demo_mode = True
        else:
            try:
                self.client = OpenAI()
                self.demo_mode = False
                print("✅ OpenAI API configurée - Mode IA complet")
            except Exception as e:
                print(f"❌ Erreur OpenAI: {e}")
                print("📋 Mode DÉMO activé")
                self.client = None
                self.demo_mode = True
        
        self.setup_directories()
        self.setup_logging()
        
    def setup_directories(self):
        """Créer les répertoires nécessaires"""
        self.scripts_dir = "GeneratedScripts"
        self.logs_dir = "IAM_Logs"
        
        for directory in [self.scripts_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def setup_logging(self):
        """Configuration du logging"""
        log_file = os.path.join(self.logs_dir, "autonomous_agent.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_operation(self, operation, status, details):
        """Enregistrer une opération"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "status": status,
            "details": details
        }
        
        log_file = os.path.join(self.logs_dir, "operations.json")
        try:
            with open(log_file, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
            
        logs.append(log_entry)
        
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
            
        self.logger.info(f"{operation}: {status} - {details}")
        
    def generate_module(self, module_name, description, requirements=None):
        """Génération automatique d'un module Python"""
        try:
            if self.demo_mode:
                # Mode démo - génération de code statique
                self.log_operation("GENERATE_MODULE", "DEMO", f"Mode démo pour: {module_name}")
                module_code = self.generate_demo_module(module_name, description)
            else:
                # Mode IA avec OpenAI
                prompt = f"""Génére un module Python complet nommé '{module_name}'.

Description: {description}

Exigences:
{requirements if requirements else "Aucune exigence spécifique"}

Le module doit:
1. Être bien documenté avec docstrings
2. Inclure la gestion d'erreurs
3. Avoir des fonctions claires et modulaires
4. Être prêt à l'usage

Génére uniquement le code Python, sans commentaires additionnels."""

                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en développement Python. Génére du code de qualité production."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                
                module_code = response.choices[0].message.content
                
                # Nettoyer le code
                if "```python" in module_code:
                    module_code = module_code.split("```python")[1].split("```")[0].strip()
                elif "```" in module_code:
                    module_code = module_code.split("```")[1].split("```")[0].strip()
            
            # Sauvegarder le module
            module_path = os.path.join(self.scripts_dir, f"{module_name}.py")
            with open(module_path, "w", encoding="utf-8") as f:
                f.write(module_code)
                
            self.log_operation("GENERATE_MODULE", "SUCCESS",
                             f"Module créé: {module_path}")
            
            return {
                "success": True,
                "module_path": module_path,
                "code": module_code,
                "mode": "demo" if self.demo_mode else "ai"
            }
            
        except Exception as e:
            self.log_operation("GENERATE_MODULE", "ERROR", str(e))
            return {"success": False, "error": str(e)}
            
    def generate_test(self, module_name):
        """Génération automatique de tests pour un module"""
        try:
            if not self.client:
                return {"success": False, "error": "API OpenAI non configurée"}
                
            module_path = os.path.join(self.scripts_dir, f"{module_name}.py")
            
            if not os.path.exists(module_path):
                return {"success": False, "error": "Module non trouvé"}
                
            with open(module_path, "r", encoding="utf-8") as f:
                module_code = f.read()
                
            test_prompt = f"""Crée un script de test Python pour le module '{module_name}'.

Code du module:
```python
{module_code}
```

Le script de test doit:
1. Importer le module à tester
2. Tester toutes les fonctions principales
3. Inclure des cas de test positifs et négatifs
4. Utiliser des assertions claires
5. Être exécutable directement

Génére uniquement le code de test Python."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un expert en tests Python. Crée des tests complets et robustes."},
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            test_code = response.choices[0].message.content
            
            # Nettoyer le code de test
            if "```python" in test_code:
                test_code = test_code.split("```python")[1].split("```")[0].strip()
            elif "```" in test_code:
                test_code = test_code.split("```")[1].split("```")[0].strip()
                
            # Sauvegarder le test
            test_path = os.path.join(self.scripts_dir, f"test_{module_name}.py")
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)
                
            self.log_operation("GENERATE_TEST", "SUCCESS",
                             f"Test créé: {test_path}")
            
            return {
                "success": True,
                "test_path": test_path,
                "code": test_code
            }
            
        except Exception as e:
            self.log_operation("GENERATE_TEST", "ERROR", str(e))
            return {"success": False, "error": str(e)}
            
    def run_test(self, module_name):
        """Exécution des tests d'un module"""
        try:
            test_path = os.path.join(self.scripts_dir, f"test_{module_name}.py")
            
            if not os.path.exists(test_path):
                return {"success": False, "error": "Fichier de test non trouvé"}
                
            # Exécuter le test
            result = subprocess.run(
                [sys.executable, test_path],
                capture_output=True,
                text=True,
                cwd=self.scripts_dir
            )
            
            success = result.returncode == 0
            
            self.log_operation("RUN_TEST", "SUCCESS" if success else "FAILED",
                             f"Module: {module_name}")
            
            return {
                "success": success,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            self.log_operation("RUN_TEST", "ERROR", str(e))
            return {"success": False, "error": str(e)}
        
    def generate_demo_module(self, module_name, description):
        """Génération de code de démonstration sans API OpenAI"""
        demo_templates = {
            "calculator": '''"""
Module calculateur automatique
Généré en mode démo IAM
"""

import math

def add(a, b):
    """Addition de deux nombres"""
    return a + b

def multiply(a, b):
    """Multiplication de deux nombres"""
    return a * b

def calculate_density(mass, volume):
    """Calcul de densité"""
    if volume == 0:
        raise ValueError("Le volume ne peut pas être zéro")
    return mass / volume

def main():
    """Fonction principale de démonstration"""
    print("=== Module Calculateur ===")
    print(f"Addition: {add(5, 3)}")
    print(f"Multiplication: {multiply(4, 7)}")
    print(f"Densité (masse=10, volume=2): {calculate_density(10, 2)}")

if __name__ == "__main__":
    main()
''',
            "analyzer": '''"""
Module d'analyse automatique
Généré en mode démo IAM
"""

import os
import json
from datetime import datetime

class DataAnalyzer:
    """Analyseur de données simple"""
    
    def __init__(self):
        self.results = []
    
    def analyze_numbers(self, numbers):
        """Analyse statistique simple"""
        if not numbers:
            return {"error": "Liste vide"}
        
        return {
            "count": len(numbers),
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers)
        }
    
    def save_results(self, filename):
        """Sauvegarde des résultats"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        return f"Résultats sauvés dans {filename}"

def main():
    """Démonstration du module"""
    analyzer = DataAnalyzer()
    test_data = [1, 5, 3, 8, 2, 9, 4]
    
    result = analyzer.analyze_numbers(test_data)
    print("Analyse:", result)
    
    analyzer.results.append(result)
    print(analyzer.save_results("demo_results.json"))

if __name__ == "__main__":
    main()
''',
            "default": '''"""
{module_name} - Module généré automatiquement
Généré en mode démo IAM
Description: {description}
"""

import os
import sys
from datetime import datetime

class {class_name}:
    """Classe principale du module {module_name}"""
    
    def __init__(self):
        self.created_at = datetime.now()
        self.name = "{module_name}"
    
    def process(self, data):
        """Traitement principal des données"""
        print(f"Traitement des données dans {self.name}")
        return {{"status": "success", "data": data, "timestamp": str(self.created_at)}}
    
    def get_info(self):
        """Informations sur le module"""
        return {{
            "name": self.name,
            "description": "{description}",
            "created": str(self.created_at),
            "mode": "demo"
        }}

def main():
    """Fonction principale de démonstration"""
    module = {class_name}()
    print("=== Module {module_name} ===")
    print("Info:", module.get_info())
    print("Test:", module.process("données de test"))

if __name__ == "__main__":
    main()
'''
        }
        
        # Déterminer le template à utiliser
        if "calcul" in description.lower() or "density" in module_name.lower():
            template = demo_templates["calculator"]
        elif "analys" in description.lower() or "data" in module_name.lower():
            template = demo_templates["analyzer"]
        else:
            # Template générique
            class_name = ''.join(word.capitalize() for word in module_name.split('_'))
            template = demo_templates["default"].format(
                module_name=module_name,
                description=description,
                class_name=class_name
            )
        
        return template
    
    def generate_demo_test(self, module_name):
        """Génération de test de démonstration"""
        return f'''"""
Test automatique pour le module {module_name}
Généré en mode démo IAM
"""

import unittest
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import {module_name}
except ImportError as e:
    print(f"Erreur d'import: {{e}}")
    sys.exit(1)

class Test{module_name.replace('_', '').capitalize()}(unittest.TestCase):
    """Tests pour le module {module_name}"""
    
    def setUp(self):
        """Préparation des tests"""
        print(f"Test du module {module_name}")
    
    def test_module_import(self):
        """Test d'import du module"""
        self.assertIsNotNone({module_name})
        print("✅ Import du module réussi")
    
    def test_main_function(self):
        """Test de la fonction main"""
        try:
            {module_name}.main()
            print("✅ Fonction main exécutée")
        except Exception as e:
            self.fail(f"Erreur dans main(): {{e}}")
    
    def test_basic_functionality(self):
        """Test des fonctionnalités de base"""
        # Test basique selon le type de module
        if hasattr({module_name}, 'add'):
            result = {module_name}.add(2, 3)
            self.assertEqual(result, 5)
            print("✅ Test calcul réussi")
        elif hasattr({module_name}, 'DataAnalyzer'):
            analyzer = {module_name}.DataAnalyzer()
            self.assertIsNotNone(analyzer)
            print("✅ Test classe réussi")
        else:
            print("✅ Test basique passé")

def main():
    """Exécution des tests"""
    print("=" * 50)
    print(f"🧪 TESTS AUTOMATIQUES - {module_name}")
    print("=" * 50)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés")
    print("=" * 50)

if __name__ == "__main__":
    main()
'''
