# -*- coding: utf-8 -*-

from datetime import datetime
import flask

import models
import nhl
import logging

from . import app

@app.route('/')
def frontpage():
    # aka navigation page
    return flask.render_template('frontpage.html', sports=['NHL'])

@app.route('/scrape/<league_id>')
def scrape_league(league_id):
    logging.info(league_id)
    if league_id.upper() == 'NHL':
        # current server date YYYY-MM-DD
        start_date = flask.request.args.get('startDate', datetime.utcnow().strftime('%Y-%m-%d'))
        end_date = flask.request.args.get('endDate', start_date)
        
        nhl_scrape = nhl.NHLScrape(start_date, end_date)
        models.ApplicationVariable.set_app_var(league_id, nhl_scrape.game_list)
    else:
        return '404 Not Found', 404
    
    return 'Success'