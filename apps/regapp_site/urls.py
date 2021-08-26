"""
regapp_site URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='site_index'),
    path('index', views.index, name='site_index'),
    path('claims', views.claims, name='site_claims'),
]
 