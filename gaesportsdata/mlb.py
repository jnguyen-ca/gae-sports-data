# -*- coding: utf-8 -*-

"""
This module contains the game model and classes that are responsible 
for retrieving MLB data

"""

from google.appengine.api import urlfetch
from datetime import datetime
import json

import data_objects

        
class MLBScrape(object):
    """To retrieve MLB data from various sites and store into structured MLBGame objects"""
    
    
    def __init__(self, start_date):
        self.game_list = self.get_games(start_date)
    
    def get_games(self, start_date):
        """
        Args:
            start_date (str): format YYYY-MM-DD
            end_date (str): format YYYY-MM-DD
            
        Returns:
            list: empty or list of MLBGame objects
        """
        
        # validate date strings
        datetime.strptime(start_date, '%Y-%m-%d')
        
        url = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=%s"
               "&hydrate=team,linescore(matchup,runners),flags,liveLookin,broadcasts(all),"
               "decisions,person,probablePitcher,stats,homeRuns,previousPlay,"
               "game(content(media(featured,epg),summary),tickets)") % (start_date)
        result = urlfetch.fetch(url)
        data_dict = json.loads(result.content)
        
        games = []
        for date_data in data_dict['dates']:
            for game_dict in date_data['games']:
                game = data_objects.MLBGame()
                
                game.datetime = datetime.strptime(game_dict['gameDate'],'%Y-%m-%dT%H:%M:%SZ')
        
                game.sport = 'Baseball'
                game.league = 'MLB'
                        
                game.type = game_dict['gameType']
                game.status = game_dict['status']['detailedState']
                if game.status is game.GAME_STATUS_FINAL:
                    game.period = game_dict['linescore']['currentPeriodOrdinal']
                
                game.team_away = game_dict['teams']['away']['team']['name']
                game.team_home = game_dict['teams']['home']['team']['name']
                
                games.append(game)
            
        return games            