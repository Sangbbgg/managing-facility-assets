#!/bin/bash
mkdir -p docker-images
docker save asset-mgmt-asset-frontend | gzip > docker-images/asset-frontend.tar.gz
docker save asset-mgmt-asset-backend  | gzip > docker-images/asset-backend.tar.gz
docker save postgres:16-alpine        | gzip > docker-images/postgres-16.tar.gz
echo "이미지 저장 완료 → docker-images/"
