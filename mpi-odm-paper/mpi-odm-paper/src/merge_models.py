import os
import sys
from pathlib import Path

# Ensure src/ is on the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import trimesh
from utils import load_config, ensure_dir


def find_mesh_file(node_result_dir):
    """Search for mesh output files in common ODM output locations."""
    candidates = [
        os.path.join(node_result_dir, "odm_texturing", "odm_textured_model_geo.obj"),
        os.path.join(node_result_dir, "odm_texturing", "odm_textured_model.obj"),
        os.path.join(node_result_dir, "odm_meshing", "odm_mesh.ply"),
        os.path.join(node_result_dir, "odm_meshing", "odm_mesh.obj"),
        os.path.join(node_result_dir, "odm_texturing", "odm_textured_model.glb"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    # Fallback: search recursively for any .obj or .ply file
    for root, dirs, files in os.walk(node_result_dir):
        for f in files:
            if f.endswith(('.obj', '.ply', '.glb')):
                return os.path.join(root, f)

    return None


def main():
    cfg = load_config()
    results_dir = cfg["results_dir"]
    final_dir = cfg["final_dir"]
    translations = cfg["translations"]

    ensure_dir(final_dir)

    meshes = []

    for rank_str, shift in translations.items():
        rank = int(rank_str)
        node_result_dir = os.path.join(results_dir, f"node_{rank}")
        mesh_path = find_mesh_file(node_result_dir)

        if not mesh_path:
            print(f"[WARN] No mesh found for node {rank} in {node_result_dir}")
            continue

        print(f"[INFO] Loading mesh for node {rank}: {mesh_path}")
        try:
            mesh = trimesh.load(mesh_path, force="mesh")
        except Exception as e:
            print(f"[WARN] Failed to load mesh for node {rank}: {e}")
            continue

        transform = np.eye(4)
        transform[:3, 3] = shift
        mesh.apply_transform(transform)
        meshes.append(mesh)
        print(f"[INFO]   Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")

    if not meshes:
        raise RuntimeError("No meshes found to merge.")

    print(f"\n[INFO] Merging {len(meshes)} meshes...")
    merged = trimesh.util.concatenate(meshes)

    output_obj = os.path.join(final_dir, "final_merged.obj")
    output_ply = os.path.join(final_dir, "final_merged.ply")

    merged.export(output_obj)
    merged.export(output_ply)

    print(f"\n[OK] Merged model stats:")
    print(f"  Vertices: {len(merged.vertices)}")
    print(f"  Faces: {len(merged.faces)}")
    print(f"[OK] Merged OBJ saved to {output_obj}")
    print(f"[OK] Merged PLY saved to {output_ply}")


if __name__ == "__main__":
    main()