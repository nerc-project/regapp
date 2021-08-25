import json
from django.conf import settings


class OIDCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        access_token = request.META.get('HTTP_X_AUTH_REQUEST_ACCESS_TOKEN', None)
        idp = request.META.get('HTTP_X_AUTH_IDP', None)

        if access_token and idp:
            if idp == "nerc":
                userinfo = {
                    'name': "Jim Nercman",
                    'email': 'test@google.com',
                }
            elif idp == "cilogon":
                userinfo = {
                    'name': "Jim Logon",
                    'email': "culbertj@mghpcc.org"
                }

        if "name" in userinfo:
            display_username = userinfo['name']
        elif all(attr in userinfo for attr in ['family_name', 'given_name']):
            display_username = (
                f'{userinfo["given_name"]} '
                f'{userinfo["family_name"]}'
            )
        else:
            display_username = userinfo.get(
                'preferred_username',
                'unknown user'
            )

        userinfo['display_username'] = display_username

        request.oidc_userinfo = userinfo

        response = self.get_response(request)

        print(response)

        return response
