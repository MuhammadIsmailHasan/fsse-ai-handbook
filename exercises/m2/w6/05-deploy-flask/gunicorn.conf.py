"""Gunicorn settings, all overridable with environment variables. See README.md.

Run:  gunicorn -c gunicorn.conf.py wsgi:app
"""

import os

bind = "127.0.0.1:8000"  # TODO
