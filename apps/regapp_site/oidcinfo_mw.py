import json
from django.conf import settings


class OIDCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        userinfo_str = request.META.get('HTTP_OIDC_USERINFO_JSON', "{}")
        userinfo = json.loads(userinfo_str)

        userinfo['storageportal_roles'] = userinfo.get(
            f'{settings.PORTAL_CLIENT_NAME}_roles', []
        )

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
        request.oidc_client = request.META.get('HTTP_OIDC_CLIENT', "")

        response = self.get_response(request)

        print(response)

        return response
