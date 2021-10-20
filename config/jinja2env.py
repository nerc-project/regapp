"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from regapp.config.env import ENV
from django.templatetags.static import static
from django.urls import reverse
from django.conf import settings
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
        'get_messages': messages.get_messages,
        'DEFAULT_MESSAGE_LEVELS': DEFAULT_LEVELS,
        'SITENAME': ENV.str('SITENAME'),
        'EMAIL_MSS_SUPPORT': settings.EMAIL_MSS_SUPPORT
    })

    return env
