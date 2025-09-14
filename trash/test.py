import openai
import yaml

with open("agent_config.yaml") as f:
    cfg = yaml.safe_load(f)

openai.api_key = cfg["gpt4_api_key"]

models = openai.Model.list()
for m in models["data"]:
    print(m["id"])

