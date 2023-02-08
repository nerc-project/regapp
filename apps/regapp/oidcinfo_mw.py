"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import base64
import json
import jwt
import re
from time import time
from django.conf import settings
import logging
from .regapp_utils import get_client_token

logger = logging.getLogger(__name__)

HEADERPATTERN = re.compile(
    r'^Bearer\s+(?P<token>.*)$',
    flags=re.IGNORECASE
)


class OIDCMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ******CLIENT TOKEN******

        # Get or refresh the client access token
        client_token_info = request.session.get('client_token_info', None)
        if client_token_info is None or client_token_info['exp'] < time():
            if client_token_info is None:
                logger.debug("Client token not found in session. Fetching")
            else:
                logger.debug(
                    "Client token in session has expired. "
                    f"Expiry: {client_token_info['exp']}"
                )

            client_token = get_client_token()

            try:
                client_token_info = jwt.decode(
                    client_token,
                    options={"verify_signature": False}
                )

                request.session['client_token_info'] = {
                    'exp': client_token_info['exp'],
                    'token': client_token
                }
            except jwt.exceptions.InvalidTokenError as invalid_error:
                logger.debug(
                    "A JWT decode error occurred decoding the client token. "
                    f"Decode error: {invalid_error}"
                )

        logger.debug(
            f"Client token: {request.session.get('client_token_info', None)}"
        )
        request.client_token = request.session['client_token_info']['token']

        # **********USERINFO AND IDP**************

        try:
            # IDToken passed as bearer
            match = HEADERPATTERN.match(request.META['HTTP_AUTHORIZATION'])
            id_token = match['token']
            id_token_dict = jwt.decode(
                id_token,
                options={"verify_signature": False}
            )

            # Convenience
            if id_token_dict['iss'] == 'https://cilogon.org':
                request.idp = 'cilogon'
            else:
                request.idp = 'mss'

            # Make a nice display name
            if "name" in id_token_dict:
                display_username = id_token_dict['name']
            elif all(
                attr in id_token_dict for attr in ['family_name', 'given_name']
            ):
                display_username = (
                    f'{id_token_dict["given_name"]} '
                    f'{id_token_dict["family_name"]}'
                )
            else:
                display_username = id_token_dict.get(
                    'preferred_username',
                    'unknown user'
                )

            id_token_dict['display_username'] = display_username
            id_token_dict['idtoken'] = id_token
            request.oidc_userinfo = id_token_dict

            logger.debug(f"Decoded idp: {request.idp}")
            logger.debug(f"Decoded token: {id_token_dict}")

        except Exception as e:
            logger.debug(f"No ID token decoded. Exception: {e}")
            request.idp = None
            request.oidc_userinfo = None

        response = self.get_response(request)

        return response


def parse_jwt_validate(access_token):
    # MSS access tokens have userinfo in them
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
