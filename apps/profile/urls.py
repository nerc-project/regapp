"""
regapp_site URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='profile_index'),
    path('index', views.index, name='profile_index'),
    path('claims', views.claims, name='profile_claims'),
    path('logout', views.logout, name='profile_logout'),
]
