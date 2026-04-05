#!/usr/bin/env bash
set -e

docker rm -f nodeodm >/dev/null 2>&1 || true

docker run -d \
  --name nodeodm \
  --restart unless-stopped \
  -p 3000:3000 \
  opendronemap/nodeodm

sleep 5
curl http://localhost:3000/info || true
echo
echo "NodeODM started on $(hostname)"