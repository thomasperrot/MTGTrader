#!/usr/bin/env bash

# wait for RabbitMQ server to start
sleep 10

echo "Starting beat..."
celery beat --app=config.celery:app --loglevel=INFO -S django