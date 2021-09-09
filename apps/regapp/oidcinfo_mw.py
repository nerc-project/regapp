import base64
import json
import requests
from requests.auth import HTTPBasicAuth
import jwt
from time import time
from django.conf import settings


class OIDCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Get or refresh the client access token
        client_token_info = request.session.get('client_token_info', None)
        if client_token_info is None or client_token_info['exp'] < time():
            token_url = (
                f"{settings.NERC_KC_SERVER}/auth/realms/"
                f"{settings.NERC_KC_REALM}/protocol/openid-connect/token"
            )

            r = requests.post(
                token_url,
                data={'grant_type': 'client_credentials'},
                auth=HTTPBasicAuth(
                    'regapp',
                    'dd7919cd-eb28-4795-81d0-8acbd38bf375'
                ),
                verify=False
            )

            token_response = r.json()
            client_token = token_response.get('access_token', None)
            # parse the jwt for expiry info
            client_token_info = fetch_nerc_userinfo_token(client_token)
            request.session['client_token_info'] = {
                'exp': client_token_info['exp'],
                'token': client_token
            }

        request.client_token = request.session['client_token_info']['token']

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
                    userinfo = fetch_nerc_userinfo(
                        access_token,
                        request.client_token
                    )
                elif idp == "cilogon":
                    userinfo = fetch_cilogon_userinfo(access_token)

                request.session[idp] = userinfo

            if "name" in userinfo:
                display_username = userinfo['name']
            elif all(
                attr in userinfo for attr in ['family_name', 'given_name']
            ):
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


def fetch_nerc_userinfo(access_token, client_token):
    token_info = fetch_nerc_userinfo_token(access_token)
    api_endpoint = (
        f"{settings.NERC_KC_SERVER}/auth/admin/realms/"
        f"{settings.NERC_KC_REALM}/users/{token_info['sub']}"
    )

    headers = {
        'Authorization': f"Bearer {client_token}",
    }

    r = requests.get(
        api_endpoint,
        headers=headers,
        verify=False
    )

    if r.ok:
        userinfo = r.json()
        # Bit of a hack to keep userinfo response same
        # as claims. Need to figure out if there is a way
        # to force token refresh in oauth2proxy
        userinfo['given_name'] = userinfo.get('firstName', "")
        userinfo['family_name'] = userinfo.get('lastName', "")
        userinfo['preferred_username'] = userinfo.get('username', "")
        userinfo['sub'] = userinfo.get('id', "")
        return userinfo
    else:
        return token_info


def fetch_nerc_userinfo_token(access_token):
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
