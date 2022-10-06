"""
Author: Jim Culbert
Copyright (c) 2022 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from regapp.config.env import ENV
import requests


TERMS_VER = ENV.get_value('TERMS_VERSION', default="v1.0.1")
TERMS_LOC = ENV.get_value('TERMS_LOCATION', default=f"https://api.github.com/repos/nerc-project/nerc-eulas/contents/regapp_terms.md?ref={TERMS_VER}")
TERMS_NAME = "NERC Privacy Statement"


def get_regapp_terms():
    # Fetch the content and whatever meta comes from TLOC
    headers = {
        'Accept': "application/vnd.github.VERSION.html"
    }
    try:
        r = requests.get(
            TERMS_LOC,
            headers=headers
        )
        terms = r.text
    except requests.exceptions.RequestException:
        # NEED TO LOG THIS
        # logger.error(f"Error fetching userinfo in requests.get. {re}")
        terms = f"Unable to retrieve terms version {TERMS_VER} from {TERMS_LOC}"

    return terms


TERMS_CONTENT = get_regapp_terms()
