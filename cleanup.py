import os
import shutil

# Define directories
TRASH_DIR = "trash"
RESULTS_DIR = "IAM_Knowledge/Results"
SCRIPTS_DIR = "scripts"
CORE_DIR = "core"

# File extensions to move to trash
TRASH_EXTENSIONS = [".log", ".xyz", ".tmp"]

# Create directories if they don't exist
os.makedirs(TRASH_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(CORE_DIR, exist_ok=True)

# Move files to appropriate directories
def cleanup_files():
    for root, dirs, files in os.walk("."):
        for file in files:
            file_path = os.path.join(root, file)
            if any(file.endswith(ext) for ext in TRASH_EXTENSIONS):
                shutil.move(file_path, os.path.join(TRASH_DIR, file))
                print(f"Moved {file_path} to {TRASH_DIR}")
            elif file.endswith(".py"):
                shutil.move(file_path, os.path.join(SCRIPTS_DIR, file))
                print(f"Moved {file_path} to {SCRIPTS_DIR}")
            elif file.endswith(".json") or file.endswith(".csv"):
                shutil.move(file_path, os.path.join(RESULTS_DIR, file))
                print(f"Moved {file_path} to {RESULTS_DIR}")

if __name__ == "__main__":
    cleanup_files()
