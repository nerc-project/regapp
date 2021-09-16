"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from regapp.apps.regapp.models import AccountAction

from datetime import timedelta


class Command(BaseCommand):
    help = 'Deletes expired registration and profile requests.'
    DEFAULT_MAX_AGE = 86400

    def add_arguments(self, parser):
        parser.add_argument(
            'max_age',
            nargs='?',
            metavar='N',
            type=int,
            help="Enter the maximum age in seconds (default: 86400 (24hrs))"
        )

    def handle(self, *args, **options):

        try:
            # Command line has highest precedence
            if options['max_age'] is not None:
                max_age = options['max_age']
            else:
                # Followed by environment var
                max_age = settings.REGAPP_REAPER_MAX_AGE
        except Exception:
            # Finally programatic default...
            max_age = Command.DEFAULT_MAX_AGE

        oldest_item = timezone.now() - timedelta(seconds=max_age)
        expired = AccountAction.objects.filter(updated_on__lte=oldest_item)
        if expired.count() > 0:
            msg = f"regreaper: Reaped {expired.count()} requests."
            expired.delete()
        else:
            msg = (
                "regreaper: No requests older than "
                f"{max_age} seconds."
            )

        self.stdout.write(msg)
