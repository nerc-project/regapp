"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import os
from django.core.asgi import get_asgi_application

"""
ASGI config for regapp project.
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'regapp.config.settings')

application = get_asgi_application()
