import json
import os
from pathlib import Path


# Project root is one level up from src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(path=None):
    """Load cluster config with paths resolved relative to project root."""
    if path is None:
        path = PROJECT_ROOT / "config" / "cluster_config.json"
    else:
        path = Path(path)

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Resolve relative paths against project root
    for key in ("shared_root", "dataset_dir", "chunks_dir", "results_dir", "final_dir"):
        if key in cfg and not os.path.isabs(cfg[key]):
            cfg[key] = str(PROJECT_ROOT / cfg[key])

    return cfg


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def list_images(folder):
    folder = Path(folder)
    if not folder.exists():
        return []
    exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
    return sorted([str(p) for p in folder.iterdir() if p.suffix.lower() in exts])


def get_node_by_rank(cfg, rank):
    for node in cfg["nodes"]:
        if node["rank"] == rank:
            return node
    raise ValueError(f"No node found for rank {rank}")


def write_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)