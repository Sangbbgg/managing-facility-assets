#!/bin/bash
set -e
cp -n .env.example .env || true
docker compose build
docker compose up -d
echo "배포 완료. 상태 확인:"
docker compose ps
