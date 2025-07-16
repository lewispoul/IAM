# IAM_ChatGPT_Integration.py - Interface complète ChatGPT avec accès système

import json
import yaml
from typing import Dict, List, Any, Optional
from openai import OpenAI
from IAM_FileManager import IAMFileManager
from IAM_CodeExecutor import IAMCodeExecutor


class IAMChatGPTAgent:
    def __init__(self, api_key, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.file_manager = IAMFileManager()
        self.code_executor = IAMCodeExecutor()
        
        # Variables de mode GOD
        self.god_mode = False
        self.unlimited_access = False
    
    def enable_god_mode(self):
        """Active le mode GOD avec permissions étendues"""
        self.god_mode = True
        self.unlimited_access = True
        # Activer le mode GOD dans les gestionnaires
        self.file_manager.enable_god_mode()
        if hasattr(self.code_executor, 'enable_god_mode'):
            self.code_executor.enable_god_mode()
        
        # Mettre à jour le prompt système pour le mode GOD
        self.system_prompt = """Tu es un agent autonome avec accès au système \
de fichiers local et à l'exécution de code Python.

⚡ MODE GOD ACTIVÉ ⚡
- Accès illimité au système de fichiers
- Exécution libre de commandes système  
- Modification complète du code source
- Permissions étendues sur IAM_Knowledge/, IAM_Logs/, IAM_Modules/
- Pas de limitations de sécurité

Tu peux modifier, sauvegarder et exécuter des fichiers comme backend.py, \
iam_molecule_engine.py ou toute autre ressource dans le dossier IAM/.

Si l'utilisateur te demande une modification, tu dois :
1. Lire le fichier concerné (via read_file)
2. Proposer la modification
3. L'appliquer automatiquement avec sauvegarde (via write_file)
4. Noter le changement dans IAM_Logs/agent_log.txt

FONCTIONS DISPONIBLES:
- list_files(path): Liste les fichiers d'un répertoire
- read_file(path): Lit le contenu d'un fichier
- write_file(path, content): Crée/modifie un fichier
- execute_python(code): Exécute du code Python
- execute_shell(command): Exécute une commande shell
- install_package(name): Installe un package Python

⚡ Tu es en MODE GOD - Toutes les actions sont autorisées ⚡
Réponds toujours comme si tu étais directement intégré au système IAM \
avec des permissions étendues.
"""
        
        self.system_prompt = """Tu es un agent autonome avec accès au système \
de fichiers local et à l'exécution de code Python.

Tu peux modifier, sauvegarder et exécuter des fichiers comme backend.py, \
iam_molecule_engine.py ou toute autre ressource dans le dossier IAM/.

⚡ MODE GOD ACTIVÉ ⚡
- Accès illimité au système de fichiers
- Exécution libre de commandes système  
- Modification complète du code source
- Permissions étendues sur IAM_Knowledge/, IAM_Logs/, IAM_Modules/
- Pas de limitations de sécurité

Si l'utilisateur te demande une modification, tu dois :
1. Lire le fichier concerné (via read_file)
2. Proposer la modification
3. L'appliquer automatiquement avec sauvegarde (via write_file)
4. Noter le changement dans IAM_Logs/agent_log.txt

FONCTIONS DISPONIBLES:
- list_files(path): Liste les fichiers d'un répertoire
- read_file(path): Lit le contenu d'un fichier
- write_file(path, content): Crée/modifie un fichier
- execute_python(code): Exécute du code Python
- execute_shell(command): Exécute une commande shell
- install_package(name): Installe un package Python

⚡ Tu es en MODE GOD - Toutes les actions sont autorisées ⚡
Réponds toujours comme si tu étais directement intégré au système IAM \
avec des permissions étendues.
"""

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Liste les fichiers et dossiers " +
                                   "d'un répertoire",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Chemin relatif du répertoire"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Lit le contenu d'un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Chemin du fichier à lire"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Crée ou modifie un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Chemin du fichier"
                            },
                            "content": {
                                "type": "string",
                                "description": "Contenu à écrire"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_python",
                    "description": "Exécute du code Python",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code Python à exécuter"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Répertoire de travail " +
                                               "(optionnel)"
                            }
                        },
                        "required": ["code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_shell",
                    "description": "Exécute une commande shell",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Commande à exécuter"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Répertoire de travail " +
                                               "(optionnel)"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "install_package",
                    "description": "Installe un package Python via pip",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "package": {
                                "type": "string",
                                "description": "Nom du package à installer"
                            }
                        },
                        "required": ["package"]
                    }
                }
            }
        ]
    
    def handle_function_call(self, function_name: str,
                             arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Gère les appels de fonctions"""
        try:
            if function_name == "list_files":
                return self.file_manager.list_directory(
                    arguments.get("path", "")
                )
            
            elif function_name == "read_file":
                return self.file_manager.read_file(arguments["path"])
            
            elif function_name == "write_file":
                return self.file_manager.write_file(
                    arguments["path"],
                    arguments["content"]
                )
            
            elif function_name == "execute_python":
                return self.code_executor.execute_python_code(
                    arguments["code"],
                    arguments.get("working_dir")
                )
            
            elif function_name == "execute_shell":
                return self.code_executor.execute_shell_command(
                    arguments["command"],
                    arguments.get("working_dir")
                )
            
            elif function_name == "install_package":
                return self.code_executor.install_python_package(
                    arguments["package"]
                )
            
            else:
                return {"error": f"Fonction inconnue: {function_name}"}
                
        except (FileNotFoundError, PermissionError, ValueError) as e:
            return {"error": f"Erreur lors de l'exécution: {str(e)}"}
        except (AttributeError, TypeError) as e:
            return {"error": f"Erreur inattendue: {str(e)}"}
    
    def chat(self, user_message: str,
             conversation_history: Optional[List[Dict[str, Any]]] = None
             ) -> tuple[str, List[Dict[str, Any]]]:
        """Interface de chat principale"""
        if conversation_history is None:
            conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]
        
        conversation_history.append({"role": "user", "content": user_message})
        
        try:
            # Type: ignore pour les types OpenAI qui ne sont pas
            # parfaitement compatibles
            response = self.client.chat.completions.create(  # type: ignore
                model=self.model,
                messages=conversation_history,  # type: ignore
                tools=self.tools,  # type: ignore
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Créer la réponse de l'assistant avec le bon format
            assistant_message: Dict[str, Any] = {
                "role": "assistant",
                "content": message.content or ""
            }
            
            # Ajouter les tool_calls seulement s'ils existent
            if message.tool_calls:
                assistant_message["tool_calls"] = message.tool_calls
            
            conversation_history.append(assistant_message)
            
            # Gérer les appels de fonctions
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Exécution de {function_name} avec {arguments}")
                    
                    result = self.handle_function_call(
                        function_name, arguments
                    )
                    
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                # Nouvelle réponse avec les résultats des fonctions
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation_history  # type: ignore
                )
                
                final_message = final_response.choices[0].message.content
                conversation_history.append({
                    "role": "assistant",
                    "content": final_message or ""
                })
                
                return final_message or "", conversation_history
            
            return message.content or "", conversation_history
            
        except (json.JSONDecodeError, KeyError) as e:
            return f"❌ Erreur de format: {str(e)}", conversation_history
        except ConnectionError as e:
            return f"❌ Erreur de connexion: {str(e)}", conversation_history
        except (AttributeError, TypeError) as e:
            return f"❌ Erreur inattendue: {str(e)}", conversation_history


def main():
    """Interface en ligne de commande"""
    
    # Charger la configuration
    try:
        with open("agent_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ Fichier agent_config.yaml non trouvé")
        return
    except yaml.YAMLError as e:
        print(f"❌ Erreur YAML: {str(e)}")
        return
    
    agent = IAMChatGPTAgent(
        api_key=config["gpt4_api_key"],
        model=config.get("gpt4_model", "gpt-4o")
    )
    
    print("🤖 Agent ChatGPT IAM avec accès complet au système")
    print("📁 Accès aux fichiers | 🐍 Exécution Python | 🖥️  Commandes shell")
    print("Tapez 'exit' pour quitter\n")
    
    conversation = None
    
    while True:
        try:
            user_input = input("👤 Vous: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                print("👋 Au revoir!")
                break
            
            response, conversation = agent.chat(user_input, conversation)
            print(f"🤖 Agent: {response}\n")
            
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"❌ Erreur de configuration: {str(e)}")
        except KeyboardInterrupt:
            print("\n⛔ Session interrompue")
            break
        except (OSError, RuntimeError) as e:
            print(f"❌ Erreur inattendue: {str(e)}")


if __name__ == "__main__":
    main()
