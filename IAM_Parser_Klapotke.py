# IAM_Parser_Klapotke.py – Extraction robuste depuis les PDF structurés de Klapötke

import pdfplumber
import pandas as pd
import re
import os
from datetime import datetime

# Liste des champs à extraire (doivent matcher le template final)
COLUMNS = [
    "Nom", "Famille", "Formule brute", "Masse molaire", "Densité",
    "Pourcentage d’azote (%N)", "Oxygen Balance (ΩCO₂)", "ΔHf (kJ/mol)",
    "T_mp (°C)", "T_dec (°C)", "VoD (m/s)", "P_cj (kbar)", "ΔH_det (kJ/kg)",
    "IS (J)", "FS (N)", "ES (mJ)", "Solubilité", "Système cristallin",
    "Groupe d’espace", "a / b / c (Å)", "α / β / γ (°)",
    "Indicateurs structuraux", "Source", "Méthode", "Commentaires"
]

# Expressions régulières (extraites de l'observation des textes typiques)
REGEX_PATTERNS = {
    "Masse molaire": r"(\d{2,4}\.\d{1,3})\s*g mol",
    "Densité": r"(?:\u03c1|Densité)\s*[=:]?\s*(\d\.\d+)",
    "Pourcentage d’azote (%N)": r"N\s*\[%\]\s*(\d{1,3}\.\d+)",
    "Oxygen Balance (ΩCO₂)": r"\u03a9\(CO2\)\s*\[%\]\s*(-?\d+\.\d+)",
    "ΔHf (kJ/mol)": r"(?:\u0394Hf|heat of formation).*?(-?\d+\.\d+).*?kJ/mol",
    "T_mp (°C)": r"Tm\.?p\.?\s*\[\u00b0C\]\s*(\d{2,4})",
    "T_dec (°C)": r"Tdec\.?\s*\[\u00b0C\]\s*(\d{2,4})",
    "VoD (m/s)": r"VoD\s*\[m s-1\]\s*(\d{3,5})",
    "P_cj (kbar)": r"pC-J\s*\[kbar\]\s*(\d{2,4})",
    "ΔH_det (kJ/kg)": r"-\u0394H\s*\[kJ/kg\]\s*(\d{3,5})",
    "IS (J)": r"IS\s*\[J\]\s*(\d+)",
    "FS (N)": r"FS\s*\[N\]\s*(\d+)",
    "ES (mJ)": r"ESD\s*\[m?J\]\s*(\d+)",
}


def extract_fields(text, source):
    data = {col: "NA" for col in COLUMNS}
    data["Source"] = source

    # Nom de la molécule : première ligne non vide contenant des majuscules
    lines = text.split('\n')
    for line in lines:
        if re.match(r"[A-Z][\w\-\s,\.]+", line.strip()):
            data["Nom"] = line.strip()
            break

    # Champs via regex
    for field, pattern in REGEX_PATTERNS.items():
        match = re.search(pattern, text)
        if match:
            data[field] = match.group(1)

    return data


def parse_pdf_with_pdfplumber(pdf_path, output_csv="IAM_Master_Energetics.csv"):
    all_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                source = f"{os.path.basename(pdf_path)} – Page {i+1}"
                mol_data = extract_fields(text, source)
                all_data.append(mol_data)

    df = pd.DataFrame(all_data, columns=COLUMNS)
    out_path = os.path.join("IAM_References", output_csv)
    os.makedirs("IAM_References", exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Extraction terminée : {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extraction des données des volumes Klapötke en CSV")
    parser.add_argument("--file", type=str, required=True, help="Chemin du fichier PDF à parser")
    args = parser.parse_args()
    parse_pdf_with_pdfplumber(args.file)
