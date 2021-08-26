
from django.shortcuts import render


def index(request):
    return render(request, 'registration/index.j2', {})


def claims(request):
    print(request.META)
    context = {
        'headers': request.META,
        'userinfo': request.oidc_userinfo
    }
    return render(request, 'registration/claims.j2', context)  
