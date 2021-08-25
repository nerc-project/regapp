
from django.shortcuts import render
import re
import json



def index(request):
    return render(request, 'registration/index.j2', {})

def claims(request):
    print(request.META)
    context = {
        'headers': request.META,
        'userinfo': {}
    }
    return render(request, 'registration/claims.j2', context)
