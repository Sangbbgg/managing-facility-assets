#!/bin/bash
docker load < docker-images/asset-frontend.tar.gz
docker load < docker-images/asset-backend.tar.gz
docker load < docker-images/postgres-16.tar.gz
echo "이미지 로드 완료"
