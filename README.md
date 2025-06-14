# IAM

IAM is a prototype chemistry assistant that combines small utilities for molecular modeling with a minimal web interface. The project currently includes scripts for running `xtb` calculations and a Flask app for quick SMILES-based submissions.

## Quick start

Install dependencies:

```bash
pip install -r requirements.txt
```

Ensure the `xtb` executable is available in your `PATH`. If it lives in a
custom directory, set the environment variable `XTB_PATH` before launching the
server, e.g.:

```bash
export XTB_PATH=/opt/xtb/bin
```

Launch the web interface:

```bash
python webui/app.py
```

This opens a simple page where you can input a SMILES string and run an `xtb` job. Results such as total energy and HOMO–LUMO gap will be displayed after the calculation.
