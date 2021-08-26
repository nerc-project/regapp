import json
import base64
import requests
import jwt
from django.conf import settings


class OIDCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        access_token = request.META.get(
            'HTTP_X_AUTH_REQUEST_ACCESS_TOKEN',
            None)

        idp = request.META.get('HTTP_X_AUTH_IDP', None)

        if access_token and idp:
            # NERC access tokens have userinfo in them
            if idp == "nerc":
                padarr = ['', '===', '==', '=']
                # Get the jwt header from the keycloak access token
                parts = access_token.split(".")
                header_encoded = parts[0] + padarr[len(parts) % 4]
                header_bytes = base64.b64decode(header_encoded)
                header = json.loads(header_bytes)
                # Fetch the signing key index from the header and
                # get the associated keyinfo. Keyinfo structure is
                # {kidx: {'alg': <ALGSTR>, 'key': <PUBKEY>}}
                kidx = header['kid']
                keyinfo = json.loads(settings.KEYCLOAK_KEYS_JSON)[kidx]
                pubkey = b"".join([
                    b"-----BEGIN PUBLIC KEY-----\n",
                    str.encode(keyinfo['key']),
                    b"\n-----END PUBLIC KEY-----\n",
                ])
                userinfo = jwt.decode(
                    access_token,
                    pubkey,
                    audience=["account"],
                    algorithms=[keyinfo['alg']])
            elif idp == "cilogon":
                r = requests.post(
                    "https://cilogon.org/oauth2/userinfo",
                    data={'access_token': access_token}
                )
                userinfo = r.json()

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

        return response
