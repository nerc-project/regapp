"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.urls import re_path, include

"""
regapp URL Configuration
"""

urlpatterns = [
    re_path(r'^', include('regapp.apps.regapp.urls')),
]
