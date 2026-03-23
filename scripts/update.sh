#!/bin/bash
case "$1" in
  backend)  docker compose build asset-backend && docker compose up -d asset-backend ;;
  frontend) docker compose build asset-frontend && docker compose up -d asset-frontend ;;
  restart)  docker compose restart ;;
  *)        docker compose build && docker compose up -d ;;
esac
echo "완료: $1"
