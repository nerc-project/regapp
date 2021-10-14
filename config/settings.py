"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from split_settings.tools import optional, include
from regapp.config.env import ENV, PROJECT_ROOT
from environ import Path

# Regapp split settings
mss_configs = [
    'base.py',
    'database.py',
    'auth.py',
    'logging.py',
    # 'core.py',
]

# Local settings overrides
local_configs = [
    # Local settings relative to regapp.config package
    'local_settings.py',

    # System wide settings for production deployments
    '/etc/mss/local_settings.py',

    # Local settings relative to regapp project root
    PROJECT_ROOT('local_settings.py')
]

if ENV.str('REGAPP_CONFIG', default='') != '':
    # Local settings from path specified via environment variable
    local_configs.append(Path(ENV.str('REGAPP_CONFIG'))())

for lc in local_configs:
    mss_configs.append(optional(lc))

include(*mss_configs)
