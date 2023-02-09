"""
Author: Jim Culbert
Copyright (c) 2022 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from regapp.config.env import ENV
import requests
import markdown
import logging

logger = logging.getLogger(__name__)

TERMS_VER = ENV.get_value('REGAPP_TERMS_VERSION', default="v1.0.1")
TERMS_LOC = ENV.get_value('REGAPP_TERMS_LOCATION', default=f"https://raw.githubusercontent.com/nerc-project/nerc-eulas/{TERMS_VER}/EULA.md")
TERMS_NAME = ENV.get_value('REGAPP_TERMS_NAME', default="NERC Privacy Statement")
DEFAULT_TERMS_GRACE_DAYS = ENV.int('REGAPP_DEFAULT_TERMS_GRACE_DAYS', default=90)


def get_regapp_terms():
    # Fetch the content from TLOC
    try:
        r = requests.get(
            TERMS_LOC,
        )
        terms = markdown.markdown(r.text)
    except requests.exceptions.RequestException as re:
        logger.error(f"Error fetching userinfo in requests.get. {re}")
        terms = f"Unable to retrieve terms version {TERMS_VER} from {TERMS_LOC}"

    return terms


TERMS_CONTENT = get_regapp_terms()
