import requests
from secrets import token_urlsafe
from smtplib import SMTPException
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from ..models import AccountAction


def validate(request):
    regcode = request.GET.get('regcode', None)

    data = {}
    if regcode is None:
        data["error"] = "No regcode supplied. Cannot complete registration."
    else:
        try:
            pending_account_action = AccountAction.objects.get(
                regcode=regcode
            )
        except AccountAction.DoesNotExist:
            data["error"] = f"Unrecognized registration code {regcode}"
            pending_account_action = None

        if pending_account_action is not None:
            opcode = pending_account_action.opcode

            api_endpoint = (
                f"{settings.NERC_KC_SERVER}/auth/admin/realms/"
                f"{settings.NERC_KC_REALM}/users"
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
                http_verb = None
                regcode = token_urlsafe(16)
                pending_account_action.regcode = regcode
                pending_account_action.opcode = 'update'
                pending_account_action.save()
                # TODO: DRY this out, profile.views.sendupdate
                update_tmpl = get_template(
                    "regapp/account_update_email.j2"
                )
                msg = update_tmpl.render({
                    "pending_account_action": pending_account_action,
                    "regcode": regcode,
                })

                try:
                    send_mail(
                        "NERC Account Update Validation",
                        msg,
                        "support@nerc.mghpcc.org",
                        [pending_account_action.email],
                        fail_silently=False
                    )
                except SMTPException as smtp_error:
                    # TODO: Log error and redirect user some place
                    # where they can try again and/or contact support.
                    raise smtp_error

            # UPDATE (NO EMAIL CHANGE)
            elif opcode == 'update':
                http_verb = 'PUT'
                if pending_account_action.sub != "":
                    api_endpoint = (
                        f"{api_endpoint}/{pending_account_action.sub}"
                    )
                else:
                    raise RuntimeError("Update action must specify a subject")

            # CREATE
            else:
                http_verb = 'POST'
                idp_link = {
                    'identityProvider': 'cilogon',
                    'userId': pending_account_action.linked_sub,
                    'userName': pending_account_action.username
                }
                data['federatedIdentities'] = [idp_link]

            # MAKE CHAGES IF CREATE OR UPDATE (NO EMAIL CHANGE)
            # Email change cause additional validation email...
            if http_verb is not None:
                # TODO FIXME - get cert to validate!!
                r = requests.request(
                    http_verb,
                    api_endpoint,
                    json=data,
                    headers=headers,
                    verify=False
                )

                if r.ok:
                    pending_account_action.delete()
                    # Clear cached nerc user info so that
                    # next request fetches from keycloak
                    if opcode == 'update' and 'nerc' in request.session:
                        del request.session['nerc']

                else:
                    try:
                        data['error'] = r.json()['errorMessage']
                    except Exception:
                        data['error'] = "Unknown error."

            # Have to set after sending request because server
            # does not recognize option "opcode"
            data['opcode'] = opcode

    return render(
        request,
        template_name='regapp/validate.j2',
        context={'account_action': data}
    )
