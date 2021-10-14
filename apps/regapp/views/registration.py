"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from ..forms import CreateAccountForm
from ..models import AccountAction
from urllib.parse import urlencode
from secrets import token_urlsafe
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls import reverse
import requests
import logging

logger = logging.getLogger(__name__)


def registration(request):

    # if this sub has a link then redirect user to profile route
    #
    # Else, check to see if username is taken
    # If good, then create a user with username, fn, ln and email provided
    # Add link for idp

    cilogon_uinfo = request.oidc_userinfo
    client_token = request.client_token
    existing_mss_account_info = None
    pending_registration = None

    # Sanity
    if client_token is None or 'sub' not in cilogon_uinfo:
        raise RuntimeError(
            f"Error checking for existing: client_token: {client_token} "
            f"cilogon sub: {cilogon_uinfo.get('sub', None)}"
        )

    # Check first for a pending registration for this user
    try:
        pending_registration = AccountAction.objects.get(
            linked_sub=cilogon_uinfo['sub']
        )
    except AccountAction.DoesNotExist:
        pending_registration = None

    # If no pending registration check to see
    # if a linked account already exists for this user
    if pending_registration is None:

        api_endpoint = (
            f"{settings.MSS_KC_SERVER}/auth/admin/realms/"
            f"{settings.MSS_KC_REALM}/users"
        )
        headers = {
            'Authorization': f"Bearer {client_token}"
        }
        params = {
            'idpUserId': cilogon_uinfo['sub']
        }

        try:
            r = requests.get(
                api_endpoint,
                params=params,
                headers=headers
            )

            mss_userinfo_result = r.json()

        # TODO: Do something reasonable with exceptions!
        except requests.exceptions.RequestException as re:
            logger.error(
                "An error occurred getting user info from "
                f"server. The error was: {re}"
            )
            raise re

        except requests.exceptions.JSONDecodeError as decode_error:
            logger.error(
                f"Error decoding server response. {decode_error}"
            )
            raise decode_error

        if len(mss_userinfo_result) > 0:
            existing_mss_account_info = mss_userinfo_result[0]

    # Handle existing account or registration-in-flight
    # here.
    if pending_registration is not None:
        logmsg = (
            f"Outstanding regisration for {cilogon_uinfo['sub']} "
            f"with code {pending_registration.regcode}"
        )
        logger.warn(logmsg)
        return redirect('reg_inflight')

    elif existing_mss_account_info is not None:
        uid = existing_mss_account_info['id']

        logger.info(f"An account already exists for {uid}")

        query = urlencode({'acctid': uid})
        target = f"{reverse('reg_accountexists')}?{query}"
        return redirect(target)

    # Initiate account creation
    # Handling as get to survive oidc redirection
    # TODO: Handle more sensibly...
    if request.method != "GET":
        logger.error(
            f"Non-get method for registration page - {request.method}"
        )
        raise Exception

    # Using presence of email as indicator of form
    # submission intent.
    if 'email' in request.GET:
        logger.info(f"Creating account action for sub {cilogon_uinfo['sub']}")
        form = CreateAccountForm(request.GET)
        if form.is_valid():
            # Create pending registration
            pending_registration = AccountAction(
                regcode="",
                opcode="create",
                linked_sub=cilogon_uinfo['sub'],
                linked_iss=cilogon_uinfo['iss'],
                linked_idp_name=cilogon_uinfo['idp_name'],
                firstName=form.cleaned_data['first_name'],
                lastName=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                username=form.cleaned_data['username']
            )
            pending_registration.save()

            return redirect('reg_sendvalidation')
    else:

        username = cilogon_uinfo.get('preferred_username', None)
        if username is None:
            username = cilogon_uinfo.get('eppn', None)

        form = CreateAccountForm(initial={
                'first_name': cilogon_uinfo.get('given_name', None),
                'last_name': cilogon_uinfo.get('family_name', None),
                'username': username,
                'email': cilogon_uinfo.get('email', None),
            }
        )

    return render(
        request,
        'registration/index.j2',
        {'form': form, 'user_info': cilogon_uinfo}
    )


def sendvalidation(request):
    cilogon_uinfo = request.oidc_userinfo
    ctx = {
        "error": None
    }
    try:
        pending_registration = AccountAction.objects.get(
            linked_sub=cilogon_uinfo['sub']
        )
        regcode = token_urlsafe(16)
        pending_registration.regcode = regcode
        pending_registration.save()

        create_tmpl = get_template(
            "registration/account_create_email.j2"
        )
        msg = create_tmpl.render({
            "pending_registration": pending_registration,
            "regcode": regcode
        })

        send_mail(
            "MSS Account Creation Validation",
            msg,
            "support@mss.mghpcc.org",
            [pending_registration.email],
            fail_silently=False
        )

    except AccountAction.DoesNotExist as e:
        logger.error(
            f"Attempt to send validation for sub {cilogon_uinfo['sub']} "
            "but no pending account creation exists."
        )
        ctx['error'] = e
        pending_registration = None

    except SMTPException as smtp_error:
        logger.error(
            "Error attempting to send email for account "
            f"creation for sub {cilogon_uinfo['sub']}. Exception: {smtp_error}"
        )
        ctx['error'] = smtp_error
        # TODO: Redirect user some place
        # where they can try again and/or contact support.
        raise smtp_error

    ctx['email'] = pending_registration.email

    return render(request, 'registration/sendvalidation.j2', ctx)


def inflight(request):
    pending_registration = AccountAction.objects.get(
        linked_sub=request.oidc_userinfo['sub']
    )
    return render(
        request,
        'registration/inflight.j2',
        context={'user_info': pending_registration}
    )


def accountexists(request):

    uid = request.GET.get('acctid', None)
    api_endpoint = (
        f"{settings.MSS_KC_SERVER}/auth/admin/realms/"
        f"{settings.MSS_KC_REALM}/users/{uid}"
    )
    headers = {
        'Authorization': f"Bearer {request.client_token}"
    }
    try:
        r = requests.get(
            api_endpoint,
            headers=headers
        )

        if r.ok:
            logger.debug(f"Account {uid} exists")
            userinfo_result = r.json()
        else:
            server_error = r.json()['errorMessage']
            logger.error(
                f"Error fetching account information for {uid}"
                f"Server returned {server_error}."
            )

    except requests.exceptions.RequestException as re:
        logger.debug(f"Error fetching userinfo in requests.get. {re}")

    except requests.exceptions.JSONDecodeError as decode_error:
        logger.debug(f"Error decoding server response. {decode_error}")

    return render(
        request,
        'registration/accountexists.j2',
        {'user_info': userinfo_result}
    )


def logout(request):
    # clear the django session information
    try:
        del request.session['client_token_info']
    except KeyError:
        pass

    # redirect the user to logout of the IdP

    redirect_to_regapp = (
        request.META['HTTP_X_FORWARDED_PROTO'] +
        "://" +
        request.META['HTTP_X_FORWARDED_HOST'] +
        reverse('site_index')
    )

    redirect_to_keycloak = (
        settings.CILOGON_LOGOUT_URL +
        "?" +
        urlencode({'redirect_uri': redirect_to_regapp})
    )

    redirect_to_oauth2_proxy = (
        settings.OAUTH2PROXY_CILOGON_LOGOUT_URL +
        "?" +
        urlencode({'rd': redirect_to_keycloak})
    )

    return redirect(redirect_to_oauth2_proxy)
