# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import flask
import logging

import models
import nhl
import mlb

from . import app

league_ids = ['NHL', 'MLB']

@app.route('/')
def frontpage():
    # aka navigation page
    return flask.render_template('frontpage.html', leagues=league_ids)

@app.route('/<league_id>')
def league_page(league_id):
    league_id = league_id.upper()
    
    if league_id in league_ids:
        return flask.render_template('league_page.html', 
                                        league_title=league_id,
                                        games=models.ApplicationVariable.get_app_var(league_id)
                                    )
    
    return '404 Not Found', 404

@app.route('/scrape-all')
def scrape_all():
    for league in league_ids:
        scrape_league(league)
    return 'Done!'

@app.route('/scrape/<league_id>')
def scrape_league(league_id):
    league_id = league_id.upper()
    
    start_date = flask.request.args.get('startDate', datetime.utcnow().strftime('%Y-%m-%d'))
    logging.info('Scraping '+league_id+' for '+start_date)
    
    if league_id == 'NHL':
        end_date = flask.request.args.get('endDate', (datetime.strptime(start_date,'%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'))
        
        nhl_scrape = nhl.NHLScrape(start_date, end_date)
        models.ApplicationVariable.set_app_var(league_id, nhl_scrape.game_list)
    elif league_id == 'MLB':
        
        mlb_scrape = mlb.MLBScrape(start_date)
        models.ApplicationVariable.set_app_var(league_id, mlb_scrape.game_list)
    else:
        return '404 Not Found', 404
    
    return 'Success'