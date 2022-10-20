"""
Author: Jim Culbert
Copyright (c) 2022 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from requests.auth import HTTPBasicAuth
import requests
from django.conf import settings
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def get_client_token():
    client_token = None
    token_url = (
        f"{settings.MSS_KC_SERVER}/auth/realms/"
        f"{settings.MSS_KC_REALM}/protocol/openid-connect/token"
    )

    try:
        r = requests.post(
            token_url,
            data={'grant_type': 'client_credentials'},
            auth=HTTPBasicAuth(
                settings.MSS_KC_CLIENT_ID,
                settings.MSS_KC_CLIENT_SECRET
            )
        )

        token_response = r.json()
        client_token = token_response.get('access_token', None)

    except requests.exceptions.RequestException as re:
        logger.error(
            "An error occurred communicating with the server "
            f"while trying to get the client_token. Error: {re}"
        )

    except requests.exceptions.JSONDecodeError as decode_error:
        logger.debug(
            "An error occurred decoding the client token "
            f" returned by the server. Error: {decode_error}"
        )

    return client_token


def get_accepted_version(request):
    mss_uinfo = request.oidc_userinfo
    accepted_terms_json = mss_uinfo.get('accepted_terms', None)
    accepted_ver = None
    if accepted_terms_json:
        accepted_terms = json.loads(accepted_terms_json)
        accepted_ver = accepted_terms.get('ver', None)
    return accepted_ver


def accepted_terms_json(ver, ip="unknown"):
    accepted_terms = {
        "ver": ver,
        "date": datetime.now(timezone.utc).isoformat(),
        "ip": ip
    }

    return json.dumps(accepted_terms)
