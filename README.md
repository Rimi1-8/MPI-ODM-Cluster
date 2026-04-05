# MPI ODM Paper-Style Implementation

This project reproduces the architecture described in the paper:
- 4 nodes
- OpenMPI
- OpenDroneMap / NodeODM
- NFS shared directory
- PyODM to control ODM on each node
- trimesh to merge outputs on node 1
- manual translation in merge step

## Nodes
- Node 1 = master + NFS server + merge node
- Node 2 = worker
- Node 3 = worker
- Node 4 = worker

## Required
- Ubuntu on all systems
- Same LAN
- SSH connectivity
- NFS shared folder mounted on all nodes
- Docker installed
- NodeODM running on each node
- Python venv with mpi4py, pyodm, trimesh

## Execution flow
1. Put images in shared/dataset/images
2. Split dataset
3. Run MPI program
4. Merge models on node 1

## Run
```bash
bash run_cluster.sh
```
