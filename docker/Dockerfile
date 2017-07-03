FROM python:3.5
ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work&
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./bin/run_web.sh /app/run_web.sh
RUN chmod +x /app/run_web.sh

COPY ./bin/run_celery.sh /app/run_celery.sh
RUN chmod +x /app/run_celery.sh

COPY ./bin/run_beat.sh /app/run_beat.sh
RUN chmod +x /app/run_beat.sh

COPY ./bin/run_monitoring.sh /app/run_monitoring.sh
RUN chmod +x /app/run_monitoring.sh

RUN mkdir -p /etc/flower /var/flower/db
COPY ./compose/flower/flowerconfig.py /etc/flower/flowerconfig.py

COPY ./mtg /app
WORKDIR /app

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser