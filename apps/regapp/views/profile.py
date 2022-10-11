"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import json
from urllib.parse import urlencode
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.urls import reverse
from .utils import get_user_confirmation
from ..forms import CreateAccountForm
from ..models import AccountAction
import logging


logger = logging.getLogger(__name__)


@never_cache
def profile(request):

    """View for editing account information.

    Args:
        request: Django HttpRequest object.

    Returns:
        A Django HttpResponse object

    View to handle display and update of user profile
    information.
    """

    # Profile is protected under path that authenticates
    # via MSS IdP. Userinfo in this session is from MSS.
    mss_uinfo = request.oidc_userinfo
    accepted_terms_json = mss_uinfo['accepted_terms']
    accepted_ver = None
    if accepted_terms_json:
        accepted_terms = json.loads(accepted_terms_json)
        if accepted_terms['ver'] == settings.TERMS_VER:
            accepted_ver = accepted_terms['ver']

    data = {
        'first_name': mss_uinfo.get('given_name', None),
        'last_name': mss_uinfo.get('family_name', None),
        'username': mss_uinfo.get('preferred_username', None),
        'email': mss_uinfo.get('email', None),
        'research_domain': mss_uinfo.get('mss_research_domain', 'other'),
        'accept_privacy_statement': accepted_ver == settings.TERMS_VER,
        'accept_privacy_statement_version': settings.TERMS_VER
    }

    if request.method != 'GET':
        logger.error(
            f"Non-get method for profile page - {request.method}"
        )
        raise Http404("Profile URL does not handle HTTP POST.")

    # Signal that request was from a form submission
    # Using GET to survive oidc redirect/return pattern.
    if 'email' in request.GET:
        form = CreateAccountForm(request.GET, initial=data)

        if form.is_valid():

            # Rock beats scissors. Kill any extant update
            # for this user.
            updates_inflight = AccountAction.objects.filter(
                sub=mss_uinfo['sub']
            )
            if updates_inflight.count() > 0:
                logger.debug("Updates were inflight. Silently deleting them")
                updates_inflight.delete()

            cleaned = form.cleaned_data
            if cleaned['accept_privacy_statement']:
                accepted_terms = cleaned['accept_privacy_statement_version']
            else:
                accepted_terms = None

            pending_update = AccountAction(
                regcode="",
                sub=mss_uinfo['sub'],
                firstName=cleaned['first_name'],
                lastName=cleaned['last_name'],
                email=cleaned['email'],
                username=cleaned['username'],
                research_domain=cleaned['research_domain'],
                accepted_terms_version=accepted_terms
            )

            pending_update.save()
        else:
            logger.debug(
                "Errors in profile update form submission. "
                f"{form.errors}"
            )
            print(form.errors)

        return redirect('profile_sendupdate')

    else:

        account_form = CreateAccountForm(data)

        account_form.fields['username'].widget.attrs['readonly'] = True

        return render(request, 'profile/index.j2', {
            'form': account_form,
            'terms': {
                'title': settings.TERMS_NAME,
                'version': settings.TERMS_VER
            }
        })


@never_cache
def sendupdate(request):

    mss_uinfo = request.oidc_userinfo
    validation_email = mss_uinfo.get('email', None)

    try:
        pending_update = AccountAction.objects.get(sub=mss_uinfo['sub'])

        # Check if pending update request is changing email
        if pending_update.email != validation_email:
            logger.debug(
                f"Sub {pending_update.sub} is changing email from "
                f"{validation_email} to {pending_update.email}"
            )

            pending_update.opcode = 'update_verify_new_email'

        else:
            pending_update.opcode = 'update'

        pending_update.save()

        get_user_confirmation(pending_update, validation_email)

        ctx = {
            'validation_recipient': validation_email
        }

    except AccountAction.DoesNotExist as e:
        ctx = {
            'error': e,
            'sub': mss_uinfo['sub']
        }
        pending_update = None

    except RuntimeError as error:
        logger.error(
            "Error attempting to validate update for account "
            f"{mss_uinfo['sub']}. Exception: {error}"
        )
        ctx = {
            'error': error,
            'sub': mss_uinfo['sub']
        }
        # TODO: Redirect user some place
        # where they can try again and/or contact support.
        raise error

    return render(request, 'profile/sendupdate.j2', ctx)


def logout(request):

    # redirect the user to logout of the IdP

    redirect_to_regapp = (
        request.META['HTTP_X_FORWARDED_PROTO'] + "://" + request.META['HTTP_X_FORWARDED_HOST'] + reverse('site_index')
    )

    redirect_to_keycloak = (
        settings.MSS_LOGOUT_URL + "?" + urlencode(
            {
                'post_logout_redirect_uri': redirect_to_regapp,
                'id_token_hint': request.oidc_userinfo['idtoken']
            }
        )
    )

    redirect_to_oauth2_proxy = (settings.OAUTH2PROXY_MSS_LOGOUT_URL + "?" + urlencode({'rd': redirect_to_keycloak}))

    return redirect(redirect_to_oauth2_proxy)
