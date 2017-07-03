"""
@author: Thomas PERROT

Contains urls for stats app
"""


from django.conf.urls import url, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'^stats', views.StatisticsViewSet)
router.register(r'^prices', views.PriceViewSet)

app_name = 'stats'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^harvest-prices/', views.harvest_prices),
    url(r'^compute-features/', views.compute_features)
]
