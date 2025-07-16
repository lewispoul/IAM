#!/usr/bin/env python3
# test_rapide.py - Test rapide de fonctionnement

import sys

def test_module(module_name, import_statement):
    try:
        exec(import_statement)
        print(f"✓ {module_name}")
        return True
    except Exception as e:
        print(f"✗ {module_name}: {e}")
        return False

print("=== Test rapide des modules ===")

tests = [
    ("IAM_Agent", "import IAM_Agent"),
    ("IAM_FileManager", "from IAM_FileManager import IAMFileManager"),
    ("IAM_CodeExecutor", "from IAM_CodeExecutor import IAMCodeExecutor"), 
    ("IAM_ChatGPT_Integration", "from IAM_ChatGPT_Integration import IAMChatGPTAgent"),
]

success_count = 0
for name, statement in tests:
    if test_module(name, statement):
        success_count += 1

print(f"\n=== Résultat: {success_count}/{len(tests)} modules OK ===")

if success_count == len(tests):
    print("🎉 Tous les modules fonctionnent correctement!")
    print("Votre agent ChatGPT est prêt à être utilisé.")
else:
    print("⚠️  Certains modules ont des problèmes.")
