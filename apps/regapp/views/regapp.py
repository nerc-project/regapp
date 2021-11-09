"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.shortcuts import render
from django.views.decorators.cache import never_cache


def index(request):
    return render(request, 'regapp/index.j2', {})


@never_cache
def claims(request):
    print(request.META)
    context = {
        'headers': request.META,
        'userinfo': request.oidc_userinfo
    }
    return render(request, 'regapp/claims.j2', context)
