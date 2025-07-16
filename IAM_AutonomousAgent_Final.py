"""
IAM Autonomous Agent v2.0 - Version finale
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
            print("📋 Mode DÉMO activé.")
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
        
    def generate_demo_module(self, module_name, description):
        """Génération de code démo sans API"""
        demo_code = f'''"""
Module {module_name}
{description}

Généré en mode démo par IAM Autonomous Agent
"""

import math
from typing import Any, Optional


class {module_name.title().replace('_', '')}:
    """Classe principale pour {module_name}"""
    
    def __init__(self):
        self.name = "{module_name}"
        self.description = "{description}"
    
    def hello_world(self) -> str:
        """Fonction de démonstration"""
        return f"Hello from {{self.name}}!"
    
    def calculate(self, x: float, y: float) -> float:
        """Calcul simple"""
        return x + y
    
    def get_info(self) -> dict:
        """Information du module"""
        return {{
            "name": self.name,
            "description": self.description,
            "version": "1.0.0"
        }}


def main():
    """Fonction principale de démonstration"""
    module = {module_name.title().replace('_', '')}()
    print(module.hello_world())
    print(f"Calcul: {{module.calculate(5, 3)}}")
    print(f"Info: {{module.get_info()}}")


if __name__ == "__main__":
    main()
'''
        return demo_code
        
    def generate_module(self, module_name, description, requirements=None):
        """Génération automatique d'un module Python"""
        try:
            if self.demo_mode:
                # Mode démo
                self.log_operation("GENERATE_MODULE", "DEMO", 
                                 f"Mode démo: {module_name}")
                module_code = self.generate_demo_module(module_name, 
                                                       description)
            else:
                # Mode IA avec OpenAI
                prompt = f"""Génère un module Python complet nommé '{module_name}'.

Description: {description}

Exigences:
{requirements if requirements else "Aucune exigence spécifique"}

Le module doit:
1. Être bien documenté avec docstrings
2. Inclure la gestion d'erreurs
3. Avoir des fonctions claires et modulaires
4. Être prêt à l'usage

Génère uniquement le code Python, sans commentaires additionnels."""

                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", 
                         "content": "Tu es un expert en développement Python."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                
                module_code = response.choices[0].message.content
                
                # Nettoyer le code
                if "```python" in module_code:
                    parts = module_code.split("```python")
                    if len(parts) > 1:
                        module_code = parts[1].split("```")[0].strip()
                elif "```" in module_code:
                    parts = module_code.split("```")
                    if len(parts) > 1:
                        module_code = parts[1].split("```")[0].strip()
            
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
                return {"success": False, 
                       "error": "API OpenAI non configurée"}
                
            module_path = os.path.join(self.scripts_dir, f"{module_name}.py")
            
            if not os.path.exists(module_path):
                return {"success": False, "error": "Module non trouvé"}
                
            with open(module_path, "r", encoding="utf-8") as f:
                module_code = f.read()
                
            test_prompt = f"""Crée un script de test Python pour '{module_name}'.

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

Génère uniquement le code de test Python."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", 
                     "content": "Tu es un expert en tests Python."},
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            test_code = response.choices[0].message.content
            
            # Nettoyer le code de test
            if "```python" in test_code:
                parts = test_code.split("```python")
                if len(parts) > 1:
                    test_code = parts[1].split("```")[0].strip()
            elif "```" in test_code:
                parts = test_code.split("```")
                if len(parts) > 1:
                    test_code = parts[1].split("```")[0].strip()
                
            # Sauvegarder le test
            test_path = os.path.join(self.scripts_dir, 
                                   f"test_{module_name}.py")
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
            test_path = os.path.join(self.scripts_dir, 
                                   f"test_{module_name}.py")
            
            if not os.path.exists(test_path):
                return {"success": False, 
                       "error": "Fichier de test non trouvé"}
                
            # Exécuter le test
            result = subprocess.run(
                [sys.executable, test_path],
                capture_output=True,
                text=True,
                cwd=self.scripts_dir
            )
            
            success = result.returncode == 0
            
            self.log_operation("RUN_TEST", 
                             "SUCCESS" if success else "FAILED",
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

    def integrate_module_to_backend(self, module_name):
        """Intègre un module généré dans le backend avec API et interface"""
        try:
            if self.demo_mode:
                return {"success": False, "error": "API OpenAI requise pour l'intégration automatique"}
            
            module_path = os.path.join(self.scripts_dir, f"{module_name}.py")
            
            if not os.path.exists(module_path):
                return {"success": False, "error": "Module non trouvé"}
            
            # Lire le code du module
            with open(module_path, "r", encoding="utf-8") as f:
                module_code = f.read()
            
            # Analyser le module pour créer l'intégration
            integration_prompt = f"""Analyse ce module Python et crée une intégration complète pour une plateforme web Flask.

MODULE À INTÉGRER:
```python
{module_code}
```

Génère:
1. CODE D'ENDPOINT Flask pour exposer les fonctions principales via API REST
2. HTML/JavaScript pour l'interface utilisateur dans le layout existant
3. Instructions d'import et d'intégration

Format de réponse:
```ENDPOINTS
# Code Flask pour les endpoints
```

```HTML
<!-- Interface HTML pour le layout -->
```

```INTEGRATION
# Instructions d'intégration
```

Le module doit être accessible via l'interface web avec formulaires appropriés."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un expert en intégration Flask et développement web. Crée des intégrations propres et fonctionnelles."},
                    {"role": "user", "content": integration_prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            integration_content = response.choices[0].message.content
            
            # Extraire les différentes parties
            endpoints_code = ""
            html_interface = ""
            integration_instructions = ""
            
            if "```ENDPOINTS" in integration_content:
                endpoints_code = integration_content.split("```ENDPOINTS")[1].split("```")[0].strip()
            
            if "```HTML" in integration_content:
                html_interface = integration_content.split("```HTML")[1].split("```")[0].strip()
            
            if "```INTEGRATION" in integration_content:
                integration_instructions = integration_content.split("```INTEGRATION")[1].split("```")[0].strip()
            
            # Sauvegarder les fichiers d'intégration
            integration_dir = os.path.join(self.scripts_dir, f"{module_name}_integration")
            os.makedirs(integration_dir, exist_ok=True)
            
            # Fichier d'endpoints
            endpoints_file = os.path.join(integration_dir, f"{module_name}_endpoints.py")
            with open(endpoints_file, "w", encoding="utf-8") as f:
                f.write(f"# Endpoints Flask pour {module_name}\n")
                f.write(f"# Import du module\nfrom GeneratedScripts.{module_name} import *\n\n")
                f.write(endpoints_code)
            
            # Fichier d'interface
            interface_file = os.path.join(integration_dir, f"{module_name}_interface.html")
            with open(interface_file, "w", encoding="utf-8") as f:
                f.write(html_interface)
            
            # Fichier d'instructions
            instructions_file = os.path.join(integration_dir, "integration_guide.md")
            with open(instructions_file, "w", encoding="utf-8") as f:
                f.write(f"# Guide d'intégration pour {module_name}\n\n")
                f.write(integration_instructions)
                f.write(f"\n\n## Fichiers générés:\n")
                f.write(f"- Endpoints: {endpoints_file}\n")
                f.write(f"- Interface: {interface_file}\n")
                f.write(f"- Module original: {module_path}\n")
            
            self.log_operation("INTEGRATE_MODULE", "SUCCESS", 
                             f"Module {module_name} intégré dans {integration_dir}")
            
            return {
                "success": True,
                "integration_dir": integration_dir,
                "endpoints_file": endpoints_file,
                "interface_file": interface_file,
                "instructions_file": instructions_file,
                "endpoints_code": endpoints_code,
                "html_interface": html_interface,
                "instructions": integration_instructions
            }
            
        except Exception as e:
            self.log_operation("INTEGRATE_MODULE", "ERROR", str(e))
            return {"success": False, "error": str(e)}
    
    def apply_integration(self, module_name):
        """Applique automatiquement l'intégration au fichier principal"""
        try:
            integration_dir = os.path.join(self.scripts_dir, f"{module_name}_integration")
            endpoints_file = os.path.join(integration_dir, f"{module_name}_endpoints.py")
            
            if not os.path.exists(endpoints_file):
                return {"success": False, "error": "Fichiers d'intégration non trouvés. Exécutez d'abord integrate_module_to_backend."}
            
            # Lire le code des endpoints
            with open(endpoints_file, "r", encoding="utf-8") as f:
                endpoints_code = f.read()
            
            # Chercher les routes Flask dans le code
            import re
            routes = re.findall(r'@app\.route\([\'"][^\'"]+[\'"][^)]*\)', endpoints_code)
            
            if not routes:
                return {"success": False, "error": "Aucune route Flask trouvée dans l'intégration"}
            
            self.log_operation("APPLY_INTEGRATION", "SUCCESS", 
                             f"Module {module_name} prêt pour intégration manuelle")
            
            return {
                "success": True,
                "routes_found": routes,
                "endpoints_file": endpoints_file,
                "message": f"Fichiers d'intégration prêts pour {module_name}. Consultez {integration_dir} pour les détails."
            }
                
        except Exception as e:
            self.log_operation("APPLY_INTEGRATION", "ERROR", str(e))
            return {"success": False, "error": str(e)}


# Instance globale
agent = IAMAutonomousAgent()


@app.route('/')
def index():
    """Interface web principale"""
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IAM - Plateforme Autonome Intelligente v2.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .container { max-width: 1200px; margin-top: 2rem; }
        .card { 
            border: none; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.95);
        }
        .card-header { 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; 
            border-radius: 15px 15px 0 0 !important;
            text-align: center;
            padding: 1.5rem;
        }
        .btn-primary { 
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        .btn-primary:hover { 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .response-box {
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        .success { 
            background-color: #d4edda; 
            border: 1px solid #c3e6cb; 
            color: #155724; 
        }
        .error { 
            background-color: #f8d7da; 
            border: 1px solid #f5c6cb; 
            color: #721c24; 
        }
        
        /* Styles pour le chat */
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            background: #f8f9fa;
            margin-bottom: 1rem;
        }
        
        .chat-message {
            margin: 0.5rem 0;
            padding: 0.75rem;
            border-radius: 8px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .chat-message.user {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .chat-message.assistant {
            background: #28a745;
            color: white;
            margin-right: auto;
        }
        
        .chat-message.system {
            background: #ffc107;
            color: #212529;
            text-align: center;
            margin: 0 auto;
        }
        
        .chat-input-container {
            display: flex;
            gap: 0.5rem;
            align-items: end;
        }
        
        .image-preview {
            max-width: 200px;
            max-height: 200px;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        .chat-textarea {
            flex: 1;
            resize: vertical;
            min-height: 40px;
            max-height: 120px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h1>🤖 IAM - Plateforme Autonome Intelligente v2.0</h1>
                        <p class="mb-0">Génération automatique de modules Python avec IA</p>
                    </div>
                    <div class="card-body">
                        <!-- Section Génération de Module -->
                        <div class="row">
                            <div class="col-md-6">
                                <h3>📦 Génération de Module</h3>
                                <div class="mb-3">
                                    <label class="form-label">Nom du module:</label>
                                    <input type="text" id="module-name" class="form-control" placeholder="ex: calculator">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Description:</label>
                                    <textarea id="module-description" class="form-control" rows="3" placeholder="Décrivez la fonctionnalité..."></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Exigences (optionnel):</label>
                                    <textarea id="module-requirements" class="form-control" rows="2" placeholder="Exigences spéciales..."></textarea>
                                </div>
                                <button class="btn btn-primary" onclick="generateModule()">🚀 Générer Module</button>
                                <div id="generate-response"></div>
                            </div>
                            
                            <!-- Section Test -->
                            <div class="col-md-6">
                                <h3>🧪 Test et Validation</h3>
                                <div class="mb-3">
                                    <label class="form-label">Module à tester:</label>
                                    <input type="text" id="test-module-name" class="form-control" placeholder="Nom du module">
                                </div>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" onclick="generateTest()">📝 Générer Test</button>
                                    <button class="btn btn-success" onclick="runTest()">▶️ Exécuter Test</button>
                                    <button class="btn btn-warning" onclick="integrateModule()">🔧 Intégrer au Backend</button>
                                </div>
                                <div id="test-response"></div>
                            </div>
                        </div>
                        
                        <hr class="my-4">
                        
                        <!-- Section Intégration Backend -->
                        <div class="row">
                            <div class="col-md-12">
                                <h3>🔧 Intégration Backend</h3>
                                <p class="text-muted">Intégrez automatiquement vos modules générés dans le backend avec API et interface web.</p>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Module à intégrer:</label>
                                            <input type="text" id="integration-module-name" class="form-control" placeholder="Nom du module">
                                        </div>
                                        <div class="d-grid gap-2">
                                            <button class="btn btn-primary" onclick="generateIntegration()">🔧 Générer Intégration</button>
                                            <button class="btn btn-success" onclick="applyIntegration()">✅ Appliquer Intégration</button>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="alert alert-info">
                                            <h6>📋 Processus d'intégration :</h6>
                                            <ol class="mb-0">
                                                <li>Génère les endpoints API Flask</li>
                                                <li>Crée l'interface utilisateur HTML</li>
                                                <li>Produit les instructions d'intégration</li>
                                                <li>Prépare les fichiers pour application</li>
                                            </ol>
                                        </div>
                                    </div>
                                </div>
                                <div id="integration-response"></div>
                            </div>
                        </div>
                        
                        <hr class="my-4">
                        
                        <!-- Section Chat IA -->
                        <div class="row">
                            <div class="col-md-12">
                                <h3>💬 Chat IA Assistant</h3>
                                <div id="chat-container" class="chat-container">
                                    <div class="chat-message system">
                                        🤖 Assistant IA prêt ! Posez vos questions sur la chimie computationnelle, Python, ou envoyez des images.
                                    </div>
                                </div>
                                <div class="chat-input-container">
                                    <textarea id="chat-input" class="form-control chat-textarea" placeholder="Tapez votre message..."></textarea>
                                    <input type="file" id="image-input" accept="image/*" style="display: none;" onchange="handleImageUpload(event)">
                                    <button class="btn btn-outline-secondary" onclick="document.getElementById('image-input').click()">📷</button>
                                    <button id="chat-send" class="btn btn-primary" onclick="sendChatMessage()">▶️ Envoyer</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function apiCall(endpoint, method = 'GET', data = null) {
            const config = {
                method: method,
                headers: { 'Content-Type': 'application/json' }
            };
            
            if (data) {
                config.body = JSON.stringify(data);
            }
            
            const response = await fetch(endpoint, config);
            return await response.json();
        }

        let chatHistory = [];
        let currentImage = null;

        function addChatMessage(content, type = 'user') {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}`;
            messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function handleImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImage = e.target.result;
                    const preview = document.createElement('div');
                    preview.innerHTML = `
                        <p>📷 Image: ${file.name}</p>
                        <img src="${currentImage}" class="image-preview" alt="Preview">
                        <button onclick="clearImage()">❌ Supprimer</button>
                    `;
                    const chatInput = document.getElementById('chat-input');
                    const existing = document.getElementById('image-preview-container');
                    if (existing) existing.remove();
                    preview.id = 'image-preview-container';
                    chatInput.parentNode.insertBefore(preview, chatInput);
                };
                reader.readAsDataURL(file);
            }
        }

        function clearImage() {
            currentImage = null;
            const preview = document.getElementById('image-preview-container');
            if (preview) preview.remove();
            document.getElementById('image-input').value = '';
        }

        async function sendChatMessage() {
            const chatInput = document.getElementById('chat-input');
            const message = chatInput.value.trim();
            
            if (!message && !currentImage) return;
            
            let userMessage = message;
            if (currentImage) {
                userMessage += '<br><img src="' + currentImage + '" class="image-preview" alt="Image">';
            }
            addChatMessage(userMessage, 'user');
            
            const chatData = {
                message: message,
                image: currentImage,
                history: chatHistory
            };
            
            try {
                const result = await apiCall('/chat', 'POST', chatData);
                
                if (result.success) {
                    addChatMessage(result.data.response, 'assistant');
                    chatHistory.push({role: 'user', content: message});
                    chatHistory.push({role: 'assistant', content: result.data.response});
                } else {
                    addChatMessage('❌ Erreur: ' + result.error, 'system');
                }
            } catch (error) {
                addChatMessage('❌ Erreur: ' + error.message, 'system');
            }
            
            chatInput.value = '';
            clearImage();
        }

        function showResponse(elementId, result, isSuccess = true) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="response-box ${isSuccess ? 'success' : 'error'}">${JSON.stringify(result, null, 2)}</div>`;
        }

        async function generateModule() {
            const name = document.getElementById('module-name').value;
            const description = document.getElementById('module-description').value;
            const requirements = document.getElementById('module-requirements').value;
            
            if (!name || !description) {
                alert('Veuillez remplir le nom et la description');
                return;
            }
            
            try {
                const result = await apiCall('/generate_module', 'POST', {
                    module_name: name,
                    description: description,
                    requirements: requirements
                });
                
                showResponse('generate-response', result, result.success);
            } catch (error) {
                showResponse('generate-response', {error: error.message}, false);
            }
        }

        async function generateTest() {
            const moduleName = document.getElementById('test-module-name').value;
            
            if (!moduleName) {
                alert('Veuillez spécifier le nom du module');
                return;
            }
            
            try {
                const result = await apiCall('/generate_test', 'POST', {
                    module_name: moduleName
                });
                
                showResponse('test-response', result, result.success);
            } catch (error) {
                showResponse('test-response', {error: error.message}, false);
            }
        }

        async function runTest() {
            const moduleName = document.getElementById('test-module-name').value;
            
            if (!moduleName) {
                alert('Veuillez spécifier le nom du module');
                return;
            }
            
            try {
                const result = await apiCall('/run_test', 'POST', {
                    module_name: moduleName
                });
                
                showResponse('test-response', result, result.success);
            } catch (error) {
                showResponse('test-response', {error: error.message}, false);
            }
        }

        async function integrateModule() {
            const moduleName = document.getElementById('test-module-name').value;
            
            if (!moduleName) {
                alert('Veuillez spécifier le nom du module à intégrer');
                return;
            }
            
            // Utiliser le même nom pour l'intégration
            document.getElementById('integration-module-name').value = moduleName;
            generateIntegration();
        }

        async function generateIntegration() {
            const moduleName = document.getElementById('integration-module-name').value;
            
            if (!moduleName) {
                alert('Veuillez spécifier le nom du module à intégrer');
                return;
            }
            
            try {
                showResponse('integration-response', {message: '🔧 Génération de l\\'intégration en cours...'}, true);
                
                const result = await apiCall('/integrate_module', 'POST', {
                    module_name: moduleName
                });
                
                if (result.success) {
                    const response = {
                        success: true,
                        message: `✅ Intégration générée pour ${moduleName}`,
                        details: {
                            integration_dir: result.integration_dir,
                            endpoints_file: result.endpoints_file,
                            interface_file: result.interface_file,
                            instructions_file: result.instructions_file
                        }
                    };
                    showResponse('integration-response', response, true);
                } else {
                    showResponse('integration-response', result, false);
                }
            } catch (error) {
                showResponse('integration-response', {error: error.message}, false);
            }
        }

        async function applyIntegration() {
            const moduleName = document.getElementById('integration-module-name').value;
            
            if (!moduleName) {
                alert('Veuillez spécifier le nom du module');
                return;
            }
            
            try {
                showResponse('integration-response', {message: '✅ Application de l\\'intégration...'}, true);
                
                const result = await apiCall('/apply_integration', 'POST', {
                    module_name: moduleName
                });
                
                if (result.success) {
                    const response = {
                        success: true,
                        message: `🎉 Intégration prête pour ${moduleName}`,
                        details: {
                            routes_found: result.routes_found,
                            endpoints_file: result.endpoints_file,
                            instructions: result.message
                        }
                    };
                    showResponse('integration-response', response, true);
                } else {
                    showResponse('integration-response', result, false);
                }
            } catch (error) {
                showResponse('integration-response', {error: error.message}, false);
            }
        }

        // Envoyer avec Entrée
        document.getElementById('chat-input').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    </script>
</body>
</html>"""
    return html_content


@app.route('/generate_module', methods=['POST'])
def generate_module():
    """Endpoint pour générer un module"""
    try:
        data = request.json
        result = agent.generate_module(
            data['module_name'],
            data['description'],
            data.get('requirements')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate_test', methods=['POST'])
def generate_test():
    """Endpoint pour générer un test"""
    try:
        data = request.json
        result = agent.generate_test(data['module_name'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/run_test', methods=['POST'])
def run_test():
    """Endpoint pour exécuter un test"""
    try:
        data = request.json
        result = agent.run_test(data['module_name'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint pour le chat avec l'IA"""
    try:
        if not agent.client:
            return jsonify({
                'success': False,
                'error': 'API OpenAI non configurée'
            }), 400
            
        data = request.json
        message = data.get('message', '')
        image_data = data.get('image')
        history = data.get('history', [])
        
        # Messages pour OpenAI
        messages = [
            {"role": "system", 
             "content": "Tu es un assistant IA expert en chimie computationnelle et Python."}
        ]
        
        # Historique (10 derniers messages)
        for msg in history[-10:]:
            messages.append(msg)
        
        # Message actuel
        user_message = {"role": "user", "content": message}
        
        # Image si fournie
        if image_data:
            user_message["content"] = [
                {"type": "text", 
                 "text": message if message else "Analyse cette image."},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        
        messages.append(user_message)
        
        # Appel OpenAI
        response = agent.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'data': {'response': response_text}
        })
        
    except Exception as e:
        agent.logger.error(f"Erreur chat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/integrate_module', methods=['POST'])
def integrate_module():
    """Endpoint pour intégrer un module au backend"""
    try:
        data = request.json
        result = agent.integrate_module_to_backend(data['module_name'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/apply_integration', methods=['POST'])
def apply_integration():
    """Endpoint pour appliquer l'intégration"""
    try:
        data = request.json
        result = agent.apply_integration(data['module_name'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Démarrage IAM Plateforme Autonome v2.0")
    print("📡 Interface: http://localhost:5002")
    print("💬 Chat IA avec support d'images")
    print("🤖 Génération automatique de modules")
    print("🧪 Tests automatisés")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
