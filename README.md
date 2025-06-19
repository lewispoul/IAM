# 🧪 IAM – Intelligent Assistant for Materials

![Python](https://img.shields.io/badge/python-3.10-blue)
![Platform](https://img.shields.io/badge/platform-RaspberryPi%20%7C%20Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-blue)
![IAM Project](https://img.shields.io/badge/IAM_Project-Active-informational)

---

## 📁 Table des matières

1. [Présentation](#présentation)
2. [Pré-requis globaux](#pré-requis-globaux)
3. [Installation par plateforme](#installation-par-plateforme)
    - [Raspberry Pi](#🍓-installation-sur-raspberry-pi)
    - [Windows](#🪟-installation-sur-windows)
    - [Linux/macOS](#🐧-installation-sur-linuxmacos)
4. [Gestion de l’environnement `chem-env`](#gestion-de-chem-env)
5. [Outils de développement recommandés](#outils-de-développement-recommandés)
6. [Structure du projet IAM](#structure-du-projet-iam)
7. [Crédits](#crédits)

---

## 🧬 Présentation

IAM permet :

- L’optimisation géométrique de molécules (via XTB)
- La prédiction d’énergie, dipôle, charges, orbitales HOMO–LUMO
- La génération automatique de fiches moléculaires enrichies
- La prédiction empirique des performances (VoD, P_cj, ΔH)
- L’utilisation locale (Raspberry Pi, laptop, mobile)
- L’interface interactive Web/Notebook (Flask, Jupyter, 3Dmol.js)

---

## ✅ Pré-requis globaux

- Python 3.9 ou 3.10
- Git
- Conda (ou Python venv)
- XTB installé : [https://github.com/grimme-lab/xtb](https://github.com/grimme-lab/xtb)
- OpenBabel, RDKit, Flask, Py3Dmol, etc.

---

## 🔧 Installation par plateforme

### 🍓 Installation sur Raspberry Pi

```bash
sudo apt update && sudo apt upgrade
sudo apt install git python3-pip python3-venv build-essential libopenbabel-dev

git clone https://github.com/votre-user/IAM.git
cd IAM

python3 -m venv chem-env
source chem-env/bin/activate
pip install -r requirements.txt