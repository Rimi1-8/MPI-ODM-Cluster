import math
import shutil
import sys
from pathlib import Path

# Ensure src/ is on the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import load_config, list_images, ensure_dir


def main():
    cfg = load_config()
    dataset_dir = cfg["dataset_dir"]
    chunks_dir = Path(cfg["chunks_dir"])
    nodes = cfg["nodes"]

    images = list_images(dataset_dir)
    if not images:
        raise RuntimeError(f"No images found in {dataset_dir}")

    num_nodes = len(nodes)
    chunk_size = math.ceil(len(images) / num_nodes)

    for node in nodes:
        chunk_path = chunks_dir / f"chunk_{node['rank']}"
        ensure_dir(chunk_path)

        # clear old files
        for old in chunk_path.iterdir():
            if old.is_file():
                old.unlink()

    for idx, image_path in enumerate(images):
        rank = min(idx // chunk_size, num_nodes - 1)
        dst = chunks_dir / f"chunk_{rank}" / Path(image_path).name
        shutil.copy2(image_path, dst)

    print(f"Distributed {len(images)} images across {num_nodes} nodes.")
    for node in nodes:
        chunk_path = chunks_dir / f"chunk_{node['rank']}"
        count = len(list(chunk_path.glob("*")))
        print(f"  Rank {node['rank']} -> {count} images")


if __name__ == "__main__":
    main()