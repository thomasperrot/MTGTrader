# Backend app

## The architecure

The backend has at least 4 components, that run in Docker containers:

* a web serveur (Django)
* one or more workers (Celery)
* a scheduler (Celerybeat)
* a monitoring module (Flower)

It is aimed at running on a RaspberryPi cluster (currenlty in progress)

## The web server

The web server contains all the logic and has several apps:

* the sets app manages sets and booster
* the cards app manages all the cards
* the tournaments app manages all the data about tournaments
* the features app manages all the data about machine learning features and card prices

It runs with the following technologies:

* Django, for web server, ORM and admin interface
* Celery, to compute all the heavy tasks (crawling, machine learning computing, etc.)
* RabbitMQ and Redis (for Celery)
* Postgresql, as the storage database used by Django.
* Docker, to have a flexible architecture

## Workers, scheduler and monitoring

* The workers, the scheduler and the monitoring components send and receive tasks. Their code is the same as the web server component, and uses the same technologies.