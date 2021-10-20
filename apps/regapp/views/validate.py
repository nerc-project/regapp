"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import requests
from django.shortcuts import render
from django.conf import settings
from .utils import get_user_confirmation
from ..models import AccountAction
import logging

logger = logging.getLogger(__name__)


def validate(request):
    regcode = request.GET.get('regcode', None)

    data = {}
    if regcode is None:
        logmsg = "No regcode supplied. Cannot complete registration."
        logger.warn(logmsg)
        data["error"] = logmsg
    else:
        try:
            pending_account_action = AccountAction.objects.get(
                regcode=regcode
            )
        except AccountAction.DoesNotExist:
            logmsg = f"Unrecognized registration code {regcode}"
            logger.warn(logmsg)
            data["error"] = logmsg
            pending_account_action = None

        if pending_account_action is not None:
            opcode = pending_account_action.opcode

            api_endpoint = (
                f"{settings.MSS_KC_SERVER}/auth/admin/realms/"
                f"{settings.MSS_KC_REALM}/users"
            )

            headers = {
                'Authorization': f"Bearer {request.client_token}",
                'Content-Type': 'application/json'
            }

            data["firstName"] = pending_account_action.firstName
            data["lastName"] = pending_account_action.lastName
            data["email"] = pending_account_action.email
            data["username"] = pending_account_action.username
            data["emailVerified"] = True
            data["enabled"] = True

            # UPDATE (EMAIL CHANGED)
            # Update email was accepted
            # convert to a normal pending update
            # and validate with user at new address
            if opcode == 'update_verify_new_email':
                logger.debug(
                    f"User {pending_account_action.username} accepted email "
                    f"change to {pending_account_action.email}. Proceding to "
                    "verify new address."
                )
                http_verb = None
                pending_account_action.opcode = 'update'
                pending_account_action.save()

                get_user_confirmation(
                    pending_account_action,
                    pending_account_action.email
                )

            # UPDATE (NO EMAIL CHANGE)
            elif opcode == 'update':
                http_verb = 'PUT'
                if pending_account_action.sub != "":
                    api_endpoint = (
                        f"{api_endpoint}/{pending_account_action.sub}"
                    )
                else:
                    logmsg = "Update action must specify a subject"
                    logger.error(logmsg)
                    raise RuntimeError(logmsg)

            # CREATE
            else:
                http_verb = 'POST'
                idp_link = {
                    'identityProvider': 'cilogon',
                    'userId': pending_account_action.linked_sub,
                    'userName': pending_account_action.username
                }
                data['federatedIdentities'] = [idp_link]
                data['attributes'] = {
                    'cilogon_idp_name': pending_account_action.linked_idp_name
                }

            # MAKE CHAGES IF CREATE OR UPDATE (NO EMAIL CHANGE)
            # Email change cause additional validation email...
            if http_verb is not None:
                try:
                    r = requests.request(
                        http_verb,
                        api_endpoint,
                        json=data,
                        headers=headers
                    )

                    if r.ok:
                        logger.info(
                            f"Acocunt {opcode} completed successfully for "
                            f"subject {pending_account_action.sub}."
                        )
                        pending_account_action.delete()

                    else:
                        server_error = r.json()['errorMessage']
                        logger.error(
                            f"Error in account {opcode} for sub "
                            f"{pending_account_action.sub}. server returned "
                            f"{server_error}."
                        )
                        data['error'] = server_error

                except requests.exceptions.RequestException as re:
                    logmsg = (
                        f"Error with account {opcode} for "
                        f"{pending_account_action.sub} A problem occurred "
                        f"communicating with the server. {re}"
                    )
                    logger.debug(logmsg)
                    data['error'] = logmsg

                except requests.exceptions.JSONDecodeError as decode_error:
                    logger.debug(
                        f"Error decoding server response. {decode_error}"
                    )
                    data['error'] = "Unknown error."

                except Exception:
                    logger.error(
                        f"An unknown error occurred while performing "
                        f"account {opcode} for sub "
                        f"{pending_account_action.sub}"
                    )
                    data['error'] = "Unknown error."

            # Have to set after sending request because server
            # does not recognize option "opcode"
            data['opcode'] = opcode

    return render(
        request,
        template_name='regapp/validate.j2',
        context={'account_action': data}
    )
