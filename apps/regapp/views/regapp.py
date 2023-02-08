"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import never_cache


def index(request):
    return render(request, 'regapp/index.j2', {})


@never_cache
def claims(request):
    context = {
        'headers': request.META,
        'userinfo': request.oidc_userinfo
    }
    return render(request, 'regapp/claims.j2', context)


@never_cache
def terms(request):
    context = {
        'terms_name': settings.TERMS_NAME,
        'terms_version': settings.TERMS_VER,
        'terms_content': settings.TERMS_CONTENT
    }
    return render(request, 'regapp/terms.j2', context)
