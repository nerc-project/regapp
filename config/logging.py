"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.contrib.messages import constants as messages
from regapp.config.env import ENV


# ------------------------------------------------------------------------------
# ColdFront logging config
# ------------------------------------------------------------------------------

MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'regapp_formatter': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-20s %(levelname)-8s  %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'regapp_formatter',
        },
    },
    'loggers': {
        'regapp': {
            'handlers': ['console'],
            'level': ENV.str('REGAPP_REGAPP_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': ENV.str('REGAPP_DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}
