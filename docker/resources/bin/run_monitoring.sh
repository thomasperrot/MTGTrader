#!/usr/bin/env bash

# wait for RabbitMQ server to start
sleep 10

echo "Starting monitoring..."
celery flower --app=config.celery:app --loglevel=INFO -S django --conf=/etc/flower/flowerconfig.py