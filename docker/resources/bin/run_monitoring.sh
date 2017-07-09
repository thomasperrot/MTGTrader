#!/usr/bin/env bash

# wait for RabbitMQ server to start
sleep 10

echo "Starting monitoring..."
# broker and broker_api can't be specified in flowerconfig.py. Maybe a bug ?
flower --broker=amqp://guest:guest@rabbit:5672// --broker_api=http://guest:guest@rabbit:15672/api/ \
    --conf=/etc/flower/flowerconfig.py