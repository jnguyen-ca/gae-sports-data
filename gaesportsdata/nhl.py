# -*- coding: utf-8 -*-

"""
This module contains the game model and classes that are responsible 
for accessing the NHL API located at statsapi.web.nhl.com

"""

from google.appengine.api import urlfetch
from datetime import datetime
import json

import pytz
import lxml.html

class NHLGame(object):
    """Object to hold information about a NHL game"""
    
    
    GAME_STATUS_SCHEDULED = 'Scheduled'
    GAME_STATUS_PENDING = 'In Progress'
    GAME_STATUS_FINAL = 'Final'
    
    GAME_TYPE_REGULAR = 'R'
    GAME_TYPE_PLAYOFFS = 'P'
    
    def __init__(self):
        self.datetime = None
        
        self.sport = None
        self.league = None
        
        self.team_away = None
        self.team_home = None
        
        self.score_away = None
        self.score_home = None
        
        self.type = None
        self.status = None
        self.period = None
        
        self.goalie_away = None
        self.goalie_home = None
        
        
class NHLScrape(object):
    """To retrieve NHL data from various sites and store into structured NHLGame objects"""
    
    
    def __init__(self, start_date, end_date):
        self.game_list = self.get_games(start_date, end_date)
    
    def get_games(self, start_date, end_date):
        """
        Args:
            start_date (str): format YYYY-MM-DD
            end_date (str): format YYYY-MM-DD
            
        Returns:
            list: empty or list of NHLGame objects
        """
        
        # validate date strings
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        url = ("https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s"
               "&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,team.leaders"
               ",schedule.game.seriesSummary,seriesSummary.series&leaderCategories=points,goals"
               ",assists&leaderGameTypes=P&site=en_nhlCA&teamId=&gameType=&timecode=") % (start_date, end_date)
        result = urlfetch.fetch(url)
        data_dict = json.loads(result.content)
        
        games = []
        for date_data in data_dict['dates']:
            for game_dict in date_data['games']:
                game = NHLGame()
                
                game.datetime = datetime.strptime(game_dict['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
        
                game.sport = 'Hockey'
                game.league = 'NHL'
                        
                game.type = game_dict['gameType']
                game.status = game_dict['status']['detailedState']
                if game.status is game.GAME_STATUS_FINAL:
                    game.period = game_dict['linescore']['currentPeriodOrdinal']
                
                game.team_away = game_dict['teams']['away']['team']['name']
                game.team_home = game_dict['teams']['home']['team']['name']
                
                games.append(game)
            
        return games
