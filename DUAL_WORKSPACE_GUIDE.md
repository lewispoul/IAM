# 🔄 Guide Dual Workspace - Pi SSH + WSL

## 🎯 **Configuration Actuelle**

### **🖥️ Laptop WSL (Environnement Principal)**
- **Port Interface :** `5005` 
- **URL :** http://localhost:5005
- **Branch Git :** `wsl-dev`
- **Utilisation :** Développement principal, tests, interface propre

### **🥧 Raspberry Pi SSH (Production)**
- **Ports Actifs :** `3000, 3001, 5000, 5001, 5002`
- **Branch Git :** `raspberry-pi-dev` 
- **Utilisation :** Production, calculs XTB, serveurs actifs

---

## ⚡ **Workflow Recommandé**

### **1. Développement sur WSL** ✅
```bash
# Sur WSL (laptop)
cd /home/pouli/IAM
git checkout wsl-dev
python3 IAM_GUI/server_clean.py   # Port 5005
```

### **2. Tests & Validation**
- Interface WSL : http://localhost:5005
- Tester toutes les fonctionnalités
- Commits réguliers sur `wsl-dev`

### **3. Synchronisation Pi ↔ WSL**
```bash
# WSL -> Pi (quand fonctionnalité prête)
git add .
git commit -m "WSL: Feature X completed"
git push origin wsl-dev

# Sur Pi SSH (via terminal Pi)
git checkout raspberry-pi-dev
git merge wsl-dev
git push origin raspberry-pi-dev
```

---

## 🚨 **Gestion des Conflits de Ports**

### **Ports Réservés :**
- **Pi :** `3000, 3001, 5000, 5001, 5002`
- **WSL :** `5005, 5006, 5007, 5008, 5009`

### **Si conflit détecté :**
```bash
# Vérifier ports utilisés
netstat -tulpn | grep :5000

# Changer port WSL
# Modifier server_clean.py : port=5005
```

---

## 📋 **Checklist Dual Workspace**

### **Avant de commencer (WSL) :**
- [ ] Vérifier branch : `git branch`
- [ ] Pull dernières MAJ : `git pull origin wsl-dev`
- [ ] Port libre : `netstat -tulpn | grep :5005`
- [ ] Démarrer serveur WSL

### **Avant sync Pi :**
- [ ] Commit tout sur WSL : `git add . && git commit`
- [ ] Push WSL : `git push origin wsl-dev`  
- [ ] Tester interface WSL fonctionnelle
- [ ] SSH vers Pi pour merge

### **Sur Pi (après sync) :**
- [ ] `git checkout raspberry-pi-dev`
- [ ] `git merge wsl-dev`
- [ ] Tester compatibilité Pi
- [ ] `git push origin raspberry-pi-dev`

---

## 🔧 **Commandes Rapides**

### **WSL (Laptop)**
```bash
# Setup rapide WSL
cd /home/pouli/IAM
git checkout wsl-dev
python3 IAM_GUI/server_clean.py

# Interface : http://localhost:5005
```

### **Pi SSH**
```bash
# Sync depuis WSL  
git checkout raspberry-pi-dev
git pull origin wsl-dev
git merge wsl-dev

# Restart services Pi
sudo systemctl restart iam-services
```

---

## ⚠️ **Bonnes Pratiques**

1. **🎯 Un seul environnement actif à la fois** pour le développement
2. **📝 Commits fréquents** sur WSL avant sync
3. **🧪 Tests complets** sur WSL avant transfert Pi  
4. **🔄 Sync quotidien** Pi ↔ WSL
5. **📦 Branches séparées** pour éviter conflicts

---

## 🆘 **Résolution Problèmes Courants**

### **Port déjà utilisé :**
```bash
# Trouver processus sur port
lsof -i :5005
# Tuer processus  
kill -9 <PID>
```

### **Git conflicts :**
```bash
# Reset hard si nécessaire
git reset --hard origin/wsl-dev
```

### **Pi non accessible :**
```bash
# Vérifier SSH
ssh -v user@pi-ip
# Restart SSH service Pi
sudo systemctl restart ssh
```

---

*💡 Conseil : Utilisez WSL comme environnement de développement principal et Pi comme production/test final.*
