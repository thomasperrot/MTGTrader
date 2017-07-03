#!/usr/bin/env bash

echo "Creating volume folders..."
mkdir -p volumes/postgres/backup
mkdir -p volumes/postgres/data

echo "Starting environment..."
docker-compose build
