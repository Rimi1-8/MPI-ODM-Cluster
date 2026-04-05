#!/usr/bin/env bash
set -e

MASTER_HOST=${1:-master}

sudo mkdir -p /mnt/mpi-odm

if ! mount | grep -q "/mnt/mpi-odm"; then
  sudo mount ${MASTER_HOST}:/mnt/mpi-odm /mnt/mpi-odm
fi

echo "${MASTER_HOST}:/mnt/mpi-odm /mnt/mpi-odm nfs defaults 0 0" | sudo tee -a /etc/fstab

echo "Worker NFS mount done on $(hostname)"