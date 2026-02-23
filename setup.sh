#!/usr/bin/env bash
set -e

if [ ! -f frontend/.env ]; then
  cp frontend/.env_example frontend/.env
  echo "Created frontend/.env"
else
  echo "frontend/.env already exists"
fi

if [ ! -f backend/.env ]; then
  cp backend/.env_example backend/.env
  echo "Created backend/.env"
else
  echo "backend/.env already exists"
fi

docker compose -f docker/docker-compose.yml up --build