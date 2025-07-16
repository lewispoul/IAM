import os
import fitz  # pymupdf
import re
import json
import yaml
import time
import requests
from pathlib import Path
import openai

PDF_DIR = "IAM_References"
COMPOUND_DIR = "IAM_Knowledge/Compounds"
RESULTS_DIR = "IAM_Knowledge/Results"
CONFIG_FILE = "agent_config.yaml"

os.makedirs(COMPOUND_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

with open(CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)

openai.api_key = config.get("gpt4_api_key", "")

compound_pattern = re.compile(r"^[A-Z][a-z\d\-(),'\\s]+\\t")

def extract_data_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_data = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.splitlines()
        for line in lines:
            if compound_pattern.match(line):
                all_data.append((page_num+1, line.strip()))
    return all_data

def parse_line(line):
    fields = line.split("\t")
    if len(fields) < 3:
        return None
    return {
        "name": fields[0],
        "density": fields[1] if len(fields) > 1 else None,
        "vod": fields[2] if len(fields) > 2 else None,
        "heat_of_det": fields[3] if len(fields) > 3 else None,
        "raw": fields
    }

def save_json(compound, source, page):
    name_clean = compound["name"].replace("/", "-").replace(" ", "_")
    outfile = Path(COMPOUND_DIR) / f"{name_clean}.json"
    compound.update({"source": source, "page": page})
    with open(outfile, 'w') as f:
        json.dump(compound, f, indent=2)

def ask_gpt4(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def run_xtb(mol_name):
    print(f"?? Lancement XTB pour {mol_name}...")
    try:
        r = requests.post(config["api_endpoints"]["xtb"], json={"molecule": mol_name})
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def run_vod(mol_name):
    print(f"?? Prédiction VoD pour {mol_name}...")
    try:
        r = requests.post(config["api_endpoints"]["vod"], json={"molecule": mol_name})
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def agent_loop():
    for file in os.listdir(COMPOUND_DIR):
        if not file.endswith(".json"):
            continue
        path = os.path.join(COMPOUND_DIR, file)
        with open(path, 'r') as f:
            compound = json.load(f)

        mol_name = compound.get("name", "Unknown")
        vod = compound.get("vod")
        density = compound.get("density")

        actions_needed = []
        if not vod:
            actions_needed.append("run_vod")

        if actions_needed:
            prompt = f"Molecule: {mol_name}\nActions required: {actions_needed}\nShould I run XTB or VoD first?"
            plan = ask_gpt4(prompt)
            print(f"?? Plan IA pour {mol_name} :\n{plan}")

            if "run_xtb" in plan:
                xtb_res = run_xtb(mol_name)
                compound["xtb"] = xtb_res
            if "run_vod" in plan:
                vod_res = run_vod(mol_name)
                compound["vod_predicted"] = vod_res

            with open(path, 'w') as f:
                json.dump(compound, f, indent=2)

if __name__ == "__main__":
    print("?? Lecture des encyclopédies...")
    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            path = os.path.join(PDF_DIR, filename)
            extracted = extract_data_from_pdf(path)
            for page, line in extracted:
                parsed = parse_line(line)
                if parsed:
                    save_json(parsed, source=filename, page=page)

    print("?? Démarrage de l'agent IA...")
    while config.get("auto_mode", False):
        agent_loop()
        print(f"⏳ Pause de {config['interval_minutes']} min...")
        time.sleep(int(config["interval_minutes"]) * 60)

    print("✅ Agent terminé.")
