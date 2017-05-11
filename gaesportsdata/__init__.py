# -*- coding: utf-8 -*-

from flask import Flask
from werkzeug.debug import DebuggedApplication
import os

app = Flask(__name__)

if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    app.config.update(
                      DEBUG = True,
                      )
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

import routing
import filters