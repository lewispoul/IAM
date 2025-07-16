# IAM_FileManager.py - Gestionnaire de fichiers pour l'agent ChatGPT

import shutil
from pathlib import Path


class IAMFileManager:
    def __init__(self, base_path="/home/lppou"):
        self.base_path = Path(base_path)
        self.allowed_extensions = {
            '.py', '.txt', '.md', '.json', '.yaml', '.yml', '.csv',
            '.xyz', '.mol', '.pdb', '.log', '.sh', '.html', '.css', '.js'
        }
        # Mode GOD - désactive les restrictions de sécurité
        self.god_mode = False

    def enable_god_mode(self):
        """Active le mode GOD avec accès illimité"""
        self.god_mode = True
        # En mode GOD, autoriser tous les types de fichiers
        self.allowed_extensions = {
            '.py', '.txt', '.md', '.json', '.yaml', '.yml', '.csv',
            '.xyz', '.mol', '.pdb', '.log', '.sh', '.html', '.css', '.js',
            '.conf', '.cfg', '.ini', '.xml', '.sql', '.c', '.cpp', '.h',
            '.java', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.ts',
            '.jsx', '.vue', '.svelte', '.scss', '.less', '.sql', '.db'
        }

    def is_safe_path(self, path):
        """Vérifie si le chemin est sécurisé - désactivé en mode GOD"""
        if self.god_mode:
            return True  # Pas de restrictions en mode GOD
        try:
            full_path = self.base_path / path
            full_path.resolve().relative_to(self.base_path.resolve())
            return True
        except ValueError:
            return False

    def list_directory(self, path=""):
        """Liste le contenu d'un répertoire"""
        try:
            if not self.is_safe_path(path):
                return {"error": "Chemin non autorisé"}

            dir_path = self.base_path / path
            if not dir_path.exists():
                return {"error": "Répertoire non trouvé"}

            items = []
            for item in dir_path.iterdir():
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime
                }
                items.append(item_info)

            return {
                "success": True,
                "items": items,
                "path": str(path)
            }
        except Exception as e:
            return {
                "error": f"Erreur lors de la lecture du répertoire: {str(e)}"
            }

    def read_file(self, path):
        """Lit le contenu d'un fichier"""
        try:
            if not self.is_safe_path(path):
                return {"error": "Chemin non autorisé"}

            file_path = self.base_path / path
            if not file_path.exists():
                return {"error": "Fichier non trouvé"}

            # Vérifier l'extension (sauf en mode GOD)
            if not self.god_mode and file_path.suffix not in self.allowed_extensions:
                return {
                    "error": f"Type de fichier non autorisé: "
                             f"{file_path.suffix}"
                }

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "path": str(path),
                "size": len(content)
            }
        except Exception as e:
            return {
                "error": f"Erreur lors de la lecture du fichier: {str(e)}"
            }

    def write_file(self, path, content, mode="w"):
        """Écrit du contenu dans un fichier"""
        try:
            if not self.is_safe_path(path):
                return {"error": "Chemin non autorisé"}

            file_path = self.base_path / path

            # Créer les répertoires parents si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Vérifier l'extension (sauf en mode GOD)
            if not self.god_mode and file_path.suffix not in self.allowed_extensions:
                return {
                    "error": f"Type de fichier non autorisé: "
                             f"{file_path.suffix}"
                }

            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)

            action = 'créé' if mode == 'w' else 'modifié'
            return {
                "success": True,
                "path": str(path),
                "message": f"Fichier {action} avec succès"
            }
        except Exception as e:
            return {
                "error": f"Erreur lors de l'écriture du fichier: {str(e)}"
            }

    def create_directory(self, path):
        """Crée un répertoire"""
        try:
            if not self.is_safe_path(path):
                return {"error": "Chemin non autorisé"}

            dir_path = self.base_path / path
            dir_path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "path": str(path),
                "message": "Répertoire créé avec succès"
            }
        except Exception as e:
            return {
                "error": f"Erreur lors de la création du répertoire: {str(e)}"
            }

    def delete_file(self, path):
        """Supprime un fichier"""
        try:
            if not self.is_safe_path(path):
                return {"error": "Chemin non autorisé"}

            file_path = self.base_path / path
            if not file_path.exists():
                return {"error": "Fichier non trouvé"}

            if file_path.is_file():
                file_path.unlink()
                return {
                    "success": True,
                    "message": "Fichier supprimé avec succès"
                }
            else:
                return {"error": "Le chemin ne correspond pas à un fichier"}
        except Exception as e:
            return {"error": f"Erreur lors de la suppression: {str(e)}"}

    def move_file(self, src_path, dst_path):
        """Déplace ou renomme un fichier"""
        try:
            safe_src = self.is_safe_path(src_path)
            safe_dst = self.is_safe_path(dst_path)
            if not safe_src or not safe_dst:
                return {"error": "Chemin non autorisé"}

            src = self.base_path / src_path
            dst = self.base_path / dst_path

            if not src.exists():
                return {"error": "Fichier source non trouvé"}

            # Créer les répertoires parents si nécessaire
            dst.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(src), str(dst))
            return {
                "success": True,
                "message": f"Fichier déplacé de {src_path} vers {dst_path}"
            }
        except Exception as e:
            return {"error": f"Erreur lors du déplacement: {str(e)}"}

    def search_files(self, pattern, directory=""):
        """Recherche des fichiers par motif"""
        try:
            if not self.is_safe_path(directory):
                return {"error": "Chemin non autorisé"}

            search_path = self.base_path / directory
            matches = []

            for file_path in search_path.rglob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.base_path)
                    matches.append(str(relative_path))

            return {
                "success": True,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {"error": f"Erreur lors de la recherche: {str(e)}"}
