import os
from regapp.config.env import ENV

from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages.constants import DEFAULT_LEVELS

from jinja2 import Environment

from crispy_forms.utils import render_crispy_form


def environment(**options):
    env = Environment(**options)

    env.globals.update({
        'static': static,
        'url': reverse,
        'crispy': render_crispy_form,
        'redirect_uri': "FOOOO",
        'nerc_logout_url': ENV.str(
            'REGAPP_KEYCLOAK_LOGOUT_URL',
            "https://keycloak.nerc.mghpcc.org/auth/realms/nerc/protocol/openid-connect/logout"
        ),
        'cilogon_logout_url': ENV.str(
            'REGAPP_CILOGON_LOGOUT_URL',
            "https://cilogon.org/logout"
        ),
        'oauth2proxy_nerc_logout_url': ENV.str(
            'REGAPP_OAUTH2PROXY_NERC_LOGOUT_URL',
            "/oauth2kc/sign_out"
        ),
        'oauth2proxy_cilogon_logout_url': ENV.str(
            'REGAPP_OAUTH2PROXY_CILOGON_LOGOUT_URL',
            "/oauth2cilogon/sign_out"
        ),
        'get_messages': messages.get_messages,
        'DEFAULT_MESSAGE_LEVELS': DEFAULT_LEVELS,
    })
    return env         
