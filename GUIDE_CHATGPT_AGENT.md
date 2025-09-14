# Guide d'utilisation - Agent ChatGPT IAM avec accès complet

## 🚀 Installation et Configuration

### 1. Configuration de l'API OpenAI

Éditez le fichier `agent_config.yaml` avec votre clé API :

```yaml
gpt4_api_key: "sk-votre-clé-api-openai-ici"
gpt4_model: "gpt-4o"  # ou "gpt-4", "gpt-3.5-turbo"
```

### 2. Installation des dépendances

```bash
pip3 install openai pyyaml pandas pymupdf
```

## 🎯 Lancement de l'agent

### Méthode 1 : Script automatique
```bash
./launch_chatgpt_agent.sh
```

### Méthode 2 : Commande directe
```bash
python3 IAM_Agent.py --full-agent
```

## 🛠️ Fonctionnalités disponibles

### 📁 Gestion des fichiers
L'agent peut :
- Lister les fichiers et dossiers
- Lire le contenu des fichiers
- Créer et modifier des fichiers
- Supprimer des fichiers
- Déplacer/renommer des fichiers
- Rechercher des fichiers

**Exemples de commandes :**
- "Liste les fichiers dans le dossier IAM"
- "Montre-moi le contenu du fichier test.py"
- "Crée un fichier hello.py avec un script qui dit bonjour"
- "Supprime le fichier temp.txt"

### 🐍 Exécution de code Python
L'agent peut exécuter du code Python directement :

**Exemples :**
- "Exécute un script qui calcule la factorielle de 10"
- "Crée un graphique avec matplotlib"
- "Analyse ce fichier CSV"
- "Lance un calcul de chimie quantique"

### 🖥️ Commandes shell
L'agent peut exécuter des commandes système (avec sécurité) :

**Exemples :**
- "Affiche l'espace disque disponible"
- "Liste les processus en cours"
- "Vérifie la version de Python"
- "Installe un package avec apt"

### 📦 Gestion des packages Python
**Exemples :**
- "Installe numpy"
- "Installe matplotlib et seaborn"

### 🧪 Calculs chimie computationnelle
L'agent peut lancer des calculs XTB :

**Exemples :**
- "Lance un calcul XTB sur nitromethane.xyz"
- "Optimise la géométrie de cette molécule"

## 🔒 Sécurité

L'agent inclut plusieurs mesures de sécurité :

1. **Commandes interdites** : Les commandes dangereuses (rm -rf, sudo, etc.) sont bloquées
2. **Sandbox des fichiers** : L'accès est limité au répertoire /home/lppou
3. **Timeout** : Les exécutions sont limitées dans le temps
4. **Extensions autorisées** : Seuls certains types de fichiers peuvent être manipulés

## 💡 Exemples d'utilisation avancée

### Analyse de données chimiques
```
Utilisateur: "Analyse le fichier molecules.csv et crée un graphique des masses molaires"

Agent: Je vais d'abord lire le fichier CSV, puis analyser les données et créer un graphique.
[Exécute read_file, puis du code Python avec pandas et matplotlib]
```

### Création d'un workflow automatisé
```
Utilisateur: "Crée un script qui lit tous les fichiers .xyz du dossier, lance des calculs XTB et sauvegarde les résultats"

Agent: Je vais créer un script Python qui automatise ce workflow.
[Crée le fichier, l'exécute, sauvegarde les résultats]
```

### Debugging et développement
```
Utilisateur: "Il y a une erreur dans mon script test.py, peux-tu la corriger ?"

Agent: Je vais examiner le fichier, identifier l'erreur et la corriger.
[Lit le fichier, identifie le problème, propose une correction, l'applique]
```

## 🔧 Corrections Function Calling (Janvier 2025)

### ✅ Problèmes corrigés dans IAM_ChatGPT_Integration.py :

1. **Chemin de base incorrect** :
   ```python
   # AVANT (incorrect)
   self.file_manager = IAMFileManager()  # Base path: /home/lppou
   
   # APRÈS (corrigé)
   self.file_manager = IAMFileManager(base_path="/home/lppou/IAM")
   ```

2. **Mode GOD non activé dans les gestionnaires** :
   ```python
   def enable_god_mode(self):
       self.god_mode = True
       self.unlimited_access = True
       
       # AJOUTÉ: Activer GOD mode dans les gestionnaires
       self.file_manager.enable_god_mode()
       if hasattr(self.code_executor, 'enable_god_mode'):
           self.code_executor.enable_god_mode()
   ```

3. **Diagnostic amélioré** :
   ```python
   # AVANT: Affichage générique
   print("✅ Résultat read_file: fichier lu avec succès")
   
   # APRÈS: Affichage détaillé
   if result.get("success"):
       print(f"✅ Lecture: {len(result.get('content', ''))} caractères")
   else:
       print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
   ```

### 🧪 Tests de validation :

Pour vérifier que le Function Calling fonctionne :

```bash
# Test rapide
python test_ultimate.py

# Test complet  
python test_chatgpt_function_calling.py
```

### 🎯 Résultat attendu :

**AVANT les corrections :**
- Agent répond : "Je ne peux pas accéder à vos fichiers..."
- Pas d'utilisation des fonctions système

**APRÈS les corrections :**
- Agent lit réellement les fichiers
- Donne des réponses basées sur le contenu des fichiers
- Utilise les fonctions read_file, execute_python, etc.

### 💡 Utilisation normale :

Une fois corrigé, vous pouvez utiliser l'agent normalement :

```bash
# Interface en ligne de commande
python IAM_Agent.py --full-agent

# Via le script de lancement
./launch_chatgpt_agent.sh
```

Et demander à l'agent :
- "Lis le fichier backend.py et explique-moi ce qu'il fait"
- "Liste tous les fichiers .py dans le répertoire"
- "Exécute ce code Python: print('Hello World')"
- "Crée un fichier test.py avec une fonction simple"
