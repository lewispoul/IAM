import os
import shutil
from datetime import datetime

def clean_project_structure():
    base_path = '/home/pouli/IAM'
    log_file = os.path.join(base_path, 'cleaning_log.txt')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    folders = {
        'IAM_GUI': ['backend.py', 'templates', 'static', 'script.js', 'style.css'],
        'IAM_Tools': ['xtb_wrapper.py', 'iam_molecule_engine.py', 'IAM_Agent.py'],
        'IAM_Knowledge': ['*.json', '*.csv'],
        'IAM_Results': ['*.json', '*.log', '*.xyz', '*.cube', '*.zip'],
        'IAM_Datasets': ['*.csv', '*.xlsx', '*.pkl'],
        'IAM_Notebooks': ['*.ipynb'],
        'trash': []
    }

    with open(log_file, 'a') as log:
        log.write(f"\n--- Cleaning Log: {now} ---\n")

        for folder, patterns in folders.items():
            folder_path = os.path.join(base_path, folder)
            os.makedirs(folder_path, exist_ok=True)

            for pattern in patterns:
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.endswith(pattern.split('.')[-1]) or file in patterns:
                            src = os.path.join(root, file)
                            dest = os.path.join(folder_path, file)
                            if src != dest and base_path in src:
                                shutil.move(src, dest)
                                log.write(f"Moved {src} to {dest}\n")

        # Move orphaned files to trash
        trash_path = os.path.join(base_path, 'trash')
        for root, dirs, files in os.walk(base_path):
            for file in files:
                src = os.path.join(root, file)
                if base_path in src and not any(folder in src for folder in folders):
                    dest = os.path.join(trash_path, file)
                    shutil.move(src, dest)
                    log.write(f"Moved {src} to {dest}\n")

if __name__ == '__main__':
    clean_project_structure()
