<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a simple Python script project. Follow best practices for Python scripting and dependency management.
# 🤖 Copilot Instructions for IAM – Intelligent Agent for Molecules

_Last updated: 2025-08-02_

---

## 🧠 Project Overview

**IAM** is a modular AI platform for computational chemistry, molecular modeling, and performance prediction of energetic materials. It integrates:
- Molecular drawing and 3D visualization,
- Quantum chemistry calculations (XTB, Psi4, Gaussian),
- Detonation performance modeling (VoD, ΔHdet, P_cj),
- Stability prediction and hydrolysis analysis,
- Automatic literature parsing and data structuring.

IAM can run locally (Raspberry Pi, workstation) or remotely (cluster via SSH), and includes a web interface with advanced input/output handling.

---

## ✅ Current Functional Modules

| Component | Description |
|----------|-------------|
| `IAM_GUI/` | HTML/JS frontend with 3Dmol.js + Ketcher sketcher |
| `backend.py` | Flask server for handling molecule inputs and calculation dispatch |
| `iam_molecule_engine.py` | SMILES → XYZ generation, XTB execution, result parsing |
| `xtb_wrapper.py` | CLI wrapper for XTB with `.log` parsing |
| `IAM_Agent.py` | Watches folders, auto-runs predictions, saves `.json` and `.csv` |
| `IAM_BenchmarkTool.py` | Benchmark for VoD prediction models (ML, KJ, Empirical) |
| `IAM_Parser_Klapotke.py` | Extracts structured chemical data from Klapötke PDFs |
| `IAM_StabilityPredictor.py` | Scores hydrolysis sensitivity using SMARTS and RDKit |
| `IAM_Knowledge/` | Stores molecular results as `.json`, `.csv`, and benchmark logs |

---

## 📈 Supported Features

- 💻 Web GUI (draw molecule, paste SMILES/MOL/XYZ, run XTB, view results)
- ⚙️ Local XTB calculations with custom options (`--opt`, `--chrg`, `--uhf`, etc.)
- 📦 Psi4 and Gaussian support (via SSH or local installation)
- 🧠 VoD prediction: Kamlet–Jacobs, ML, Keshavarz formulas
- 📊 Auto-benchmark results (R², RMSE, MAE + comparison plots)
- 📁 Literature parsing: Klapötke Vol. 1–3, Agrawal, LLNL Handbook
- 🔐 Full Raspberry Pi support (SSH tunnel, Jupyter auto-launch)
- 🌐 Remote submission to HPC cluster via secure bridge
- 🔬 Cube file generation for HOMO–LUMO visualization
- 📱 Future mobile mode with Pydroid3 (offline support on Android)

---

## 🚧 Work In Progress / To Do

- [ ] Add cube file viewer using 3Dmol.js + HOMO–LUMO toggles
- [ ] Add VoD predictor tab in GUI with model selection (KJ/ML/Empirical)
- [ ] Improve error handling in backend.py + unified status output
- [ ] Complete parsing of Klapötke Vol. 2 and 3 + dataset merge
- [ ] Enable Psi4/Gaussian job submission via frontend
- [ ] Mobile version of IAM with GUI + computation relay
- [ ] Enable crystal structure visualization in GUI (if data present)
- [ ] Add reactive group detection module (azide, NO₂, BN, etc.)
- [ ] Expand IAM Agent to include memory tracking and async tasks

---

## 🤖 How Copilot Can Help

You (Copilot) can help by:

1. Fixing bugs or improving stability in `backend.py`, `script.js`, or `iam_molecule_engine.py`.
2. Generating endpoints for new features (e.g., `/run_vod_prediction`, `/generate_cube`).
3. Enhancing the `IAM_Agent.py` to manage scheduling, logging, or retrigger failed jobs.
4. Creating new modules like `IAM_CrystalViewer.py` or `IAM_HeatOfFormationPredictor.py`.
5. Integrating ML inference scripts into Flask (pretrained models for VoD/ΔH).
6. Maintaining clean `.json` format for each molecule in `IAM_Knowledge/`.
7. Optimizing performance for local/mobile deployment.

---

## 🧠 Design Philosophy

IAM is designed to:
- Automate scientific workflows,
- Augment the chemist’s thinking (via Nox, the assistant AI),
- Be extendable by Copilot, other agents, or humans,
- Run on any platform, including Raspberry Pi.

Always preserve **modularity**, **readability**, and **interoperability**.

