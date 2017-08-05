"""
@author: Thomas PERROT

Contains urls for cards app
"""


from django.conf.urls import url, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()

router.register(r'^cards', views.CardViewSet)
router.register(r'^name', views.CardNameViewSet)

app_name = 'cards'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^harvest-cards/', views.harvest_cards),
    url(r'^harvest-sets/', views.harvest_sets)
]
