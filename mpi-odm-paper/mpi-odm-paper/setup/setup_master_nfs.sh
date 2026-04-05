#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y nfs-kernel-server

sudo mkdir -p /mnt/mpi-odm/{dataset/images,chunks,results,final}
sudo chown -R $USER:$USER /mnt/mpi-odm

EXPORT_LINE="/mnt/mpi-odm *(rw,sync,no_subtree_check,no_root_squash)"

if ! grep -q "/mnt/mpi-odm" /etc/exports; then
  echo "$EXPORT_LINE" | sudo tee -a /etc/exports
fi

sudo exportfs -ra
sudo systemctl restart nfs-kernel-server

echo "Master NFS setup done."