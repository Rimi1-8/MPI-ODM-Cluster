# MPI-ODM Distributed System Deployment Guide

This guide provides instructions to deploy the MPI-based OpenDroneMap architecture on new systems, supporting both Single-Machine execution testing as well as scalable Multi-Node environments. 

## 1. Prerequisites (For Windows Systems)

To set up this architecture on a target environment, ensure the following applications map seamlessly:
1.  **Python 3.10+**: Ensure standard Python environment execution is available.
2.  **Microsoft MPI (MS-MPI)**: For Windows nodes mimicking the OpenMPI wrapper. 
    * To install, download and run `msmpisetup.exe` and `msmpisdk.msi` from Microsoft.
    * *(Note: To run on Ubuntu/Linux natively as in the base paper, install `openmpi-bin` and `libopenmpi-dev`.)*
3.  **Docker Desktop / Engine**: Enables the backend `NodeODM` container logic.

## 2. Environment Initialization

Pull the project from the compressed `.zip` package and navigate into the root directory.

1.  **Initialize Virtual Environment:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate  # On Linux use: source venv/bin/activate
    ```
2.  **Install Library Dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```
    *(Essential modules: `mpi4py`, `pyodm`, `trimesh`, `numpy`)*

3.  **Spin up NodeODM Backend Container:**
    You must maintain a live active Docker endpoint mapping port `3000`.
    ```powershell
    docker run -d -p 3000:3000 opendronemap/nodeodm
    ```

## 3. Configuring Topologies & Targets

### Option A: Local Single-System Execution (Baseline Mapping)
This simulates a 4-node cluster entirely natively on your host machine to verify integration pipelines.
1. Modify the `hosts` file securely to map `localhost slots=4`. 
2. Verify that `config/cluster_config.json` points to local nodes. 
    ```json
    "nodes": [
      { "rank": 0, "name": "worker0", "host": "localhost" },
      { "rank": 1, "name": "worker1", "host": "localhost" }
    ]
    ```

### Option B: True Multi-System Distributed Setup
To execute calculations across separate physical PCs, network IP addresses must replace `localhost` settings.
1. Map Target IPs in the `hosts` sequence:
    ```text
    192.168.1.10 slots=1
    192.168.1.11 slots=1
    ```
2. Mirror the target hostnames dynamically in `config/cluster_config.json`.
3. Assure NodeODM is actively listening to exposed ports on each respective IP address endpoint. 

## 4. Pipeline Execution 

This architecture triggers automatically via orchestrated bash or powershell workflows matching your respective OS. 

**For Windows Deployments:** 
Execute the bundled powershell wrapper. This will automatically split dataset segments natively based on subset dimensions, invoke MS-MPI mapping against the hosts routing table, initialize PyODM tracking loops, and stitch together terminal meshes. 
```powershell
powershell -ExecutionPolicy Bypass -File .\run_single_system.ps1
```

> **Note on Performance Metric:** OpenDroneMap natively dictates intensive calculation loads. Consider altering the options matrix in `config/cluster_config.json` switching values across `.fast-orthophoto` booleans to expedite low-tier system metric prototyping tests. 
