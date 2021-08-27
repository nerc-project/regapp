"""
regapp_site URL Configuration
"""

from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='site_index'),
    path('index', views.index, name='site_index'),
    path(
        'reglanding',
        TemplateView.as_view(template_name="regapp_site/reglanding.j2"),
        name='registration_landing'
    )
]
      