# -*- coding: utf-8 -*-

"""Module containing all objects responsible for retrieving basic game information 
and initializing their respective data_objects.Game() objects

"""

from google.appengine.api import urlfetch
from datetime import datetime
import json

import data_objects


class MLBAMAPI(object):
    """To retrieve data from MLB Advanced Media API"""
    
    GAME_STATUS_SCHEDULED = 'Scheduled'
    GAME_STATUS_PENDING = 'In Progress'
    GAME_STATUS_FINAL = 'Final'
    
    GAME_TYPE_REGULAR = 'R'
    GAME_TYPE_PLAYOFFS = 'P'
    
    def __init__(self, url, league_id):
        """
        Args:
            url (string): full url to fetch
            league_id (string): a valid league_id from constants.py
        """
        self.league_id = league_id
        self.url = url
        
        response = urlfetch.fetch(self.url)
        self.response_dict = json.loads(response.content)
        self.game_list = self.fill_data()
        
    def fill_data(self):
        """Parses response data into structured objects
        
        Returns:
            list: empty or list of data_objects.Game objects
        """
        games = []
        for date_data in self.response_dict['dates']:
            for game_dict in date_data['games']:
                game = data_objects.Game(self.league_id)
                game.datetime = datetime.strptime(game_dict['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
        
                # Not using yet so commented out
#                 game.type = game_dict['gameType']
#                 game.status = game_dict['status']['detailedState']
#                 if game.status is self.GAME_STATUS_FINAL:
#                     game.period = game_dict['linescore']['currentPeriodOrdinal']
                
                game.teams.away.name = game_dict['teams']['away']['team']['name']
                game.teams.home.name = game_dict['teams']['home']['team']['name']
                
                games.append(game)
                
        return games