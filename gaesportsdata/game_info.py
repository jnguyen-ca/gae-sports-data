# -*- coding: utf-8 -*-

"""Module containing all objects responsible for retrieving basic game information 
and initializing their respective data_objects.Game() objects

"""

from google.appengine.api import urlfetch
from datetime import datetime
import json
import logging

import data_objects
import constants


class GameInfo(object):
    def __init__(self, league_id, start_date, end_date):
        """
        Args:
            league_id (string): a valid league_id from constants.py
            start_date (string): date string in iso 8601 format
            end_date (string): date string in iso 8601 format
        """
        self.league = league_id
        self.start_date = start_date
        self.end_date = end_date
        
        logging.info("Requesting %s for %s until %s" % (self.league, self.start_date, self.end_date))
        response = urlfetch.fetch(self.url)
        self.response_dict = json.loads(response.content)
        
        self.game_list = self.parse_game_list()
        
    def valid_date(self, game_datetime):
        if (game_datetime.date() >= datetime.strptime(self.start_date,'%Y-%m-%d').date()
            and game_datetime.date() <= datetime.strptime(self.end_date,'%Y-%m-%d').date()
        ):
            return True
        return False

class MLBAMAPI(GameInfo):
    """To retrieve data from MLB Advanced Media API"""
    
#     GAME_STATUS_SCHEDULED = 'Scheduled'
#     GAME_STATUS_PENDING = 'In Progress'
#     GAME_STATUS_FINAL = 'Final'
#     
#     GAME_TYPE_REGULAR = 'R'
#     GAME_TYPE_PLAYOFFS = 'P'
    
    @property
    def url(self):
        """Returns appropriate url for given league id
        
        Returns:
            string
        """
        if self.league == constants.LEAGUE_ID_NHL:
            url = ("https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s"
                   "&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,team.leaders"
                   ",schedule.game.seriesSummary,seriesSummary.series&leaderCategories=points,goals"
                   ",assists&leaderGameTypes=P&site=en_nhlCA&teamId=&gameType=&timecode=") % (self.start_date, self.end_date)
        elif self.league == constants.LEAGUE_ID_MLB:
            url = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=%s"
                   "&hydrate=team,linescore(matchup,runners),flags,liveLookin,broadcasts(all),"
                   "decisions,person,probablePitcher,stats,homeRuns,previousPlay,"
                   "game(content(media(featured,epg),summary),tickets)") % (self.start_date)
        else:
            raise ValueError('invalid league id for mlb advanced media api')
                   
        return url
        
    def parse_game_list(self):
        """Parses response data into structured objects
        
        Returns:
            list: list of data_objects.Game objects
        """
        games = []
        for date_data in self.response_dict['dates']:
            for game_dict in date_data['games']:
                game = data_objects.Game(self.league)
                game.datetime = datetime.strptime(game_dict['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
                
                if not self.valid_date(game.datetime):
                    continue
        
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
    
class NBA(GameInfo):
    @property
    def url(self):
        return "https://watch.nba.com/schedule?date=%s&format=json" % (self.start_date)
    
    def parse_game_list(self):
        games = []
        
        for game_dict in self.response_dict['games']:
            game = data_objects.Game(self.league)
            game.datetime = datetime.strptime(game_dict['dateTimeGMT'],'%Y-%m-%dT%H:%M:%S.000')
            
            if not self.valid_date(game.datetime):
                continue
        
            game.teams.away.name = game_dict['awayTeam']['name']
            game.teams.home.name = game_dict['homeTeam']['name']
            
            games.append(game)
        
        return games