# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch
from datetime import datetime
import json

import data_objects
import constants


class MLBAMAPI(object):
    """To retrieve data from MLB Advanced Media API"""
    
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
                if self.league_id == constants.LEAGUE_ID_NHL:
                    game = data_objects.NHLGame()
                    game.sport = 'Hockey'
                    game.league = constants.LEAGUE_ID_NHL
                elif self.league_id == constants.LEAGUE_ID_MLB:
                    game = data_objects.MLBGame()
                    game.sport = 'Baseball'
                    game.league = constants.LEAGUE_ID_MLB
                
                game.datetime = datetime.strptime(game_dict['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
        
                game.type = game_dict['gameType']
                game.status = game_dict['status']['detailedState']
                if game.status is game.GAME_STATUS_FINAL:
                    game.period = game_dict['linescore']['currentPeriodOrdinal']
                
                game.team_away = game_dict['teams']['away']['team']['name']
                game.team_home = game_dict['teams']['home']['team']['name']
                
                games.append(game)
                
        return games