"""
Author: Jim Culbert
Copyright (c) 2022 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from regapp.config.env import ENV


def get_regapp_terms():
    # Fetch the content and whatever meta comes from TLOC
    return "You better not shout!"


TERMS_VER = ENV.get_value('TERMS_VERSION', default="v1.0")
TERMS_LOC = ENV.get_value('TERMS_LOCATION', default=f"https://nerc.mghpcc.org/terms/regapp_statement/{TERMS_VER}")
TERMS_NAME = "NERC Privacy Statement"
TERMS_CONTENT = get_regapp_terms()
