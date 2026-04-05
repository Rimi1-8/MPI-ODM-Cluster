import trimesh
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def main():
    mesh_path = sys.argv[1] if len(sys.argv) > 1 else 'shared/final/final_merged.obj'
    if not os.path.exists(mesh_path):
        mesh_path = 'shared/final/final_merged.ply'
        if not os.path.exists(mesh_path):
            print("Cannot find merged mesh.")
            return

    print("Loading mesh...")
    mesh = trimesh.load(mesh_path, force='mesh')
    
    points = mesh.vertices
    if len(points) > 50000:
        idx = np.random.choice(len(points), 50000, replace=False)
        points = points[idx]

    print(f"Plotting {len(points)} points...")
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Attempt to extract color info if present, otherwise just blue
    colors = 'b'
    try:
        if hasattr(mesh.visual, 'vertex_colors') and len(mesh.visual.vertex_colors) > 0:
            c = mesh.visual.vertex_colors
            if len(c) > 50000: c = c[idx]
            colors = c[:, :3] / 255.0
    except:
        pass

    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=0.1, c=colors, depthshade=True)
    
    # Keep aspect ratio bounded roughly
    max_range = np.array([points[:, 0].max()-points[:, 0].min(), 
                          points[:, 1].max()-points[:, 1].min(), 
                          points[:, 2].max()-points[:, 2].min()]).max() / 2.0
    mid_x = (points[:, 0].max()+points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max()+points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max()+points[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Nice isometric/aerial angle
    ax.view_init(elev=60, azim=-45)
    ax.axis('off')
    
    out_path = 'shared/final/visualization.png'
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor='black')
    print(f"Saved visualization to {out_path}")

if __name__ == "__main__":
    main()
