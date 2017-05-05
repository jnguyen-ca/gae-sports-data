# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

app = Blueprint('frontpage', __name__)

@app.route('/')
def frontpage():
    return render_template('frontpage.html', sports=['NHL'])
