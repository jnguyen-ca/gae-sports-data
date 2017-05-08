# -*- coding: utf-8 -*-

"""
This module contains the game model and classes that are responsible 
for accessing the NHL API located at statsapi.web.nhl.com

"""

from google.appengine.api import urlfetch
from datetime import datetime
import json
import pytz


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
        
        
class NHLAPI(object):
    """To use undocumented NHL API at statsapi.web.nhl.com"""
    
    
    def get_games(self, start_date, end_date):
        """Fetches game list between start_date and end_date
        
        Args:
            start_date (str): format YYYY-MM-DD
            end_date (str): format YYYY-MM-DD
            
        Returns:
            _format_data(self, json_data)
        """
        
        # validate date strings
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        url = ("https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s"
               "&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,team.leaders"
               ",schedule.game.seriesSummary,seriesSummary.series&leaderCategories=points,goals"
               ",assists&leaderGameTypes=P&site=en_nhlCA&teamId=&gameType=&timecode=") % (start_date, end_date)
        result = urlfetch.fetch(url)
        json_data = json.loads(result.content)
        
        return self._format_data(json_data)
    
    def _format_data(self, json_data):
        """Formats the raw data retrieved into a configured object
        
        Args:
            json_data (object)
            
        Returns:
            list: empty or list of NHLGame objects
        """
        
        games = []
        for date_data in json_data['dates']:
            for json_game in date_data['games']:
                game = NHLGame()
                
                game.datetime = datetime.strptime(json_game['gameDate'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
        
                game.sport = 'Hockey'
                game.league = 'NHL'
                        
                game.type = json_game['gameType']
                game.status = json_game['status']['detailedState']
                if game.status is game.GAME_STATUS_FINAL:
                    game.period = json_game['linescore']['currentPeriodOrdinal']
                
                game.team_away = json_game['teams']['away']['team']['name']
                game.team_home = json_game['teams']['home']['team']['name']
                
                games.append(game)
            
        return games