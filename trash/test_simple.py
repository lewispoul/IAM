#!/usr/bin/env python3

print("🧪 Test simple de l'agent ChatGPT IAM")
print("=" * 40)

try:
    import yaml
    print("✅ yaml: OK")
except ImportError:
    print("❌ yaml: manquant")

try:
    import openai
    print("✅ openai: OK")
except ImportError:
    print("❌ openai: manquant")

try:
    import pandas
    print("✅ pandas: OK")
except ImportError:
    print("❌ pandas: manquant")

try:
    import fitz
    print("✅ PyMuPDF: OK")
except ImportError:
    print("❌ PyMuPDF: manquant")

# Test configuration
try:
    with open("agent_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    print("✅ Configuration: OK")
    
    if config.get("gpt4_api_key"):
        print("✅ Clé API: Configurée")
    else:
        print("❌ Clé API: Manquante")
        
except Exception as e:
    print(f"❌ Configuration: {e}")

print("\n🎉 Test terminé!")
print("\nPour lancer l'agent:")
print("python3 IAM_Agent.py --full-agent")
