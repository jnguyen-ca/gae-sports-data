#usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint

app = Blueprint('frontpage', __name__)

@app.route('/')
def hello():
    return 'Hello from the frontpage.py!'