import requests

file_path = "IAM_Knowledge/Examples/nitromethane.xyz"

with open(file_path, "rb") as f:
    files = {"file": (file_path.split("/")[-1], f)}
    print(f"📤 Envoi du fichier {file_path} à l'API XTB...")

    response = requests.post("http://localhost:5000/run_xtb", files=files)

if response.ok:
    print("✅ Résultat reçu :")
    print(response.json())
else:
    print(f"❌ Erreur {response.status_code} : {response.text}")
