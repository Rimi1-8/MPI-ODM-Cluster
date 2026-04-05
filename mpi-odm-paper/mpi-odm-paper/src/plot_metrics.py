import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image

def create_latency_graph():
    labels = ['Single Node', 'Dual Nodes', 'Triad Cluster', 'Quad Array']
    total_time = [7.2, 4.5, 4.0, 3.05] # In minutes

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, total_time, color=['#e74c3c', '#2ecc71', '#3498db', '#9b59b6'], width=0.5)
    
    ax.set_ylabel('Total Pipeline Execution Time (Minutes)')
    ax.set_title('Distributed Parallel Processing Latency Scaling')
    ax.set_ylim(0, 10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height} mins',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig('shared/final/graph_latency_v3.png', dpi=300)
    print("Saved graph_latency_v3.png")

def create_workload_graph():
    labels = ['Single Node', 'Dual Nodes', 'Triad Cluster', 'Quad Array']
    vertices = [144.09, 404.0, 480.99, 485.83] # in thousands
    faces = [247.46, 682.0, 839.60, 844.96]    # in thousands

    x = np.arange(len(labels)) 
    width = 0.35  

    fig, ax = plt.subplots(figsize=(11, 7))
    
    rects1 = ax.bar(x - width/2, vertices, width, label='Vertices (x1000)', color='#3498db')
    rects2 = ax.bar(x + width/2, faces, width, label='Faces (x1000)', color='#f39c12')

    ax.set_ylabel('Metric Output Volume (In Thousands)')
    ax.set_title('Topographic Compute Execution Scaling Topology')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=0, fontsize=8)

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    plt.savefig('shared/final/graph_workload_v3.png', dpi=300)
    print("Saved graph_workload_v3.png")

if __name__ == '__main__':
    os.makedirs('shared/final', exist_ok=True)
    create_latency_graph()
    create_workload_graph()
