![][py35] [![GitHub forks][forks]][network] [![GitHub stars][stars]][stargazers] [![GitHub license][license]][lic_file]

# MTGTrader

A micro trading tool to predict Magic The Gathering cards prices. :boom:

## Overview

* This project crawls data from different sources and uses machine learning model to predict Magic The Gathering cards price.
* Collected data are cards prices and last major tournaments. Price data are collected from magiccardmarket.eu, and tournament data from mtgtop8.com.
* All data in the application can be accessed through a REST API

## Environment, Architecture

This project contains two parts:

* a Django application that contains all the logic.
* a VueJS application to display results.

To start the hole application:
```bash
$ ./script/install_app.sh
$ ./script/restart_app.sh
```

## Entry points

The Django application allows the user to:

* view data in a REST API
* manage database and schedule tasks in the Django admin interface (with django-celery-beat plugin)
* manage queues and exchanges in RabbitMQ management interface
* visualize monitoring dashboards about tasks (with Flower, a celery plugin). Picture is below.

![Flower dashboard][flower]

## Credits

This project relies on a research paper "Prediction of Price Increase for Magic: The Gathering Cards", published by Matthew Pawlicki, Joseph Polin and Jesse Zhang, from Stanford University. This paper is available in the doc folder.


[py35]: https://img.shields.io/badge/python-3.5-brightgreen.svg

[issues_img]: https://img.shields.io/github/issues/thomasperrot/MTGTrader.svg
[issues]: https://github.com/thomasperrot/MTGTrader/issues

[forks]: https://img.shields.io/github/forks/thomasperrot/MTGTrader.svg
[network]: https://github.com/thomasperrot/MTGTrader/network

[stars]: https://img.shields.io/github/stars/thomasperrot/MTGTrader.svg
[stargazers]: https://github.com/thomasperrot/MTGTrader/stargazers

[license]: https://img.shields.io/badge/license-MIT-blue.svg
[lic_file]: https://raw.githubusercontent.com/thomasperrot/MTGTrader/master/LICENCE.txt

[flower]: https://raw.githubusercontent.com/thomasperrot/MTGTrader/master/doc/img/flower_dashboard.png