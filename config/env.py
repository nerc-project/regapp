"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

import environ

ENV = environ.Env()
PROJECT_ROOT = environ.Path(__file__) - 2

# Default paths to environment files
env_paths = [
    PROJECT_ROOT.path('.env'),
    environ.Path('/etc/mss/mss.env'),
]

if ENV.str('REGAPP_ENV', default='') != '':
    env_paths.insert(0, environ.Path(ENV.str('REGAPP_ENV')))

# Read in any environment files
for e in env_paths:
    try:
        e.file('')
        ENV.read_env(e())
    except FileNotFoundError:
        pass
