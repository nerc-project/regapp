"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import requests
from urllib.parse import urlencode
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.urls import reverse

from .utils import get_user_confirmation
from ..forms import ConfirmTermsForm, CreateAccountForm
from ..models import AccountAction
from ..regapp_utils import get_accepted_version, accepted_terms_json
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
    accepted_ver = get_accepted_version(request)
    mss_uinfo = request.oidc_userinfo

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
                accepted_terms_version = (
                    cleaned['accept_privacy_statement_version']
                )
            else:
                accepted_terms_version = None

            pending_update = AccountAction(
                regcode="",
                sub=mss_uinfo['sub'],
                firstName=cleaned['first_name'],
                lastName=cleaned['last_name'],
                email=cleaned['email'],
                username=cleaned['username'],
                research_domain=cleaned['research_domain'],
                accepted_terms_version=accepted_terms_version
            )

            pending_update.save()
        else:
            logger.debug(
                "Errors in profile update form submission. "
                f"{form.errors}"
            )

        return redirect('profile_sendupdate')

    else:

        account_form = CreateAccountForm(data)

        account_form.fields['username'].widget.attrs['readonly'] = True

        return render(request, 'profile/index.j2', {
            'form': account_form,
            'terms': {
                'title': settings.TERMS_NAME,
                'version': settings.TERMS_VER,
                'content': settings.TERMS_CONTENT
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


@never_cache
def terms(request):

    # Signals update as oppsed to get. For redirect survival.
    if 'accept_privacy_statement_version' in request.GET:
        form = ConfirmTermsForm(request.GET)

        if form.is_valid():
            sub = request.oidc_userinfo['sub']

            api_endpoint = (
                f"{settings.MSS_KC_SERVER}/admin/realms/"
                f"{settings.MSS_KC_REALM}/users/{sub}"
            )

            headers = {
                'Authorization': f"Bearer {request.client_token}",
                'Content-Type': 'application/json'
            }

            r = requests.request(
                'GET',
                api_endpoint,
                headers=headers
            )

            user_data = r.json()
            if not user_data.get('attributes', None):
                user_data['attributes'] = {}

            user_data['attributes']['accepted_terms'] = accepted_terms_json(
                form.cleaned_data['accept_privacy_statement_version'],
                request.META['HTTP_X_REAL_IP']
            )

            r = requests.request(
                'PUT',
                api_endpoint,
                json=user_data,
                headers=headers
            )

            # Redirect to oauth2-proxy logout to clear
            # session cookie with return here. This
            # should auto login and renew the
            # id_token. Need to do this otherwise change
            # will not show to the user (i.e. will get
            # prompted again to agree to tsandcs)
            target = (
                f"{settings.OAUTH2PROXY_MSS_LOGOUT_URL}?"
                f"{urlencode({'rd': reverse('profile_terms')})}"
            )
            return redirect(target)
        else:
            # Not sure how here - form posted but not valid
            # TODO: better exception or review if we can get
            # here at all
            raise Exception("form not valid??")
    else:
        accepted_ver = get_accepted_version(request)

    if accepted_ver != settings.TERMS_VER:
        form = ConfirmTermsForm()
        messages.warning(
            request,
            (
                "MSS Terms have changed. "
                "Please review and agree to the new terms"
            )
        )
    else:
        form = None

    context = {
        'terms_name': settings.TERMS_NAME,
        'terms_version': settings.TERMS_VER,
        'terms_content': settings.TERMS_CONTENT,
        'form': form
    }
    return render(request, 'profile/terms.j2', context)


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
