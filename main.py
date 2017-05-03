#usr/bin/python
# -*- coding: utf-8 -*-
import logging

from flask import Flask
from gaesportsdata import frontpage

app = Flask(__name__)
app.register_blueprint(frontpage.app)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500