
from django.shortcuts import render


def index(request):
    return render(request, 'regapp_site/index.j2', {})
