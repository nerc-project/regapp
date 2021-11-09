"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.http import urlencode
from .utils import get_user_confirmation
from ..models import AccountAction
import logging

logger = logging.getLogger(__name__)


@never_cache
def validate(request):
    regcode = request.GET.get('regcode', None)

    data = {
        "attributes": {}
    }
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
            data["attributes"]['mss_research_domain'] = (
                pending_account_action.research_domain
            )
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

                # This method fires off an email to the user
                # to confirm the pending action.
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

            # UPDATE (DISPLAY AFTER SESSION DISCARD)
            elif opcode == 'update_display_only':
                http_verb = None
                data["research_domain_name"] = (
                    pending_account_action.research_domain_name
                )
                # Can discard this now (deferred from update...)
                pending_account_action.delete()

            # CREATE
            else:
                http_verb = 'POST'
                idp_link = {
                    'identityProvider': 'cilogon',
                    'userId': pending_account_action.linked_sub,
                    'userName': pending_account_action.username
                }
                data['federatedIdentities'] = [idp_link]
                data['attributes']["cilogon_idp_name"] = (
                    pending_account_action.linked_idp_name
                )

            # MAKE CHAGES IF CREATE OR UPDATE (NO EMAIL CHANGE)
            # Email change cause additional validation email...
            if http_verb is not None:
                try:

                    if http_verb == 'PUT':
                        # Keycloak API does not merge user attributes but
                        # replace on PUT so, to update attribute,
                        # (e.g. mss-research_domain) we need to get the
                        # existing full list, merge the changed attribute
                        # then provide the full list back on the PUT
                        r = requests.request(
                            'GET',
                            api_endpoint,
                            headers=headers
                        )

                        if r.ok:
                            logger.info(
                                f"Account info prefetch successful for "
                                f"subject {pending_account_action.sub}."
                            )
                            # These are the existing user attrs
                            user_attributes = r.json().get('attributes', None)

                            # Merge changes and existing
                            if user_attributes is not None:
                                user_attributes.update(data['attributes'])
                                data['attributes'] = user_attributes

                        else:
                            server_error = r.json()['errorMessage']
                            logger.error(
                                f"Error in account {opcode} for sub "
                                f"{pending_account_action.sub}. "
                                f"server returned {server_error} while "
                                f"pre-fetching user info."
                            )
                            data['error'] = server_error

                            # TODO: Do something more informative here?
                            raise Exception(server_error)

                    r = requests.request(
                        http_verb,
                        api_endpoint,
                        json=data,
                        headers=headers
                    )

                    # If we are here, we have successfully created or updated
                    # the account
                    if r.ok:
                        logger.info(
                            f"Acocunt {opcode} completed successfully for "
                            f"subject {pending_account_action.sub}."
                        )

                        # TODO: This is a little too tied to knowing
                        # oauth2proxy internals. Signout url should
                        # come from config...

                        # If this is an update, we need to clear the session
                        # cookie held by oauth2proxy as info token is now
                        # out of date
                        if pending_account_action.opcode == 'update':
                            pending_account_action.opcode = 'update_display_only'
                            pending_account_action.save()
                            rd_param = urlencode(
                                {
                                    "rd": request.get_full_path_info()
                                }
                            )
                            return redirect(
                                f"{settings.OAUTH2PROXY_MSS_LOGOUT_URL}?"
                                f"{rd_param}"
                            )
                        else:
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
                        f"An error occurred while performing "
                        f"account {opcode} for sub "
                        f"{pending_account_action.sub}"
                    )
                    data['error'] = "Unknown error."

            # Have to set after sending request because server
            # does not recognize option "opcode" or "research_domain_name"
            data['opcode'] = opcode
            data["research_domain_name"] = (
                pending_account_action.research_domain_name
            )

    return render(
        request,
        template_name='regapp/validate.j2',
        context={'account_action': data}
    )
