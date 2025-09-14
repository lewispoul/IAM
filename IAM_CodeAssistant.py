# IAM_CodeAssistant.py
from openai import OpenAI
import yaml

def ask_gpt_code_assistant():
    print("💡 Mode assistant de codage activé. Tapez 'exit' pour quitter.\n")
    context = [
        {"role": "system", "content": "Tu es un assistant Python. Fournis uniquement du code fonctionnel et bien structuré."}
    ]

    # Charge la clé API
    with open("agent_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    api_key = config["gpt4_api_key"]
    model = config.get("gpt4_model", "gpt-4o")
    client = OpenAI(api_key=api_key)

    while True:
        try:
            prompt = input("👨‍💻 Vous : ")
            if prompt.strip().lower() in ["exit", "quit"]:
                break
            context.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=model,
                messages=context
            )
            answer = response.choices[0].message.content
            print("🤖 CodeGPT :\n" + answer + "\n")
            context.append({"role": "assistant", "content": answer})
        except Exception as e:
            print(f"❌ Erreur : {e}")
            break
