# IAM_Agent.py – Agent principal IAM avec modes GPT-4, XTB, etc.

import openai
import yaml
import os
impo        mol = {k: 'NA' for k in [
            "Nom", "Famille", "Formule brute", "Masse molaire", "Densité",
            "Pourcentage d'azote (%N)", "Oxygen Balance (ΩCO₂)", 
            "ΔHf (kJ/mol)", "T_mp (°C)", "T_dec (°C)", "VoD (m/s)", 
            "P_cj (kbar)", "ΔH_det (kJ/kg)", "IS (J)", "FS (N)", "ES (mJ)", 
            "Solubilité", "Système cristallin", "Groupe d'espace", 
            "a / b / c (Å)", "α / β / γ (°)", "Indicateurs structuraux", 
            "Source", "Méthode", "Commentaires"]}ests
import json
import re
import fitz  # PyMuPDF
import pandas as pd
from datetime import datetime
from openai import OpenAI

# Chargement de la configuration GPT-4
with open("agent_config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

openai.api_key = config["gpt4_api_key"]
model = config.get("gpt4_model", "gpt-4o")


# --- Fonction : Assistant de codage GPT-4 ---
def launch_code_assistant():
    from IAM_CodeAssistant import ask_gpt_code_assistant
    ask_gpt_code_assistant()


# --- Fonction : Assistant conversationnel GPT-4 ---
def launch_chat_assistant():
    print("💬 Assistant conversationnel IAM prêt. Tapez 'exit' pour quitter.\n")
    context = [
        {
            "role": "system",
            "content": "Tu es un assistant expert en chimie computationnelle "
                       "et en Python. Sois toujours clair, structuré, et précis."
        }
    ]

    client = OpenAI(api_key=openai.api_key)

    while True:
        try:
            user_input = input("👤 Vous : ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            context.append({"role": "user", "content": user_input})
            response = client.chat.completions.create(
                model=model,
                messages=context
            )
            answer = response.choices[0].message.content
            print("🤖 IAM :\n" + answer + "\n")
            context.append({"role": "assistant", "content": answer})
        except KeyboardInterrupt:
            print("\n⛔ Session interrompue par l'utilisateur.")
            break
        except Exception as e:
            if "openai" in str(type(e)).lower():
                print(f"❌ Erreur OpenAI : {e}")
            else:
                print(f"❌ Erreur : {e}")


# --- Fonction : Test XTB via API Flask ---
def test_xtb_workflow():
    file_path = "IAM_Knowledge/Examples/nitromethane.xyz"
    mol_name = os.path.splitext(os.path.basename(file_path))[0]

    print(f"📤 Envoi du fichier {file_path} à l'API XTB...")

    with open(file_path, "rb") as file:
        files = {"file": (os.path.basename(file_path), file)}
        response = requests.post(
            "http://localhost:5000/run_xtb",
            files=files,
            timeout=300
        )

    if response.ok:
        data = response.json()
        print("✅ Résultat reçu :")
        print(json.dumps(data, indent=2))

        export_folder = "IAM_Knowledge/Results"
        os.makedirs(export_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(
            export_folder, f"{mol_name}_xtb_{timestamp}.json"
        )

        with open(export_path, "w", encoding="utf-8") as export_file:
            json.dump(data, export_file, indent=2)
        print(f"📁 Résultat XTB exporté vers {export_path}")
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")


# --- Fonction : Extraction des volumes Klapötke avec PyMuPDF ---
def parse_pdf_volume(filepath, volume_tag):
    doc = fitz.open(filepath)
    all_data = []

    for i, page in enumerate(doc):
        text = page.get_text()
        lines = text.split("\n")

        mol = {k: 'NA' for k in [
            "Nom", "Famille", "Formule brute", "Masse molaire", "Densité",
            "Pourcentage d’azote (%N)", "Oxygen Balance (ΩCO₂)", "ΔHf (kJ/mol)",
            "T_mp (°C)", "T_dec (°C)", "VoD (m/s)", "P_cj (kbar)", "ΔH_det (kJ/kg)",
            "IS (J)", "FS (N)", "ES (mJ)", "Solubilité", "Système cristallin",
            "Groupe d’espace", "a / b / c (Å)", "α / β / γ (°)",
            "Indicateurs structuraux", "Source", "Méthode", "Commentaires"]}

        mol["Source"] = f"{volume_tag}, Page {i + 1}"

        for line in lines:
            if re.search(r"^Name: ", line):
                mol["Nom"] = line.split(":", 1)[1].strip()
            if re.search(r"^Formula: ", line):
                mol["Formule brute"] = line.split(":", 1)[1].strip()
            if "Density" in line:
                match = re.search(r"(\d+\.\d+)", line)
                mol["Densité"] = match.group(1) if match else 'NA'
            if "Heat of formation" in line:
                match = re.search(r"([-\d\.]+)", line)
                mol["ΔHf (kJ/mol)"] = match.group(1) if match else 'NA'
            if "VoD" in line:
                match = re.search(r"(\d{3,5})", line)
                mol["VoD (m/s)"] = match.group(1) if match else 'NA'
            if "pC-J" in line:
                match = re.search(r"(\d+)", line)
                mol["P_cj (kbar)"] = match.group(1) if match else 'NA'
            if "Tm.p." in line:
                match = re.search(r"(\d+)", line)
                mol["T_mp (°C)"] = match.group(1) if match else 'NA'
            if "Tdec." in line:
                match = re.search(r"(\d+)", line)
                mol["T_dec (°C)"] = match.group(1) if match else 'NA'
            if "-ΔH" in line:
                match = re.search(r"(\d+)", line)
                mol["ΔH_det (kJ/kg)"] = match.group(1) if match else 'NA'

        all_data.append(mol)

    df = pd.DataFrame(all_data)
    return df


def parse_klap_volumes():
    volumes = {
        "Volume 1 (A–D)": "IAM_References/klapotke_vol1.pdf",
        "Volume 2 (E)": "IAM_References/klapotke_vol2.pdf",
        "Volume 3 (O)": "IAM_References/klapotke_vol3.pdf"
    }

    all_dfs = []
    for tag, path in volumes.items():
        if os.path.exists(path):
            print(f"🔍 Traitement de {tag}...")
            df = parse_pdf_volume(path, tag)
            all_dfs.append(df)
        else:
            print(f"❌ Fichier non trouvé : {path}")

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        os.makedirs("IAM_References", exist_ok=True)
        final_df.to_csv(
            "IAM_References/IAM_Master_Energetics.csv", index=False
        )
        print("✅ Fichier final enregistré : "
              "IAM_References/IAM_Master_Energetics.csv")


# --- Fonction : Assistant ChatGPT avec accès système complet ---
def launch_full_chatgpt_agent():
    from IAM_ChatGPT_Integration import main as chatgpt_main
    chatgpt_main()


# --- Bloc principal ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--code", action="store_true",
                        help="Activer le mode assistant de codage GPT-4")
    parser.add_argument("--chat", action="store_true",
                        help="Activer le mode conversationnel GPT-4 "
                             "(avec mémoire contextuelle)")
    parser.add_argument("--full-agent", action="store_true",
                        help="Lancer l'agent ChatGPT avec accès complet "
                             "(fichiers + exécution)")
    parser.add_argument("--xtb", action="store_true",
                        help="Exécuter un test XTB local sur le fichier "
                             ".xyz par défaut")
    parser.add_argument("--parse-volumes", action="store_true",
                        help="Extraction complète des encyclopédies "
                             "Klapötke")
    args = parser.parse_args()

    if args.code:
        launch_code_assistant()

    if args.chat:
        launch_chat_assistant()

    if args.full_agent:
        launch_full_chatgpt_agent()

    if args.xtb:
        test_xtb_workflow()

    if args.parse_volumes:
        parse_klap_volumes()
