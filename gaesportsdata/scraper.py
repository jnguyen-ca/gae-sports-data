# -*- coding: utf-8 -*-

"""
This module contains classes and methods that are responsible and used in
the scraping of sites.

"""

from datetime import datetime

from flask import Blueprint

import nhl
import models
import logging


app = Blueprint('scraper', __name__)

@app.route('/scrape/all')
def scrape_all():
    return scrape_league('NHL')

@app.route('/scrape/<league_id>')
def scrape_league(league_id):
    if league_id.upper() == 'NHL':
        nhl_scrape = nhl.NHLAPI()
        # current server date YYYY-MM-DD
        start_date = datetime.utcnow().strftime('%Y-%m-%d')
        end_date = start_date
        
        result = nhl_scrape.get_games(start_date, end_date)
    else:
        return '404 Not Found', 404
    
    models.ApplicationVariable.set_app_var(league_id, result)
    return