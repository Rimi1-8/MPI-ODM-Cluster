#!/usr/bin/env bash
set -e

ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa || true

for host in worker1 worker2 worker3; do
  ssh-copy-id "$USER@$host"
done

echo "Passwordless SSH setup complete."