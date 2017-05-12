# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import flask
import logging

import models
import game_info
import constants

from . import app


@app.route('/')
def frontpage():
    # aka navigation page
    return flask.render_template('frontpage.html', leagues=constants.LEAGUE_ID_LIST)

@app.route('/<league_id>')
def league_page(league_id):
    league_id = league_id.upper()
    
    if league_id in constants.LEAGUE_ID_LIST:
        return flask.render_template('league_page.html', 
                                        league_title=league_id,
                                        games=models.ApplicationVariable.get_app_var(league_id)
                                    )
    
    return '404 Not Found', 404

@app.route('/scrape-all')
def scrape_all():
    for league in constants.LEAGUE_ID_LIST:
        scrape_league(league)
    return 'Done!'

@app.route('/scrape/<league_id>')
def scrape_league(league_id):
    league_id = league_id.upper()
    
    start_date = flask.request.args.get('startDate', datetime.utcnow().strftime('%Y-%m-%d'))
    logging.info('Scraping '+league_id+' for '+start_date)
    
    if league_id == constants.LEAGUE_ID_NHL:
        end_date = flask.request.args.get('endDate', (datetime.strptime(start_date,'%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d'))
        
        url = ("https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s"
               "&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,team.leaders"
               ",schedule.game.seriesSummary,seriesSummary.series&leaderCategories=points,goals"
               ",assists&leaderGameTypes=P&site=en_nhlCA&teamId=&gameType=&timecode=") % (start_date, end_date)
        
        nhl_info = game_info.MLBAMAPI(url=url, league_id=constants.LEAGUE_ID_NHL)
        models.ApplicationVariable.set_app_var(league_id, nhl_info.game_list)
    elif league_id == constants.LEAGUE_ID_MLB:
        url = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=%s"
               "&hydrate=team,linescore(matchup,runners),flags,liveLookin,broadcasts(all),"
               "decisions,person,probablePitcher,stats,homeRuns,previousPlay,"
               "game(content(media(featured,epg),summary),tickets)") % (start_date)
        
        mlb_info = game_info.MLBAMAPI(url=url, league_id=constants.LEAGUE_ID_MLB)
        models.ApplicationVariable.set_app_var(league_id, mlb_info.game_list)
    else:
        return '404 Not Found', 404
    
    return 'Success'