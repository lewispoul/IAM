# test_gpt.py – Vérification de l'accès à GPT-4 via agent_config.yaml

import openai
import yaml

# Chargement de la configuration
with open("agent_config.yaml", "r") as f:
    config = yaml.safe_load(f)

openai.api_key = config["gpt4_api_key"]
model = config.get("gpt4_model", "gpt-4o")

# Test de requête explicite
response = openai.ChatCompletion.create(
    model=model,
    messages=[
        {"role": "user", "content": "Je parle de mon assistant de chimie computationnelle nommé IAM. Est-il prêt à analyser des composés énergétiques aujourd’hui ?"}
    ]
)

print("✅ Réponse de GPT-4 :\n")
print(response["choices"][0]["message"]["content"])
