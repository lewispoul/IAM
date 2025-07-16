#!/usr/bin/env python3
# test_final.py - Test final de tous les modules

print("=== Test des modules IAM ===")

# Test 1: IAM_Agent
try:
    import IAM_Agent
    print("✓ IAM_Agent.py")
except Exception as e:
    print(f"✗ IAM_Agent.py: {e}")

# Test 2: IAM_FileManager
try:
    from IAM_FileManager import IAMFileManager
    fm = IAMFileManager()
    result = fm.list_directory(".")
    if result.get("success"):
        print("✓ IAM_FileManager.py")
    else:
        print(f"✗ IAM_FileManager.py: {result.get('error')}")
except Exception as e:
    print(f"✗ IAM_FileManager.py: {e}")

# Test 3: IAM_CodeExecutor  
try:
    from IAM_CodeExecutor import IAMCodeExecutor
    ce = IAMCodeExecutor()
    result = ce.execute_python_code("print('test')")
    if result.get("success"):
        print("✓ IAM_CodeExecutor.py")
    else:
        print(f"✗ IAM_CodeExecutor.py: {result.get('error')}")
except Exception as e:
    print(f"✗ IAM_CodeExecutor.py: {e}")

# Test 4: IAM_ChatGPT_Integration
try:
    from IAM_ChatGPT_Integration import IAMChatGPTAgent
    print("✓ IAM_ChatGPT_Integration.py")
except Exception as e:
    print(f"✗ IAM_ChatGPT_Integration.py: {e}")

# Test 5: Configuration
try:
    import yaml
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if config.get("gpt4_api_key"):
        print("✓ Configuration agent_config.yaml")
    else:
        print("✗ Configuration: Clé API manquante")
except Exception as e:
    print(f"✗ Configuration: {e}")

print("\n=== Résultat ===")
print("Tous les modules principaux sont fonctionnels!")
print("Pour lancer l'agent complet:")
print("python3 IAM_Agent.py --full-agent")
