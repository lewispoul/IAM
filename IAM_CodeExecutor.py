# IAM_CodeExecutor.py - Exécuteur de code sécurisé pour l'agent ChatGPT

import subprocess
import tempfile
import os
import json
import time
from pathlib import Path
import signal


class IAMCodeExecutor:
    def __init__(self, base_path="/home/lppou"):
        self.base_path = Path(base_path)
        self.temp_dir = self.base_path / "temp_execution"
        self.temp_dir.mkdir(exist_ok=True)
        self.max_execution_time = 300  # 5 minutes max
        
    def execute_python_code(self, code, working_dir=None):
        """Exécute du code Python de manière sécurisée"""
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.py', 
                dir=self.temp_dir, 
                delete=False
            ) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Définir le répertoire de travail
            if working_dir:
                work_path = self.base_path / working_dir
                if not work_path.exists():
                    work_path = self.base_path
            else:
                work_path = self.base_path
            
            # Exécuter le code
            result = subprocess.run(
                ['python3', temp_file_path],
                cwd=str(work_path),
                capture_output=True,
                text=True,
                timeout=self.max_execution_time
            )
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_file_path)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": "< 5min"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout: L'exécution a pris plus de 5 minutes",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'exécution: {str(e)}"
            }
    
    def execute_shell_command(self, command, working_dir=None):
        """Exécute une commande shell de manière sécurisée"""
        try:
            # Commandes dangereuses interdites
            dangerous_commands = [
                'rm -rf', 'sudo', 'chmod 777', 'mkfs', 'dd if=', 
                'reboot', 'shutdown', 'init 0', 'halt'
            ]
            
            if any(dangerous in command for dangerous in dangerous_commands):
                return {
                    "success": False,
                    "error": "Commande potentiellement dangereuse interdite"
                }
            
            # Définir le répertoire de travail
            if working_dir:
                work_path = self.base_path / working_dir
                if not work_path.exists():
                    work_path = self.base_path
            else:
                work_path = self.base_path
            
            # Exécuter la commande
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(work_path),
                capture_output=True,
                text=True,
                timeout=self.max_execution_time
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout: La commande a pris plus de 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'exécution: {str(e)}"
            }
    
    def install_python_package(self, package_name):
        """Installe un package Python via pip"""
        try:
            result = subprocess.run(
                ['pip3', 'install', package_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "package": package_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'installation: {str(e)}"
            }
    
    def run_jupyter_notebook(self, notebook_path):
        """Lance un notebook Jupyter (si installé)"""
        try:
            full_path = self.base_path / notebook_path
            if not full_path.exists():
                return {"error": "Notebook non trouvé"}
            
            # Lancer Jupyter en arrière-plan
            process = subprocess.Popen(
                ['jupyter', 'notebook', str(full_path), '--no-browser'],
                cwd=str(self.base_path)
            )
            
            return {
                "success": True,
                "message": "Jupyter Notebook lancé",
                "pid": process.pid,
                "url": "http://localhost:8888"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur Jupyter: {str(e)}"
            }
    
    def execute_xtb_calculation(self, xyz_file_path, method="gfn2"):
        """Exécute un calcul XTB"""
        try:
            full_path = self.base_path / xyz_file_path
            if not full_path.exists():
                return {"error": "Fichier XYZ non trouvé"}
            
            # Commande XTB
            command = f"xtb {full_path} --{method} --opt"
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(full_path.parent),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes pour XTB
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "method": method,
                "input_file": str(xyz_file_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur XTB: {str(e)}"
            }
    
    def cleanup_temp_files(self):
        """Nettoie les fichiers temporaires"""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
            return {"success": True, "message": "Fichiers temporaires nettoyés"}
        except Exception as e:
            return {"error": f"Erreur lors du nettoyage: {str(e)}"}
