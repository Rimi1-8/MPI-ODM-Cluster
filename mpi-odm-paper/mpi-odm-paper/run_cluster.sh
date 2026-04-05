#!/usr/bin/env bash
set -e

source ~/mpi-odm-venv/bin/activate

echo "Step 1: Split dataset"
python3 src/split_dataset.py

echo "Step 2: MPI hello test"
mpirun --hostfile hosts -np 4 python3 src/hello_mpi.py

echo "Step 3: Run distributed ODM"
mpirun --hostfile hosts -np 4 python3 src/mpi_odm_main.py

echo "Step 4: Verify outputs"
python3 src/verify_outputs.py

echo "Step 5: Merge models on master"
python3 src/merge_models.py

echo "Done."