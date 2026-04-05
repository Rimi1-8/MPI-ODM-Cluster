import os
import sys
from pathlib import Path

# Ensure src/ is on the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import load_config


def main():
    cfg = load_config()
    print("=== Output Verification ===\n")

    all_ok = True
    for node in cfg["nodes"]:
        rank = node["rank"]
        result_dir = os.path.join(cfg["results_dir"], f"node_{rank}")
        print(f"Node {rank} ({node['name']}): {result_dir}")

        if not os.path.exists(result_dir):
            print("  [MISSING] Result directory not found!")
            all_ok = False
            continue

        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(result_dir):
            level = root.replace(result_dir, "").count(os.sep)
            indent = "  " * (level + 1)
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = "  " * (level + 2)
            for f in files[:15]:
                fpath = os.path.join(root, f)
                fsize = os.path.getsize(fpath)
                total_size += fsize
                file_count += 1
                print(f"{sub_indent}{f} ({fsize:,} bytes)")
            if len(files) > 15:
                print(f"{sub_indent}... and {len(files) - 15} more files")

        print(f"  Total: {file_count} files, {total_size:,} bytes")
        print()

    if all_ok:
        print("[OK] All node outputs present.")
    else:
        print("[WARN] Some node outputs are missing!")


if __name__ == "__main__":
    main()