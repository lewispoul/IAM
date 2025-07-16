# 🌐 Workflow Git: Raspberry Pi ↔ WSL

## 🏗️ **Architecture Branches**

```
main (GitHub)
├── pi-dev-clean (Raspberry Pi) 
└── wsl-dev (WSL Windows)
```

## 🎯 **Stratégie de Développement**

### **🍓 Branche Raspberry Pi: `pi-dev-clean`**
- **Environnement:** Raspberry Pi 4/5, Linux ARM
- **Focus:** Performance optimisée, hardware spécifique
- **Spécialités:** Calculs XTB natifs, interfaces GPIO si besoin
- **Commits typiques:** "[PI] Optimisation ARM", "[PI] Interface tactile"

### **🖥️ Branche WSL: `wsl-dev`**
- **Environnement:** Windows WSL2, développement principal
- **Focus:** Interface moderne, développement rapide
- **Spécialités:** UI/UX avancée, debugging, prototypage
- **Commits typiques:** "[WSL] Interface moderne", "[WSL] Debug fixes"

## 🔄 **Workflow de Synchronisation**

### **📤 Partager une amélioration Pi → WSL**
```bash
# Sur le Pi
git add .
git commit -m "[PI] Feature: amélioration backend XTB"
git push origin pi-dev-clean

# Sur WSL  
git fetch origin
git checkout wsl-dev
git cherry-pick <commit-hash-du-pi>
# Résoudre conflits si nécessaire
git commit -m "[WSL] Port from PI: amélioration backend XTB"
```

### **📥 Partager une amélioration WSL → Pi**
```bash
# Sur WSL
git add .
git commit -m "[WSL] Feature: interface moderne Ketcher"
git push origin wsl-dev

# Sur le Pi
git fetch origin  
git checkout pi-dev-clean
git cherry-pick <commit-hash-wsl>
# Adapter pour Pi si nécessaire
git commit -m "[PI] Port from WSL: interface moderne adaptée"
```

### **🔄 Synchronisation Bidirectionnelle**
```bash
# Script de sync (à lancer sur les deux machines)
git fetch origin
git log --oneline pi-dev-clean ^HEAD   # Voir commits Pi manquants
git log --oneline wsl-dev ^HEAD        # Voir commits WSL manquants

# Cherry-pick les commits intéressants
git cherry-pick <hash1> <hash2> <hash3>
```

## 📋 **Convention de Commits**

### **🏷️ Préfixes Obligatoires:**
- `[PI]` - Spécifique Raspberry Pi
- `[WSL]` - Spécifique Windows WSL
- `[BOTH]` - Compatible les deux
- `[MERGE]` - Fusion de branches

### **📝 Exemples:**
```bash
git commit -m "[PI] Fix: optimisation calculs XTB pour ARM"
git commit -m "[WSL] Feature: interface Ketcher responsive" 
git commit -m "[BOTH] Update: amélioration parsing MOL"
git commit -m "[MERGE] Sync: intégration features WSL→PI"
```

## 🛠️ **Commandes Utiles**

### **🔍 Comparer les Branches**
```bash
# Voir différences entre Pi et WSL
git diff pi-dev-clean..wsl-dev

# Voir commits uniques à chaque branche
git log pi-dev-clean --not wsl-dev --oneline
git log wsl-dev --not pi-dev-clean --oneline
```

### **📦 Export/Import de Commits**
```bash
# Exporter un commit en patch
git format-patch -1 <commit-hash>

# Appliquer sur l'autre machine
git apply 0001-mon-patch.patch
```

### **🔄 Résolution de Conflits**
```bash
# En cas de conflit lors cherry-pick
git status
# Éditer fichiers en conflit
git add .
git cherry-pick --continue
```

## 🎯 **Workflow Pratique Quotidien**

### **🌅 Début de Session**
```bash
# Synchro du matin
git fetch origin
git status
git log --oneline origin/[autre-branche] ^HEAD
```

### **🌙 Fin de Session**
```bash
# Sauvegarde du soir
git add .
git commit -m "[PI/WSL] Session: résumé des changements"
git push origin [ma-branche]
```

### **📋 Check Hebdomadaire** 
```bash
# Sync complète bi-directionnelle
git fetch origin
git cherry-pick origin/wsl-dev <hash-intéressant-1>
git cherry-pick origin/pi-dev-clean <hash-intéressant-2>
git push origin [ma-branche]
```

## 🚀 **Avantages de cette Approche**

### **✅ Développement Indépendant**
- Travaillez sur Pi et WSL simultanément
- Pas de blocage mutuel
- Optimisations spécifiques à chaque plateforme

### **✅ Partage Sélectif**
- Cherry-pick seulement ce qui vous intéresse
- Pas de merge massif avec conflits
- Historique propre et traçable

### **✅ Flexibilité**
- Pi peut avoir des optimisations ARM
- WSL peut avoir des interfaces plus modernes
- Fusion des meilleurs éléments

## 📄 **Templates de Commit**

### **🍓 Template Pi:**
```
[PI] <type>: <description courte>

Optimisation spécifique Raspberry Pi:
- Performance ARM améliorée
- Gestion mémoire optimisée
- Interface hardware si applicable

Testé sur: Pi 4/5, RAM 4-8GB
```

### **🖥️ Template WSL:**
```
[WSL] <type>: <description courte>

Amélioration développement WSL:
- Interface moderne
- Debugging amélioré
- Compatibilité Windows

Testé sur: WSL2, Ubuntu 22.04
```

## 🎉 **Prêt à Rock!**

Vous avez maintenant un workflow Git robuste pour gérer vos deux environnements de développement IAM !

**Commandes pour démarrer:**
```bash
# Sur Pi
git checkout pi-dev-clean

# Sur WSL
git checkout wsl-dev
```

**Happy coding! 🚀**
