"""
registration URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='reg_index'),
    path('index', views.index, name='reg_index'),  
    path('claims', views.claims, name='reg_claims'),
]  
     