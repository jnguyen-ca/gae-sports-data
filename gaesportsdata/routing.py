# -*- coding: utf-8 -*-

"""Handles all app routing and rendering"""

from google.appengine.api.urlfetch_errors import DeadlineExceededError
import flask
import logging

import models
import scraper
import appvars
import constants

from . import app

@app.url_value_preprocessor
def preprocess_url_values(endpoint, values):
    if app.url_map.is_endpoint_expecting(endpoint, 'league_id'):
        if 'league_id' in values:
            values['league_id'] = values['league_id'].upper()

@app.route('/')
def frontpage():
    # aka navigation page
    return flask.render_template('frontpage.html', leagues=constants.LEAGUE_SPORT_MAP.keys())

@app.route('/<league_id>')
def league_page(league_id):
    if league_id in constants.LEAGUE_SPORT_MAP:
        return flask.render_template('league_page.html', 
                                        league_title=league_id,
                                        games=models.ApplicationVariable.get_app_var(league_id)
                                    )
    
    return '404 Not Found', 404

@app.route('/scrape-all')
@app.route('/scrape/<league_id>')
def scrape_league(league_id=None):
    details_only = flask.request.args.get('detailsOnly')
    details_list = flask.request.args.get('details', '')
    start_date = flask.request.args.get('startDate')
    end_date = flask.request.args.get('endDate')
    
    url_rule = flask.request.url_rule
    if url_rule.rule.startswith('/scrape-all'):
        league_list = constants.LEAGUE_SPORT_MAP.keys()
        details_list = True
    else:
        if league_id in constants.LEAGUE_SPORT_MAP:
            league_list = [league_id]
        else:
            return '404 Not Found', 404
        
        details_list = [x.lower() for x in details_list.split(',')]
        
    for league_key in league_list:
        scraper_object = scraper.Scraper(league_key)
        
        try:
            if not details_only:
                scraper_object.fill_game_list(start_date, end_date)
            
            if details_list is True or 'odds' in details_list:
                scraper_object.fill_game_odds()
                
            if details_list is True or 'pitchers' in details_list:
                scraper_object.fill_pitchers()
        except DeadlineExceededError as e:
            # one of the sites probably temporarily down
            logging.exception(e)
    
    return 'Success'

@app.route('/appvars', methods=['GET', 'POST'])
def appvars_page():
    if flask.request.method == 'GET':
        return flask.render_template('appvars.html', app_var_keys=constants.APPVAR_DISPLAY_LIST)
    elif flask.request.method == 'POST':
        return appvars.handle_request()