# IAM_AutonomousAgent.py - Plateforme d'agent autonome intelligente

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import json
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import yaml

# Import des modules IAM existants
from IAM_CodeExecutor import IAMCodeExecutor
from IAM_FileManager import IAMFileManager
from IAM_ChatGPT_Integration import IAMChatGPTAgent

app = Flask(__name__)
CORS(app, origins=["*"], allow_headers=["*"], methods=["*"], supports_credentials=True)

class IAMAutonomousAgent:
    def __init__(self):
        # Charger la configuration
        with open("agent_config.yaml", "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.client = OpenAI(api_key=self.config["gpt4_api_key"])
        self.model = self.config.get("gpt4_model", "gpt-4o")
        self.code_executor = IAMCodeExecutor()
        self.file_manager = IAMFileManager()
        
        # Créer les dossiers nécessaires
        os.makedirs("GeneratedScripts", exist_ok=True)
        os.makedirs("IAM_Logs", exist_ok=True)
        
        self.log_file = "IAM_Logs/agent_log.txt"
        self.module_history = "IAM_Logs/module_history.json"
    
    def log_operation(self, operation, status, details=None):
        """Enregistre une opération dans les logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {operation}: {status}"
        if details:
            log_entry += f" - {details}"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def save_module_history(self, module_name, status, result=None):
        """Sauvegarde l'historique des modules"""
        history = []
        if os.path.exists(self.module_history):
            with open(self.module_history, "r", encoding="utf-8") as f:
                history = json.load(f)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module_name,
            "status": status,
            "result": result
        }
        history.append(entry)
        
        with open(self.module_history, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    
    def generate_module(self, name, description, output_type="json"):
        """Génère automatiquement un module Python"""
        try:
            self.log_operation("GENERATE_MODULE", "START", f"Module: {name}")
            
            # Prompt pour générer le module
            prompt = f"""Crée un module Python complet pour: {name}

Description: {description}
Type de sortie: {output_type}

Le module doit:
1. Être une fonction principale nommée '{name}_main(input_data)'
2. Retourner un dictionnaire avec les résultats
3. Inclure une gestion d'erreurs robuste
4. Être documenté avec des docstrings
5. Utiliser des imports standards Python

Exemple de structure:
```python
def {name}_main(input_data):
    \"\"\"
    {description}
    
    Args:
        input_data: Données d'entrée
    
    Returns:
        dict: Résultats du traitement
    \"\"\"
    try:
        # Code principal ici
        result = {{"success": True, "data": "résultat"}}
        return result
    except Exception as e:
        return {{"success": False, "error": str(e)}}

if __name__ == "__main__":
    # Test rapide
    test_data = "données_test"
    print({name}_main(test_data))
```

Génère uniquement le code Python, rien d'autre."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            module_code = response.choices[0].message.content.strip()
            
            # Nettoyer le code (enlever les balises markdown)
            if "```python" in module_code:
                module_code = module_code.split("```python")[1].split("```")[0].strip()
            elif "```" in module_code:
                module_code = module_code.split("```")[1].strip()
            
            # Sauvegarder le module
            module_path = f"GeneratedScripts/{name}.py"
            with open(module_path, "w", encoding="utf-8") as f:
                f.write(module_code)
            
            self.log_operation("GENERATE_MODULE", "SUCCESS", f"Module créé: {module_path}")
            
            # Générer le test automatiquement
            test_success = self.generate_test(name, description)
            
            return {
                "success": True,
                "module_path": module_path,
                "code": module_code,
                "test_generated": test_success
            }
            
        except Exception as e:
            self.log_operation("GENERATE_MODULE", "ERROR", str(e))
            return {"success": False, "error": str(e)}
    
    def generate_test(self, module_name, description):
        """Génère un script de test pour un module"""
        try:
            test_prompt = f"""Crée un script de test Python pour le module '{module_name}'.

Description du module: {description}

Le test doit:
1. Importer le module depuis GeneratedScripts.{module_name}
2. Tester la fonction {module_name}_main() avec des données d'exemple
3. Vérifier que le résultat est correct
4. Afficher "TEST PASSED" ou "TEST FAILED"
5. Gérer les exceptions

Structure attendue:
```python
import sys
import os
sys.path.append('GeneratedScripts')

try:
    from {module_name} import {module_name}_main
    
    # Données de test
    test_data = "exemple"
    
    # Exécution du test
    result = {module_name}_main(test_data)
    
    # Vérification
    if result.get("success"):
        print("TEST PASSED: Module fonctionne correctement")
        print(f"Résultat: {{result}}")
    else:
        print("TEST FAILED: Erreur dans le module")
        print(f"Erreur: {{result.get('error')}}")
        
except Exception as e:
    print(f"TEST FAILED: Exception - {{e}}")
```

Génère uniquement le code Python."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": test_prompt}],
                temperature=0.3
            )
            
            test_code = response.choices[0].message.content.strip()
            
            # Nettoyer le code
            if "```python" in test_code:
                test_code = test_code.split("```python")[1].split("```")[0].strip()
            elif "```" in test_code:
                test_code = test_code.split("```")[1].strip()
            
            # Sauvegarder le test
            test_path = f"test_{module_name}.py"
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)
            
            self.log_operation("GENERATE_TEST", "SUCCESS", f"Test créé: {test_path}")
            return True
            
        except Exception as e:
            self.log_operation("GENERATE_TEST", "ERROR", str(e))
            return False
    
    def run_module_test(self, module_name):
        """Exécute le test d'un module"""
        try:
            test_file = f"test_{module_name}.py"
            if not os.path.exists(test_file):
                return {"success": False, "error": "Fichier de test non trouvé"}
            
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = "TEST PASSED" in result.stdout
            
            self.log_operation("RUN_TEST", "SUCCESS" if success else "FAILED", 
                             f"Module: {module_name}")
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            self.log_operation("RUN_TEST", "ERROR", str(e))
            return {"success": False, "error": str(e)}

# Instance globale de l'agent
agent = IAMAutonomousAgent()

# === ENDPOINTS FLASK ===

@app.route('/generate_module', methods=['POST'])
def generate_module():
    """Endpoint pour générer un module automatiquement"""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    output_type = data.get('output', 'json')
    
    if not name or not description:
        return jsonify({"error": "Nom et description requis"}), 400
    
    result = agent.generate_module(name, description, output_type)
    
    if result["success"]:
        # Exécuter le test automatiquement
        test_result = agent.run_module_test(name)
        result["test_result"] = test_result
        
        # Sauvegarder dans l'historique
        agent.save_module_history(name, "GENERATED", result)
    
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint pour le chat avec l'IA"""
    try:
        data = request.json
        message = data.get('message', '')
        image_data = data.get('image')
        history = data.get('history', [])
        
        # Préparer les messages pour OpenAI
        messages = [
            {"role": "system", "content": "Tu es un assistant IA expert en chimie computationnelle et en développement Python. Tu aides l'utilisateur avec des questions générales et peux analyser des images. Réponds en français de manière claire et utile."}
        ]
        
        # Ajouter l'historique
        for msg in history[-10:]:  # Garder seulement les 10 derniers messages
            messages.append(msg)
        
        # Message utilisateur actuel
        user_message = {"role": "user", "content": message}
        
        # Si une image est fournie, l'ajouter au message
        if image_data:
            user_message["content"] = [
                {"type": "text", "text": message if message else "Analyse cette image s'il te plaît."},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        
        messages.append(user_message)
        
        # Appel à OpenAI
        response = client.chat.completions.create(
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
        logger.error(f"Erreur dans le chat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test_module', methods=['POST'])
def test_module():
    """Endpoint pour tester un module"""
    data = request.get_json()
    module_name = data.get('module_name')
    
    if not module_name:
        return jsonify({"error": "Nom du module requis"}), 400
    
    result = agent.run_module_test(module_name)
    return jsonify(result)

@app.route('/list_modules', methods=['GET'])
def list_modules():
    """Liste tous les modules générés"""
    modules = []
    script_dir = "GeneratedScripts"
    
    if os.path.exists(script_dir):
        for file in os.listdir(script_dir):
            if file.endswith('.py'):
                module_name = file[:-3]  # Enlever .py
                modules.append({
                    "name": module_name,
                    "path": os.path.join(script_dir, file),
                    "size": os.path.getsize(os.path.join(script_dir, file)),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(script_dir, file))
                    ).isoformat()
                })
    
    return jsonify({"modules": modules})

@app.route('/run_shell', methods=['POST'])
def run_shell():
    """Exécute une commande shell"""
    data = request.get_json()
    command = data.get('command')
    
    if not command:
        return jsonify({"error": "Commande requise"}), 400
    
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        
        return jsonify({
            "success": True,
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/write_file', methods=['POST'])
def write_file():
    """Écrit un fichier"""
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    
    if not filename or content is None:
        return jsonify({"error": "Nom de fichier et contenu requis"}), 400
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        agent.log_operation("WRITE_FILE", "SUCCESS", f"Fichier: {filename}")
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/log_feedback', methods=['POST'])
def log_feedback():
    """Enregistre un feedback utilisateur"""
    data = request.get_json()
    feedback = data.get('feedback')
    task = data.get('task', 'GENERAL')
    level = data.get('level', 'INFO')
    
    agent.log_operation(f"FEEDBACK_{level}", task, feedback)
    return jsonify({"success": True})

@app.route('/run_backup', methods=['POST'])
def run_backup():
    """Lance une sauvegarde complète"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"IAM_Backup_{timestamp}"
        
        # Créer une copie des scripts générés
        if os.path.exists("GeneratedScripts"):
            shutil.copytree("GeneratedScripts", f"{backup_dir}/GeneratedScripts")
        
        # Copier les logs
        if os.path.exists("IAM_Logs"):
            shutil.copytree("IAM_Logs", f"{backup_dir}/IAM_Logs")
        
        agent.log_operation("BACKUP", "SUCCESS", f"Dossier: {backup_dir}")
        return jsonify({"success": True, "backup": backup_dir})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    })

# Nouvelle route pour servir l'interface web
@app.route('/')
def serve_interface():
    return '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 IAM Agent Autonome - Interface Intégrée</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            background: #2ecc71;
            color: white;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
        }
        .section h3 {
            color: #2c3e50;
            margin-top: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }
        .form-group textarea {
            height: 80px;
            resize: vertical;
        }
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #2980b9;
        }
        .btn.primary {
            background: #2ecc71;
        }
        .btn.primary:hover {
            background: #27ae60;
        }
        .btn.warning {
            background: #f39c12;
        }
        .btn.warning:hover {
            background: #e67e22;
        }
        .response {
            margin-top: 15px;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        .response.success {
            background: #d5f5d5;
            border: 1px solid #2ecc71;
        }
        .response.error {
            background: #f8d7da;
            border: 1px solid #e74c3c;
        }
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .module-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
        }
        .module-card h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .module-card p {
            margin: 0;
            font-size: 12px;
            color: #6c757d;
        }
        .chat-container {
            height: 400px;
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
            margin-bottom: 15px;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        .chat-message.user {
            background: #3498db;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .chat-message.assistant {
            background: #2ecc71;
            color: white;
        }
        .chat-message.system {
            background: #95a5a6;
            color: white;
            text-align: center;
            max-width: 100%;
        }
        .chat-input-container {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }
        .chat-input {
            flex: 1;
            min-height: 60px;
            resize: vertical;
        }
        .chat-send-btn {
            height: 60px;
            background: #2ecc71;
            border: none;
            color: white;
            border-radius: 5px;
            padding: 0 20px;
            cursor: pointer;
            font-weight: bold;
        }
        .chat-send-btn:hover {
            background: #27ae60;
        }
        .chat-send-btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .image-preview {
            max-width: 200px;
            max-height: 200px;
            border-radius: 5px;
            margin: 5px 0;
        }
        .file-input-label {
            background: #f39c12;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        .file-input-label:hover {
            background: #e67e22;
        }
        .chat-message pre {
            background: rgba(0,0,0,0.1);
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }
        .chat-message code {
            background: rgba(0,0,0,0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 IAM Agent Autonome</h1>
            <p>Interface intégrée - Génération IA de modules Python</p>
            <div class="status">🟢 En ligne - Agent opérationnel</div>
        </div>

        <!-- Section Chat IA -->
        <div class="section">
            <h3>💬 Chat avec l'Agent IA</h3>
            <p><strong>Fonctionnalités :</strong> Questions générales, aide au code, analyse d'images, conseils techniques...</p>
            <div id="chat-container" class="chat-container">
                <div class="chat-message system">
                    🤖 Agent IAM en ligne ! Posez-moi vos questions sur la chimie computationnelle, le code Python, ou uploadez des images pour analyse.
                </div>
            </div>
            <div class="chat-input-container">
                <textarea id="chat-input" class="chat-input" placeholder="Tapez votre message... (Markdown supporté, ex: ```python pour du code)"></textarea>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <label for="image-input" class="file-input-label">📷 Image</label>
                    <input type="file" id="image-input" accept="image/*" style="display: none;" onchange="handleImageUpload(event)">
                    <button id="chat-send" class="chat-send-btn" onclick="sendChatMessage()">▶️ Envoyer</button>
                </div>
            </div>
        </div>

        <!-- Section Génération de Module -->
        <div class="section">
            <h3>🧠 Génération Automatique de Module</h3>
            <p><strong>Exemples à tester :</strong></p>
            <ul>
                <li><strong>density_calculator</strong> : Calcule la densité d'un explosif</li>
                <li><strong>vod_predictor</strong> : Prédit la vitesse de détonation</li>
                <li><strong>molecular_analyzer</strong> : Analyse les propriétés moléculaires</li>
            </ul>
            <div class="form-group">
                <label for="module-name">Nom du module :</label>
                <input type="text" id="module-name" placeholder="ex: density_calculator">
            </div>
            <div class="form-group">
                <label for="module-description">Description complète :</label>
                <textarea id="module-description" placeholder="ex: Module qui calcule la densité d'un explosif à partir de sa formule chimique et de sa structure moléculaire. Utilise des équations empiriques et des données thermodynamiques."></textarea>
            </div>
            <button class="btn primary" onclick="generateModule()">🚀 Générer Module IA</button>
            <div id="generate-response" class="response" style="display: none;"></div>
        </div>

        <!-- Section Modules Générés -->
        <div class="section">
            <h3>📋 Modules Générés</h3>
            <button class="btn" onclick="listModules()">🔄 Actualiser Liste</button>
            <div id="modules-list" class="modules-grid"></div>
        </div>

        <!-- Section Commandes -->
        <div class="section">
            <h3>🖥️ Commandes Système</h3>
            <div class="form-group">
                <label for="shell-command">Commande shell :</label>
                <input type="text" id="shell-command" placeholder="ex: ls -la GeneratedScripts/" value="ls -la GeneratedScripts/">
            </div>
            <button class="btn warning" onclick="runShell()">▶️ Exécuter</button>
            <button class="btn" onclick="runBackup()">💾 Sauvegarde Complète</button>
            <div id="shell-response" class="response" style="display: none;"></div>
        </div>
    </div>

    <script>
        async function apiCall(endpoint, method = 'GET', data = null) {
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    timeout: 60000  // 60 secondes timeout
                };
                
                if (data) {
                    options.body = JSON.stringify(data);
                }

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 60000);
                options.signal = controller.signal;

                const response = await fetch(endpoint, options);
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                return { success: true, data: result };
            } catch (error) {
                if (error.name === 'AbortError') {
                    return { success: false, error: 'Timeout - La génération prend plus de temps que prévu. Vérifiez les modules générés.' };
                }
                return { success: false, error: error.message };
            }
        }

        let chatHistory = [];
        let currentImage = null;

        function formatMessage(text) {
            // Formatage automatique du texte avec support Markdown
            text = text.replace(/```([a-zA-Z]*)\\n([\\s\\S]*?)\\n```/g, '<pre><code class="language-$1">$2</code></pre>');
            text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
            text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            text = text.replace(/\\*(.*?)\\*/g, '<em>$1</em>');
            text = text.replace(/\n/g, '<br>');
            return text;
        }

        function addChatMessage(content, type = 'user', isHtml = false) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}`;
            
            if (isHtml) {
                messageDiv.innerHTML = content;
            } else {
                messageDiv.innerHTML = formatMessage(content);
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function handleImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImage = e.target.result;
                    // Afficher un aperçu
                    const preview = document.createElement('div');
                    preview.innerHTML = `
                        <p>📷 Image sélectionnée : ${file.name}</p>
                        <img src="${currentImage}" class="image-preview" alt="Preview">
                        <button onclick="clearImage()" style="margin-left: 10px; background: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">❌ Supprimer</button>
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
            const sendBtn = document.getElementById('chat-send');
            const message = chatInput.value.trim();
            
            if (!message && !currentImage) return;
            
            // Désactiver le bouton d'envoi
            sendBtn.disabled = true;
            sendBtn.textContent = '⏳ Envoi...';
            
            // Afficher le message utilisateur
            let userMessage = message;
            if (currentImage) {
                userMessage += '<br><img src="' + currentImage + '" class="image-preview" alt="Image utilisateur">';
            }
            addChatMessage(userMessage, 'user', true);
            
            // Ajouter au historique
            const chatData = {
                message: message,
                image: currentImage,
                history: chatHistory
            };
            
            try {
                // Envoyer à l'agent
                const result = await apiCall('/chat', 'POST', chatData);
                
                if (result.success) {
                    addChatMessage(result.data.response, 'assistant');
                    // Mettre à jour l'historique
                    chatHistory.push({role: 'user', content: message});
                    chatHistory.push({role: 'assistant', content: result.data.response});
                } else {
                    addChatMessage('❌ Erreur: ' + result.error, 'system');
                }
            } catch (error) {
                addChatMessage('❌ Erreur de communication: ' + error.message, 'system');
            }
            
            // Nettoyer et réactiver
            chatInput.value = '';
            clearImage();
            sendBtn.disabled = false;
            sendBtn.textContent = '▶️ Envoyer';
        }

        // Envoyer avec Entrée (Shift+Entrée pour nouvelle ligne)
        document.addEventListener('DOMContentLoaded', function() {
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                chatInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendChatMessage();
                    }
                });
            }
        });

        function showResponse(elementId, result, isSuccess = true) {
            const element = document.getElementById(elementId);
            element.style.display = 'block';
            element.className = isSuccess ? 'response success' : 'response error';
            element.textContent = JSON.stringify(result, null, 2);
        }

        async function generateModule() {
            const name = document.getElementById('module-name').value;
            const description = document.getElementById('module-description').value;
            
            if (!name || !description) {
                alert('Veuillez remplir tous les champs');
                return;
            }

            showResponse('generate-response', '🤖 Génération en cours...\\n⏳ L\\'IA analyse votre demande...\\n📝 Création du code Python...\\n⚡ Génération du script de test...\\n\\nCela peut prendre 30-60 secondes, veuillez patienter...', true);

            const data = {
                name: name,
                description: description,
                output: 'json'
            };

            const result = await apiCall('/generate_module', 'POST', data);
            
            if (result.success) {
                showResponse('generate-response', '✅ Module généré avec succès !\\n\\n' + JSON.stringify(result.data, null, 2), true);
                setTimeout(() => {
                    listModules();
                    showResponse('generate-response', '✅ Module généré avec succès !\\n📁 Fichier créé: GeneratedScripts/' + name + '.py\\n🧪 Test automatique: test_' + name + '.py\\n\\n📋 Actualisez la liste des modules ci-dessous', true);
                }, 2000);
            } else {
                if (result.error.includes('Timeout')) {
                    showResponse('generate-response', '⏰ Timeout détecté mais le module pourrait être en cours de génération...\\n\\n🔄 Actualisez la liste des modules dans quelques secondes pour vérifier.\\n\\nErreur: ' + result.error, false);
                    setTimeout(listModules, 5000);
                } else {
                    showResponse('generate-response', '❌ Erreur de génération:\\n' + result.error, false);
                }
            }
        }

        async function listModules() {
            const result = await apiCall('/list_modules');
            const container = document.getElementById('modules-list');
            
            if (result.success && result.data.modules && result.data.modules.length > 0) {
                container.innerHTML = '';
                result.data.modules.forEach(module => {
                    const card = document.createElement('div');
                    card.className = 'module-card';
                    const sizeKB = Math.round(module.size / 1024 * 100) / 100;
                    const modifiedDate = new Date(module.modified).toLocaleString('fr-FR');
                    card.innerHTML = `
                        <h4>📁 ${module.name}</h4>
                        <p><strong>Taille:</strong> ${sizeKB} KB</p>
                        <p><strong>Modifié:</strong> ${modifiedDate}</p>
                        <p><strong>Chemin:</strong> ${module.path}</p>
                        <button class="btn" onclick="testModule('${module.name}')">🧪 Tester</button>
                        <button class="btn" onclick="viewModule('${module.name}')">👁️ Voir Code</button>
                    `;
                    container.appendChild(card);
                });
            } else {
                container.innerHTML = '<p>Aucun module généré. Créez votre premier module ci-dessus ! 🚀</p>';
            }
        }

        async function testModule(moduleName) {
            const result = await apiCall('/test_module', 'POST', { module_name: moduleName });
            alert('Résultat du test:\\n' + JSON.stringify(result, null, 2));
        }

        async function viewModule(moduleName) {
            const result = await apiCall('/run_shell', 'POST', { command: `cat GeneratedScripts/${moduleName}.py` });
            if (result.success && result.data.success) {
                const newWindow = window.open('', '_blank');
                newWindow.document.write(`
                    <html>
                    <head><title>Code: ${moduleName}.py</title></head>
                    <body style="font-family: monospace; padding: 20px; background: #f5f5f5;">
                    <h2>📄 ${moduleName}.py</h2>
                    <pre style="background: white; padding: 15px; border-radius: 5px; overflow: auto;">${result.data.output}</pre>
                    </body>
                    </html>
                `);
            } else {
                alert('Erreur lors de la lecture du fichier');
            }
        }

        async function runShell() {
            const command = document.getElementById('shell-command').value;
            if (!command) {
                alert('Veuillez entrer une commande');
                return;
            }

            const result = await apiCall('/run_shell', 'POST', { command: command });
            showResponse('shell-response', result.success ? result.data : result.error, result.success);
        }

        async function runBackup() {
            showResponse('shell-response', 'Sauvegarde en cours...', true);
            const result = await apiCall('/run_backup', 'POST');
            showResponse('shell-response', result.success ? result.data : result.error, result.success);
        }

        // Charger les modules au démarrage
        window.onload = function() {
            listModules();
        };
    </script>
</body>
</html>'''

if __name__ == "__main__":
    print("🚀 Lancement de la plateforme IAM Autonome")
    print("📡 Endpoints disponibles:")
    print("   POST /generate_module - Générer un module")
    print("   POST /test_module - Tester un module") 
    print("   GET  /list_modules - Lister les modules")
    print("   POST /run_shell - Exécuter commande shell")
    print("   POST /write_file - Écrire un fichier")
    print("   POST /log_feedback - Enregistrer feedback")
    print("   POST /run_backup - Lancer sauvegarde")
    print("   GET  /health - Statut de santé")
    print("")
    print("🌐 Serveur démarré sur http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
