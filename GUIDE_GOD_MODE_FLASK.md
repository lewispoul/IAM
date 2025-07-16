# 🔥 Guide Complet: GOD MODE + Interface Flask 🔥

## 🚀 Comment activer le GOD MODE avec l'interface Flask

### ✅ **Option 1: Script Automatique (Recommandé)**
```bash
./launch_god_mode_flask.sh
```
**Choisissez l'option 3** pour GOD MODE + Interface Flask combinés

### ✅ **Option 2: Commandes Manuelles**

#### 🔧 **Étape 1: Préparer l'environnement**
```bash
# Activer conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Définir variables GOD MODE
export IAM_GOD_MODE=TRUE
export IAM_UNLIMITED_ACCESS=TRUE
export IAM_SYSTEM_COMMANDS=TRUE

cd /home/lppou/IAM
```

#### 🌐 **Étape 2: Démarrer l'interface Flask**
```bash
# Terminal 1: Interface Flask
cd IAM_GUI
python backend.py
```
➡️ Interface disponible sur: **http://localhost:5000**

#### ⚡ **Étape 3: Démarrer le GOD MODE**  
```bash
# Terminal 2: GOD MODE
python3 IAM_Agent.py --full-agent
```

## 🎯 **Fonctionnalités Disponibles**

### 🔥 **GOD MODE Activé:**
- ✅ **Accès système illimité**
- ✅ **Modification complète du code**
- ✅ **Exécution libre de commandes shell**
- ✅ **Permissions étendues sur tous dossiers IAM**
- ✅ **Pas de limitations de sécurité**

### 🌐 **Interface Flask Disponible:**
- ✅ **Interface web intuitive** (http://localhost:5000)
- ✅ **Conversion MOL ↔ XYZ**
- ✅ **Calculs XTB avancés**
- ✅ **Prédictions VoD/densité**
- ✅ **Éditeur moléculaire Ketcher**
- ✅ **Visualisation 3D**

## 🛠️ **Commandes GOD MODE Disponibles**

### 📁 **Gestion des Fichiers:**
```
- Lire/écrire tout fichier du système
- Modifier le code source IAM en temps réel
- Créer/supprimer dossiers et fichiers
- Accéder à IAM_Knowledge/, IAM_Logs/, etc.
```

### 🐍 **Exécution de Code:**
```
- Exécuter scripts Python
- Lancer commandes shell
- Installer packages
- Modifier configuration système
```

### 🔬 **Chimie Computationnelle:**
```
- Calculs XTB automatiques
- Optimisation géométrique
- Prédictions de propriétés
- Analyse de données moléculaires
```

## 🎯 **Utilisation Pratique**

### **Scénario 1: Développement**
1. **Interface Flask** → Test des fonctionnalités
2. **GOD MODE** → Modification du code en temps réel
3. **Rechargement automatique** → Voir les changements

### **Scénario 2: Recherche**
1. **Interface Flask** → Dessiner molécules (Ketcher)
2. **GOD MODE** → Scripts de calcul personnalisés
3. **Résultats** → Analyse et export

### **Scénario 3: Production**
1. **Interface Flask** → Interface utilisateur stable
2. **GOD MODE** → Maintenance et debugging
3. **Monitoring** → Supervision système

## ⚠️ **Sécurité et Précautions**

### 🔒 **Mode GOD - Utilisation Responsable:**
- ⚠️ **Accès système complet** - Soyez prudent
- ⚠️ **Modifications permanentes** - Sauvegardez avant
- ⚠️ **Exécution libre** - Vérifiez les commandes

### ✅ **Recommandations:**
- 💾 **Sauvegardez** votre travail régulièrement
- 🧪 **Testez** sur des copies avant production  
- 📝 **Documentez** vos modifications
- 🔄 **Versionnez** le code avec git

## 🚨 **Dépannage**

### **Problème: Interface Flask ne démarre pas**
```bash
# Vérifier le port
netstat -tulpn | grep :5000

# Tuer processus bloquant
sudo fuser -k 5000/tcp

# Relancer
cd IAM_GUI && python backend.py
```

### **Problème: GOD MODE ne s'active pas**
```bash
# Vérifier variables d'environnement
echo $IAM_GOD_MODE
echo $IAM_UNLIMITED_ACCESS

# Réexporter si nécessaire
export IAM_GOD_MODE=TRUE
export IAM_UNLIMITED_ACCESS=TRUE
```

### **Problème: Conda non activé**
```bash
# Réactiver conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env
```

## 🎉 **Ready to Rock!**

**Votre plateforme IAM est maintenant prête avec:**
- 🔥 **GOD MODE**: Puissance illimitée
- 🌐 **Interface Flask**: Interface utilisateur
- ⚡ **Intégration complète**: Workflow optimal

**Lancez `./launch_god_mode_flask.sh` et choisissez l'option 3!** 🚀
