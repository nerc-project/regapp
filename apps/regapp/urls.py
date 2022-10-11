"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.urls import path
from django.views.generic import TemplateView
from . import views

"""
regapp URL Configuration
"""

urlpatterns = [
    # ############################
    # Top-level, not-authenticated
    # ############################
    path(
        '',
        views.regapp.index,
        name='site_index'
    ),
    path(
        'index/',
        views.regapp.index,
        name='site_index'
    ),
    path(
        'reglanding/',
        TemplateView.as_view(template_name="regapp/reglanding.j2"),
        name='registration_landing'
    ),
    path(
        'validate/',
        views.validate.validate,
        name="site_validate"
    ),
    path(
        'terms/',
        views.regapp.terms,
        name="site_terms"
    ),
    # #######################################
    # Registration - authenticated at CILogon
    # #######################################
    path(
        'registration/',
        views.registration.registration,
        name='reg_home'
    ),
    path(
        'registration/claims/',
        views.regapp.claims,
        name='reg_claims'
    ),
    path(
        'registration/logout/',
        views.registration.logout,
        name='reg_logout'
    ),
    path(
        'registration/accountexists/',
        views.registration.accountexists,
        name='reg_accountexists'
    ),
    path(
        'registration/inflight/',
        views.registration.inflight,
        name='reg_inflight'
    ),
    path(
        'registration/sendvalidation/',
        views.registration.sendvalidation,
        name='reg_sendvalidation'
    ),
    # #################################
    # Profile - authenticated at MSS
    # #################################
    path(
        'profile/',
        views.profile.profile,
        name='profile_home'
    ),
    path(
        'profile/claims/',
        views.regapp.claims,
        name='profile_claims'
    ),
    path(
        'profile/logout/',
        views.profile.logout,
        name='profile_logout'
    ),
    path(
        'profile/sendupdate/',
        views.profile.sendupdate,
        name="profile_sendupdate"
    ),
]
