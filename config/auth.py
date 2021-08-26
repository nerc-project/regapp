from regapp.config.env import ENV
import json
import base64
# from regapp.config.base import INSTALLED_APPS, AUTHENTICATION_BACKENDS, TEMPLATES

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

kckeys = {
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
KEYCLOAK_KEYS_JSON = ENV.str('REGAPP_KEYCLOAK_KEYS_JSON', json.dumps(kckeys))


SESSION_COOKIE_AGE = 60 * 15
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = True

#------------------------------------------------------------------------------
# Enable administrators to login as other users
#------------------------------------------------------------------------------
# if ENV.bool('ENABLE_SU', default=True):
#     AUTHENTICATION_BACKENDS += ['django_su.backends.SuBackend',]
#     INSTALLED_APPS.insert(0, 'django_su')
#     TEMPLATES[0]['OPTIONS']['context_processors'].extend(['django_su.context_processors.is_su', ])
