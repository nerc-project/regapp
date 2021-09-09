from regapp.config.env import ENV
import json

# from regapp.config.base import INSTALLED_APPS, AUTHENTICATION_BACKENDS,
# TEMPLATES

# ------------------------------------------------------------------------------
# Regapp default authentication settings
# ------------------------------------------------------------------------------
# AUTHENTICATION_BACKENDS += [
#     'django.contrib.auth.backends.ModelBackend',
# ]

LOGIN_URL = '/user/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = ENV.str('LOGOUT_REDIRECT_URL', LOGIN_URL)

# keycloak
PORTAL_CLIENT_NAME = ENV.str('REGAPP_CLIENT_NAME', 'nercra_regapp')

kckeys_linux = {
    # RS256 RSA Signing pubkey
    'xRVALOo7ct1D2kQMX0mK2EJ6U8E9f37kW0ANwWIwZ8k': {
        'key': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAn56RAOlnkBk0LK1QBUbJT2D2GBN7r+VQakwiHVBoDB9W7fdIvFNzBeMg9m9vAglVmEuvuiWr2v3Q761wFh3K5npJMC+Q76qDPb9Xog7Y62hbUnAIU6+5evUTesojAJRLEDHlFRZKMWQDTj/w/w3oG6LMmkwTs0CP7/Ewii1a4LJjuQz+izXttf1dN5Vg6B7TMJjajR3iplL2ERhWaefGLpWiAM1olmKdyqRIBRvh4m2wYk/sAmzCmcCgFdPCIw08vaApTWtQHzBx/8sCrvPXHtlsy5YVQ7SMSLnkx+j/H6BUBbWVcW4TBv7H3vqvnumU8jh/LaJnyoXYzvRqwAu9CwIDAQAB',  # noqa: E501
        'alg': 'RS256'
    },
    # RS256 RSA Encryption pubkey
    'Ef5GW4U_bCxDotVkLj7yT5kCure7dsYc2cxSIHB1pDM': {
        'key': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoRFLwI3wc15mNl+W/z7KVBGhkTDXsWr1QfTaXttSXlxjqfhomXjGJuOlnyAY/OskUtfDfsQqJ0YGAqMnZO4Zumu5UD5xhmMvTZ9id7L+tN/trQwxCj++67OcjA57aQLWh09J/4eM9JRai8rBWN3xDFp1QHW3K/XxzLFnVeWVP7/sHPqLEA7qBtYfw7+zp1MBjFE+L+9jz6s9F6NI+nBFx/ZH1tjNlrF9FItJdBtrnsMDNuL3wCB4w1miXFQjq7xGz8hHElDnRgKT3WESjm4+0HLalXpve2tFvJuDHnbT3UKeEzAmoVkWYjLwk5mvgDQml/tHpTd666FY8yE3Jijz+QIDAQAB',  # noqa: E501
        'alg': 'RS256'
    }
}

kckeys_mac = {
    # RS256 RSA Signing pubkey
    'VcIRBNwOYBN3i12iRjzp0dJrcV2thkWj7nFDk8mZvUU': {
        'key': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArbpw0OGySxC/TiNiN7hXONLvRRpX2ocJCEnPnzAxfJRdYBZx+3AlcDmMaSttMXBVcS7QuL5Rn0MBQfNcH4lWeG1cIU6nHYSunwJooatVU5iFiSIWGpBjpql0kI2pnfWUGoRahjsyPTDiFaP4qy6NKFG8x8/iZFqwcjLTHbNZUl+lc9jo6U4Wn2DetOGbOh6B1z05khiA+qfu/zKRM6N+1CAEg2quzs43qNsaMfDmnQKIf7rpUyEIgB1f+/Ncob1eaIhtr38mPSC2ymTNRs4Jd00JBkeIiwoY2/3iT3Xh9qmCRFftS9EdjWoKtIuusWfmWeTu++l8VfSYIi6SWljxwQIDAQAB',  # noqa: E501
        'alg': 'RS256'
    },
    # RS256 RSA Encryption pubkey
    'X9vG7wWV1dEgAy8Ovx7WqP3EJ4IhilQ-mL0iV-bewa0': {
        'key': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAibSyC1W1pt8trTsALV0wtvLeLqsdqesR4miF3uF9bsj6Bq2GSSKLpKJ3Ebopo7MDrkRVhLa3MNRfe6JQNk3VBzvNWRyQpPI9no/M8OHyVv1CZyTPZwNVOwvCDKUdtvTlMK/7tB928Ae96ebGB5XJc5M3M0Y+NYWS9sWvI8IEUmx8QNae4egdkHL+rFvWKEjJkmyS2GCckAPoOw+cmY+W6YOax3T9/PtzrmbzI4aXYHSL8R0mPGKxZ4KQO9G2dr4U/aCRdRlgAvWRl8OS4fOaEbMX49w1upvmxd+X4hFU3P9WiZFqiZgUIsQj/B2NQnk2puFfs2qGy5b4+QV+0/b8sQIDAQAB',  # noqa: E501
        'alg': 'RS256'
    }
}

kckeys = kckeys_linux
KEYCLOAK_KEYS_JSON = ENV.str('REGAPP_KEYCLOAK_KEYS_JSON', json.dumps(kckeys))

NERC_KC_SERVER = ENV.str(
    'REGAPP_NERC_KC_SERVER',
    'https://keycloak.nerc.mghpcc.org'
)

NERC_KC_REALM = ENV.str(
    'REGAPP_NERC_KC_REALM',
    'nerc'
)

NERC_KC_CLIENT = ENV.str('REGAPP_NERCKC_CLIENT', 'regapp')

# NERC_KC_CLIENT_SECRET = ENV.str('','')

NERC_LOGOUT_URL = ENV.str(
    'REGAPP_NERC_LOGOUT_URL',
    (
        f"{NERC_KC_SERVER}/auth/realms/"
        f"{NERC_KC_REALM}/protocol/openid-connect/logout"
    )
)

CILOGON_LOGOUT_URL = ENV.str(
    'REGAPP_CILOGON_LOGOUT_URL',
    "https://cilogon.org/logout"
)

OAUTH2PROXY_NERC_LOGOUT_URL = ENV.str(
    'REGAPP_OAUTH2PROXY_NERC_LOGOUT_URL',
    "/oauth2kc/sign_out"
)

OAUTH2PROXY_CILOGON_LOGOUT_URL = ENV.str(
    'REGAPP_OAUTH2PROXY_CILOGON_LOGOUT_URL',
    "/oauth2cilogon/sign_out"
)

SESSION_COOKIE_AGE = 60 * 15
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = True

# ------------------------------------------------------------------------------
# Enable administrators to login as other users
# ------------------------------------------------------------------------------
# if ENV.bool('ENABLE_SU', default=True):
#     AUTHENTICATION_BACKENDS += ['django_su.backends.SuBackend',]
#     INSTALLED_APPS.insert(0, 'django_su')
#     TEMPLATES[0]['OPTIONS']['context_processors'] \
#       .extend(['django_su.context_processors.is_su', ])
