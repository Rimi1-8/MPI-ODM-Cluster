import zipfile
import os
import sys

def create_project_zip(zip_filename, source_dir):
    print(f"Creating zip file: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude massive or unnecessary directories
            if any(part in ['venv', '.git', '__pycache__'] for part in root.split(os.sep)):
                continue

            for file in files:
                # Do not zip the script itself or the target zip
                if file == os.path.basename(zip_filename) or file == 'make_zip.py':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"Skipping {arcname} due to error: {e}")
                    
    print(f"Successfully created {zip_filename}")

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else 'MPI-ODM_Project_Implementation.zip'
    create_project_zip(out_path, ".")
