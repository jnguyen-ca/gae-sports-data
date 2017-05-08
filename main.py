# -*- coding: utf-8 -*-

import logging
import os

from flask import Flask

from gaesportsdata import (frontpage,
                           scraper)

app = Flask(__name__)

app.register_blueprint(frontpage.app)
app.register_blueprint(scraper.app)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# @app.errorhandler(500)
# def server_error(e):
#     # Log the error and stacktrace.
#     logging.exception('An error occurred during a request.')
#     return 'An internal error occurred.', 500