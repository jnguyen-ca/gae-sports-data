# -*- coding: utf-8 -*-

"""Module containing all objects responsible for retrieving basic game information 
and initializing their respective data_objects.Game() objects

"""

from google.appengine.api import urlfetch
from datetime import datetime, timedelta
import json
import logging

import data_objects
import constants


class MLBAMAPI(object):
    """To retrieve data from MLB Advanced Media API"""
    
    GAME_STATUS_SCHEDULED = 'Scheduled'
    GAME_STATUS_PENDING = 'In Progress'
    GAME_STATUS_FINAL = 'Final'
    
    GAME_TYPE_REGULAR = 'R'
    GAME_TYPE_PLAYOFFS = 'P'
    
    def __init__(self, league_id, start_date=None, end_date=None):
        """
        Args:
            league_id (string): a valid league_id from constants.py
            start_date (datetime|string): date string in iso 8601 format
            end_date (datetime|string): date string in iso 8601 format
        """
        self.league = league_id
        
        response = urlfetch.fetch(self.get_url(start_date, end_date))
        self.response_dict = json.loads(response.content)
        self.game_list = self.fill_data()
    
    @property
    def league(self):
        return self._league
    @league.setter
    def league(self, value):
        if (value not in [
                         constants.LEAGUE_ID_MLB,
                         constants.LEAGUE_ID_NHL,
                         ]
        ):
            raise ValueError('invalid league id for mlb advanced media api')
        self._league = value
    
    def get_url(self, start_date, end_date):
        """Returns appropriate url for given league id
        
        Args:
            start_date (datetime|string): date string in iso 8601 format
            end_date (datetime|string): date string in iso 8601 format
        Returns:
            string
        """
        if not start_date:
            start_date = datetime.utcnow()
        
        if not end_date:
            if not isinstance(start_date, datetime):
                start_date = datetime.strptime(start_date,'%Y-%m-%d')
            end_date = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
        elif isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')
            
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        
        logging.info("Requesting %s for %s until %s" % (self.league, start_date, end_date))
        if self.league == constants.LEAGUE_ID_NHL:
            url = ("https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s"
                   "&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,team.leaders"
                   ",schedule.game.seriesSummary,seriesSummary.series&leaderCategories=points,goals"
                   ",assists&leaderGameTypes=P&site=en_nhlCA&teamId=&gameType=&timecode=") % (start_date, end_date)
        elif self.league == constants.LEAGUE_ID_MLB:
            url = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=%s"
                   "&hydrate=team,linescore(matchup,runners),flags,liveLookin,broadcasts(all),"
                   "decisions,person,probablePitcher,stats,homeRuns,previousPlay,"
                   "game(content(media(featured,epg),summary),tickets)") % (start_date)
                   
        return url
        
    def fill_data(self):
        """Parses response data into structured objects
        
        Returns:
            list: empty or list of data_objects.Game objects
        """
        games = []
        for date_data in self.response_dict['dates']:
            for game_dict in date_data['games']:
                game = data_objects.Game(self.league)
                game.datetime = datetime.strptime(game_dict['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
        
                # Not using yet so commented out
#                 game.type = game_dict['gameType']
#                 game.status = game_dict['status']['detailedState']
#                 if game.status is self.GAME_STATUS_FINAL:
#                     game.period = game_dict['linescore']['currentPeriodOrdinal']
                
                game.teams.away.name = game_dict['teams']['away']['team']['name']
                game.teams.home.name = game_dict['teams']['home']['team']['name']
                
                try:
                    if self.league == constants.LEAGUE_ID_MLB:
                        game.teams.away.pitcher = {'name' : game_dict['teams']['away']['probablePitcher']['fullName']}
                        game.teams.home.pitcher = {'name' : game_dict['teams']['home']['probablePitcher']['fullName']}
                except KeyError:
                    pass
                
                games.append(game)
                
        return games