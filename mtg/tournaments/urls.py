"""
@author: Thomas PERROT

Contains urls for tournaments app
"""


from django.conf.urls import url, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'^tournaments', views.TournamentViewSet)
router.register(r'^decks', views.DeckViewSet)
# router.register(r'^crawl', views.harvest_formats, base_name='crawl')

app_name = 'tournaments'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^crawl-formats', views.harvest_formats),
    url(r'^crawl-deck/([0-9]{6})/$', views.get_deck),
    url(r'^update-relevance/', views.update_relevance)
]
