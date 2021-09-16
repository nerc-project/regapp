"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import os
from django.core.wsgi import get_wsgi_application

"""
WSGI config for regapp project.
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'regapp.settings')

application = get_wsgi_application()
