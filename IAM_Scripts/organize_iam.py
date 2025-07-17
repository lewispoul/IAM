import os
import shutil
from datetime import datetime, timedelta

# Define directories
TRASH_DIR = "trash"
MOLECULES_DIR = "IAM_Knowledge/Molecules"
REFERENCES_DIR = "IAM_Knowledge/References"
RESULTS_DIR = "IAM_Results"
MODULES_DIR = "IAM_Modules"
STATIC_DIR = "IAM_GUI/static"
DOCS_DIR = "IAM_Docs"
SCRIPTS_DIR = "IAM_Scripts"
TEMP_RESULTS_DIR = "IAM_TempResults"
DATA_DIR = "IAM_Data"

# File categorization
FILE_CATEGORIES = {
    "trash": [".Zone.Identifier"],
    "molecules": ["methane_test.xyz", "nitromethane.xyz"],
    "references": ["chem-env.yaml", "requirements.txt"],
    "modules": ["xtb_wrapper.py", "IAM_StabilityPredictor.py", "main.py", "iam_update_db.py"],
    "static": ["script.js", "style.css"],
    "docs": ["README.md"],
    "scripts": ["*.sh", "*.py"],
    "temp_results": ["*.xyz", "*.mol", "*.log", "*.json", "charges", "wbo", "xtbopt.xyz", "xtbrestart"]
}

# Enhanced file categorization
FILE_CATEGORIES.update({
    "temp_results": ["*.log", "*.json", "*.txt"],
    "docs": ["IAM_StatusDashboard.html"],
})

# Move files to appropriate directories
def move_files():
    log_entries = []
    for category, patterns in FILE_CATEGORIES.items():
        target_dir = globals().get(f"{category.upper()}_DIR")
        if not target_dir:
            continue
        os.makedirs(target_dir, exist_ok=True)
        for root, dirs, files in os.walk("."):
            for file in files:
                for pattern in patterns:
                    if file.endswith(pattern) or pattern in file:
                        old_path = os.path.join(root, file)
                        new_path = os.path.join(target_dir, file)
                        shutil.move(old_path, new_path)
                        log_entries.append(f"Moved {old_path} to {new_path}")
                        print(f"Moved {old_path} to {new_path}")

    # Handle uncategorized files
    for root, dirs, files in os.walk("."):
        for file in files:
            old_path = os.path.join(root, file)
            if not any(file.endswith(pattern) or pattern in file for patterns in FILE_CATEGORIES.values()):
                new_path = os.path.join(TRASH_DIR, file)
                shutil.move(old_path, new_path)
                log_entries.append(f"Moved uncategorized {old_path} to {new_path}")
                print(f"Moved uncategorized {old_path} to {new_path}")

    # Write log
    with open("organize_log.txt", "w") as log_file:
        log_file.write("\n".join(log_entries))

# Merge xtb_output into TEMP_RESULTS_DIR
def merge_xtb_output():
    xtb_output_dir = "xtb_output"
    if os.path.exists(xtb_output_dir):
        for root, dirs, files in os.walk(xtb_output_dir):
            for file in files:
                old_path = os.path.join(root, file)
                new_path = os.path.join(TEMP_RESULTS_DIR, file)
                shutil.move(old_path, new_path)
                print(f"Merged {old_path} into {new_path}")

# Clear old files from trash
def clear_old_results(days=30):
    cutoff_date = datetime.now() - timedelta(days=days)
    for root, dirs, files in os.walk(TRASH_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff_date:
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")

# Function to restore files from trash
def restore_files():
    log_entries = []
    for root, dirs, files in os.walk(TRASH_DIR):
        for file in files:
            if file.endswith(".sh") or file.endswith(".py"):
                new_path = os.path.join(SCRIPTS_DIR, file)
            elif file.endswith(".html") or file.endswith(".md"):
                new_path = os.path.join(DOCS_DIR, file)
            elif file.endswith(".xyz") or file.endswith(".mol") or file.endswith(".json"):
                new_path = os.path.join(TEMP_RESULTS_DIR, file)
            else:
                continue

            old_path = os.path.join(root, file)
            shutil.move(old_path, new_path)
            log_entries.append(f"Restored {old_path} to {new_path}")
            print(f"Restored {old_path} to {new_path}")

    # Write log
    with open("organize_log.txt", "a") as log_file:
        log_file.write("\n".join(log_entries))

# Function to undo all file movements
def undo_file_movements():
    log_entries = []
    for root, dirs, files in os.walk(SCRIPTS_DIR):
        for file in files:
            old_path = os.path.join(root, file)
            new_path = os.path.join(".", file)
            shutil.move(old_path, new_path)
            log_entries.append(f"Moved {old_path} back to {new_path}")
            print(f"Moved {old_path} back to {new_path}")

    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            old_path = os.path.join(root, file)
            new_path = os.path.join(".", file)
            shutil.move(old_path, new_path)
            log_entries.append(f"Moved {old_path} back to {new_path}")
            print(f"Moved {old_path} back to {new_path}")

    for root, dirs, files in os.walk(TEMP_RESULTS_DIR):
        for file in files:
            old_path = os.path.join(root, file)
            new_path = os.path.join(".", file)
            shutil.move(old_path, new_path)
            log_entries.append(f"Moved {old_path} back to {new_path}")
            print(f"Moved {old_path} back to {new_path}")

    # Write log
    with open("undo_log.txt", "w") as log_file:
        log_file.write("\n".join(log_entries))

# Function to restore all files to their original locations

def restore_to_root():
    log_entries = []
    directories = [SCRIPTS_DIR, DOCS_DIR, TEMP_RESULTS_DIR, TRASH_DIR]

    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                old_path = os.path.join(root, file)
                new_path = os.path.join(".", file)
                shutil.move(old_path, new_path)
                log_entries.append(f"Moved {old_path} back to {new_path}")
                print(f"Moved {old_path} back to {new_path}")

    # Write log
    with open("restore_log.txt", "w") as log_file:
        log_file.write("\n".join(log_entries))

if __name__ == "__main__":
    move_files()
    merge_xtb_output()
    clear_old_results()
    restore_files()
    undo_file_movements()
    restore_to_root()

# déplacé par organize_iam.py
