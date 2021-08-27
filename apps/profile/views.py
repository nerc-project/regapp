from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse


def index(request):
    return render(request, 'profile/index.j2', {})


def claims(request):
    print(request.META)
    context = {
        'headers': request.META,
        'userinfo': request.oidc_userinfo
    }
    return render(request, 'profile/claims.j2', context) 


def logout(request):
    # clear the django session information

    try:
        del request.session[request.idp]
    except KeyError:
        pass

    # redirect the user to logout of the IdP

    redirect_to_regapp = (
        request.META['HTTP_X_FORWARDED_PROTO'] +
        "://" +
        request.META['HTTP_X_FORWARDED_HOST'] +
        reverse(index)
    )

    redirect_to_keycloak = (
        settings.NERC_LOGOUT_URL +
        "?" +
        urlencode({'redirect_uri': redirect_to_regapp})
    )

    redirect_to_oauth2_proxy = (
        settings.OAUTH2PROXY_NERC_LOGOUT_URL +
        "?" +
        urlencode({'rd': redirect_to_keycloak})
    )

    return redirect(redirect_to_oauth2_proxy)
