import os

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
        'redirect_uri': os.environ["OIDCRedirectURI"],
        'get_messages': messages.get_messages,
        'DEFAULT_MESSAGE_LEVELS': DEFAULT_LEVELS,
    })
    return env
