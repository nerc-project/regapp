"""
Author: Jim Culbert
Copyright (c) 2022 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from datetime import datetime, timezone, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core import mail
from django.template.loader import render_to_string
import json
import logging
import requests
from ...regapp_utils import get_client_token
from ...models import UserNotification

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    API_ENDPOINT_USERS = (
        f"{settings.MSS_KC_SERVER}/admin/realms/"
        f"{settings.MSS_KC_REALM}/users"
    )
    help = 'MGHPCC-SS terms maintenance utility'

    def add_arguments(self, parser):
        parser.add_argument(
            '-r', '--report',
            action='store_true',
            help="Generate report only. Do not email users."
        )

        parser.add_argument(
            '-g', '--grace',
            nargs='?',
            default=settings.DEFAULT_TERMS_GRACE_DAYS,
            metavar='DAYS',
            type=int,
            help="Grace period in days before user is notified again."
        )

    def handle(self, *args, **options):

        all_keycloak_users = []
        target_keycloak_users = {}

        if options['verbosity'] > 0:
            self.stdout.write("Starting MGHPCC-SS terms maintenance utility.")

        client_token = get_client_token()
        if not client_token:
            msg = "Unable to retrieve client token, aborting."
            logger.error(msg)
            self.stdout.write(msg)
            return

        #
        # ***Fetch all keycloak users***
        #
        try:
            r = requests.get(
                Command.API_ENDPOINT_USERS,
                headers={'Authorization': f"Bearer {client_token}"}
            )

            if r.ok:
                all_keycloak_users = r.json()
            else:
                server_error = r.json()['errorMessage']
                logger.error(
                    f"Error fetching keycloak users."
                    f"Server returned {server_error}."
                )

        except requests.exceptions.RequestException as re:
            logger.error(
                "An error occurred communicating with the server "
                f"while trying to get the client_token. Error: {re}"
            )
        except requests.exceptions.JSONDecodeError as decode_error:
            logger.debug(f"Error decoding server response. {decode_error}")

        #
        # ***Collect users who have not agreed to the latest terms***
        #

        # Build dict of users to target
        for u in all_keycloak_users:
            try:
                accepted_terms_json = u['attributes']['accepted_terms'][0]
                accepted_terms = json.loads(accepted_terms_json)
                accepted_version = accepted_terms['ver']
            except Exception:
                accepted_version = None

            if accepted_version != settings.TERMS_VER:
                # 'remember' the accepted version for convenience
                u['accepted_version'] = accepted_version
                target_keycloak_users[u['id']] = u

        #
        # ***Filter out users with valid outstanding notifications***
        #

        # Notification is considered "valid outstanding" if it
        # was issued recently (i.e. within some grace period)
        utcnow = datetime.now(timezone.utc)
        gracedelta = timedelta(days=options['grace'])
        earliest_notification_date = utcnow - gracedelta

        # All terms notifications
        terms_notifications = UserNotification.objects.filter(
            notification_type='terms'
        )
        # All terms notifications within grace
        within_grace = terms_notifications.filter(
            notification_date__gt=earliest_notification_date
        )
        # All terms notifications within grace pertaining to target
        # users
        outstanding_user_notifications = within_grace.filter(
            sub__in=target_keycloak_users
        )

        # Remove users with valid outstanding notifications
        # from target dict
        for n in outstanding_user_notifications:
            target_keycloak_users.pop(n.sub)

        #
        # ***Main Processing Section***
        #
        if options['report']:
            for u in target_keycloak_users.values():
                line = (
                    f"{u['id']},{u['username']},"
                    f"{u['firstName']},{u['lastName']},"
                    f"{u['email']},"
                    f"{u['accepted_version']},{settings.TERMS_VER}"
                )
                self.stdout.write(line)
        else:
            failed_sends = []
            succeeded_sends = []
            with mail.get_connection() as connection:
                for u in target_keycloak_users.values():
                    # Create email message for user
                    ctx = {
                        'terms_name': settings.TERMS_NAME,
                        'previous_version': u['accepted_version'],
                        'current_version': settings.TERMS_VER,
                    }
                    msg = render_to_string(
                        'profile/terms_update_email.j2',
                        ctx
                    )
                    subject = "MGHPCC-SS Terms and Conditions Update"
                    success = mail.EmailMessage(
                        subject,
                        msg,
                        settings.EMAIL_MSS_SUPPORT,
                        [u['email']],
                        connection=connection,
                    ).send(fail_silently=True)

                    if success:
                        outstanding_notification = UserNotification(
                            sub=u['id'],
                            firstName=u['firstName'],
                            lastName=u['lastName'],
                            email=u['email'],
                            username=u['username'],
                            notification_date=datetime.now(tz=timezone.utc),
                            notification_type="terms",
                            notification_data={
                                "accepted_version": u['accepted_version'],
                                "required_version": settings.TERMS_VER
                            }
                        )
                        outstanding_notification.save()

                        msg = (
                            "Sent terms and conditions update notification "
                            f"to {u['email']}. Current accepted version "
                            f"{u['accepted_version']}, required version "
                            f"{settings.TERMS_VER}"
                        )
                        logger.info(msg)
                        succeeded_sends.append(msg)
                    else:
                        msg = (
                            "Failed to send notificaiton message to "
                            f"{u['email']}. Current accepted version "
                            f"{u['accepted_version']}, required version "
                            f"{settings.TERMS_VER}"
                        )
                        logger.error(msg)
                        failed_sends.append(msg)

            if options['verbosity'] > 0:
                for failed in failed_sends:
                    self.stderr.write(failed)

                for succeeded in succeeded_sends:
                    self.stdout.write(succeeded)

        if options['verbosity'] > 0:
            self.stdout.write("DONE")
