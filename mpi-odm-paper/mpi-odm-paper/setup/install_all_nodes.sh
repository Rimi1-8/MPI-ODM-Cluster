#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y \
  build-essential \
  python3 python3-pip python3-venv \
  openmpi-bin libopenmpi-dev \
  openssh-server \
  nfs-common \
  docker.io \
  curl wget git net-tools

sudo systemctl enable ssh
sudo systemctl start ssh

sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker "$USER"

python3 -m venv ~/mpi-odm-venv
source ~/mpi-odm-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true

echo "Installation complete on $(hostname)"