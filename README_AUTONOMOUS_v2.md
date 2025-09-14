# 🤖 IAM - Plateforme Autonome Intelligente v2.0

## 📋 Description

La Plateforme Autonome Intelligente IAM est un système complet qui combine :
- **Génération automatique de modules Python** avec IA
- **Tests automatisés** des modules générés
- **Chat intelligent** avec support d'images
- **Interface web moderne** et intuitive

## 🚀 Fonctionnalités

### 1. Génération de Modules IA 🤖
- Génération automatique de code Python de qualité production
- Personnalisation via descriptions et exigences
- Sauvegarde automatique dans `GeneratedScripts/`
- Documentation automatique avec docstrings

### 2. Tests Automatisés 🧪
- Génération automatique de tests unitaires
- Exécution des tests avec rapport détaillé
- Validation du code généré
- Gestion des erreurs et debug

### 3. Chat IA Assistant 💬
- Conversation en temps réel avec GPT-4o
- Support d'images avec analyse IA
- Formatage automatique du code
- Historique de conversation

### 4. Interface Web 🌐
- Interface moderne avec Bootstrap
- Design responsive
- Notifications en temps réel
- Gestion des fichiers

## 📦 Installation et Configuration

### Prérequis
```bash
# Dépendances Python
pip install flask flask-cors openai

# Variables d'environnement
export OPENAI_API_KEY="votre-clé-api-openai"
```

### Démarrage
```bash
# Option 1: Script de démarrage
./start_autonomous_agent_v2.sh

# Option 2: Démarrage direct
python IAM_AutonomousAgent_v2.py

# Option 3: Avec clé API temporaire
OPENAI_API_KEY='votre-clé' python IAM_AutonomousAgent_v2.py
```

## 🔧 Utilisation

### Interface Web
1. Ouvrir http://localhost:5002 dans votre navigateur
2. Utiliser les sections :
   - **Génération de Module** : Créer de nouveaux modules Python
   - **Test et Validation** : Tester les modules créés
   - **Chat IA Assistant** : Assistance conversationnelle

### API REST

#### Génération de Module
```bash
curl -X POST http://localhost:5002/generate_module \\
  -H "Content-Type: application/json" \\
  -d '{
    "module_name": "calculator",
    "description": "Module de calculs mathématiques",
    "requirements": "Inclure fonctions trigonométriques"
  }'
```

#### Génération de Test
```bash
curl -X POST http://localhost:5002/generate_test \\
  -H "Content-Type: application/json" \\
  -d '{"module_name": "calculator"}'
```

#### Exécution de Test
```bash
curl -X POST http://localhost:5002/run_test \\
  -H "Content-Type: application/json" \\
  -d '{"module_name": "calculator"}'
```

#### Chat IA
```bash
curl -X POST http://localhost:5002/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Explique la chimie quantique",
    "history": []
  }'
```

## 📁 Structure des Fichiers

```
IAM/
├── IAM_AutonomousAgent_v2.py          # Application principale
├── start_autonomous_agent_v2.sh       # Script de démarrage
├── GeneratedScripts/                  # Modules générés
│   ├── module_name.py                 # Modules Python
│   └── test_module_name.py           # Tests associés
└── IAM_Logs/                         # Logs système
    ├── autonomous_agent.log           # Logs de l'agent
    └── operations.json                # Historique des opérations
```

## 🔍 Modes de Fonctionnement

### Mode Complet (avec API OpenAI)
- Toutes les fonctionnalités disponibles
- Génération IA de modules et tests
- Chat intelligent avec images
- Analyse avancée

### Mode Interface Seule (sans API)
- Interface web fonctionnelle
- Gestion des fichiers existants
- Tests de modules locaux
- Pas de génération IA

## 📊 Surveillance et Logs

### Logs Système
- `IAM_Logs/autonomous_agent.log` : Logs détaillés
- `platform_v2.log` : Logs de démarrage
- `IAM_Logs/operations.json` : Historique JSON

### Monitoring
```bash
# Vérifier le processus
ps aux | grep IAM_AutonomousAgent_v2

# Surveiller les logs
tail -f IAM_Logs/autonomous_agent.log

# Tester la connectivité
curl http://localhost:5002/
```

## 🛠️ Dépannage

### Problèmes Courants

#### Port 5002 occupé
```bash
# Changer le port dans le code
app.run(host='0.0.0.0', port=5003, debug=True)
```

#### API OpenAI non configurée
```bash
# Définir la variable d'environnement
export OPENAI_API_KEY="sk-votre-clé-ici"
```

#### Erreurs de modules
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Réinitialiser l'environnement
conda activate chem-env
```

### Codes d'Erreur
- `400` : Données invalides
- `500` : Erreur serveur interne
- `API non configurée` : Clé OpenAI manquante

## 🔄 Mise à Jour

### Nouvelles Fonctionnalités Ajoutées
- ✅ Chat temps réel avec IA
- ✅ Support d'images dans le chat
- ✅ Formatage automatique du code
- ✅ Interface modernisée
- ✅ Gestion d'erreurs améliorée
- ✅ Mode dégradé sans API

### Fonctionnalités Futures
- 🔄 Export de modules en packages
- 🔄 Intégration Git automatique
- 🔄 Templates de modules prédéfinis
- 🔄 Analyse de performance

## 📞 Support

### Documentation
- `README_AUTONOMOUS.md` : Guide détaillé
- Code source commenté
- Logs détaillés pour debug

### Ressources
- Interface web : http://localhost:5002
- Logs : `IAM_Logs/`
- Modules : `GeneratedScripts/`

---

## 🎯 Exemples d'Utilisation

### Génération d'un Module de Calcul
1. Nom : `chemistry_calculator`
2. Description : "Module pour calculs de chimie quantique"
3. Exigences : "Inclure constantes physiques et conversions"

### Test Automatique
1. Sélectionner le module créé
2. Générer les tests automatiquement
3. Exécuter et vérifier les résultats

### Chat Assistance
- "Explique la théorie DFT"
- "Analyse cette structure moléculaire" (avec image)
- "Comment optimiser ce code Python ?"

---

*IAM Autonomous Platform v2.0 - Transformer l'IA en assistant de développement intelligent*
