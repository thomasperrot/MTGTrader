#!/usr/bin/env bash

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
echo "Starting worker..."
celery worker --app=config.celery:app --loglevel=INFO -S django -B