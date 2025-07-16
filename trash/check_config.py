import yaml

with open("agent_config.yaml", "r") as f:
    config = yaml.safe_load(f)

print("Clé API chargée :")
print(config.get("gpt4_api_key", "❌ Clé non trouvée"))
