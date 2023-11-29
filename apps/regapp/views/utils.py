"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from secrets import token_urlsafe
from django.template.loader import render_to_string
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import send_mail
import logging


logger = logging.getLogger(__name__)


def get_user_confirmation(account_action, validation_email):

    """Utility function to validate account actions.

    Args:
        account_action: AccountAction object for pending action.
        validation_email: The email address where the validation
        will be sent.

    Raises:
        RuntimeError: Raised for bad arguments or smtp errors

    This utility function handles validating pending account updates.

    There are three scenarios:
        1) Account Creation
        2) Account Update
        3) Account Update with Email Update

    Email update is unique in that you need to do two validations
        1) Confirm that the update is intentional to the current
        account address.
        2) Confirm that the new address is valid.

    This utility handles code generation and email sending
    for the three scenarios.
    """

    subject = ""
    tmpl = ""
    errmsg = ""

    if account_action is None:
        errmsg = "account_action cannot be None"
        logger.error(errmsg)
        raise RuntimeError(errmsg)

    # Code used to tie registration validation responses
    # to pending AccountAction objects.
    account_action.regcode = token_urlsafe(16)
    account_action.save()

    ctx = {
        "account_action": account_action,
        "old_email": validation_email
    }

    if account_action.opcode == 'create':

        subject = "MGHPCC-SS Account Creation Validation"
        tmpl = "registration/account_create_email.j2"

    elif account_action.opcode == 'update':

        subject = "MGHPCC-SS Account Update Validation"
        tmpl = "profile/account_update.j2"

    elif account_action.opcode == 'update_verify_new_email':

        subject = "MGHPCC-SS Account Update Validation"
        tmpl = "profile/account_update_email.j2"

    else:
        # This should not happen...
        errmsg = (
            "Account action has unrecognized "
            f"opcode {account_action.opcode}"
        )
        logger.error(errmsg)
        raise RuntimeError(errmsg)

    try:
        send_mail(
            subject,
            render_to_string(tmpl, ctx),
            settings.EMAIL_MSS_SUPPORT,
            [validation_email],
            fail_silently=False
        )

    except SMTPException as smtp_error:
        errmsg = (
            "Error attempting to send email for account "
            f"validation to addr {validation_email}. "
            f"Exception: {smtp_error}"
        )
        logger.error(errmsg)
        raise RuntimeError(errmsg)
