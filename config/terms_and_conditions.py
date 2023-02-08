"""
Author: Jim Culbert
Copyright (c) 2022 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from regapp.config.env import ENV
import requests
import logging

logger = logging.getLogger(__name__)

TERMS_VER = ENV.get_value('REGAPP_TERMS_VERSION', default="v1.0.1")
TERMS_LOC = ENV.get_value('REGAPP_TERMS_LOCATION', default=f"https://api.github.com/repos/nerc-project/nerc-eulas/contents/regapp_terms.md?ref={TERMS_VER}")
TERMS_NAME = ENV.get_value('REGAPP_TERMS_NAME', default="NERC Privacy Statement")
DEFAULT_TERMS_GRACE_DAYS = ENV.int('REGAPP_DEFAULT_TERMS_GRACE_DAYS', default=90)


def get_regapp_terms():
    # Fetch the content from TLOC
    headers = {
        'Accept': "application/vnd.github.VERSION.html"
    }
    try:
        r = requests.get(
            TERMS_LOC,
            headers=headers
        )
        terms = r.text
    except requests.exceptions.RequestException as re:
        logger.error(f"Error fetching userinfo in requests.get. {re}")
        terms = f"Unable to retrieve terms version {TERMS_VER} from {TERMS_LOC}"

    return terms


TERMS_CONTENT = get_regapp_terms()
