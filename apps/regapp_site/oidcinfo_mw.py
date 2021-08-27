import base64
import hashlib
import json
import requests
import jwt
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class OIDCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        idp = request.META.get('HTTP_X_AUTH_IDP', None)
        if idp:
            request.idp = idp

            access_token = request.META.get(
                'HTTP_X_AUTH_REQUEST_ACCESS_TOKEN',
                None)

            userinfo = {}
            if idp in request.session:
                userinfo = request.session[idp]
            elif access_token:
                if idp == "nerc":
                    userinfo = fetch_nerc_userinfo(access_token)
                elif idp == "cilogon":
                    userinfo = fetch_cilogon_userinfo(access_token)
                
                request.session[idp] = userinfo

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


def fetch_nerc_userinfo(access_token):
    # NERC access tokens have userinfo in them
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

    return userinfo


def fetch_cilogon_userinfo(access_token):
    r = requests.post(
        "https://cilogon.org/oauth2/userinfo",
        data={'access_token': access_token}
    )
    userinfo = r.json()

    return userinfo
