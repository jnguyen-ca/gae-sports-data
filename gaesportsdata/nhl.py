# -*- coding: utf-8 -*-

"""
This module contains the game model and classes that are responsible 
for retrieving NHL data

"""

from google.appengine.api import urlfetch
from datetime import datetime
import json

import pytz
import lxml.html

import data_objects

        
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
                game = data_objects.NHLGame()
                
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
    
    def fill_data(self):
        for game in self.game_list:
            self.scrape_leftwinglock(game)
            
        return self.game_list
    
    def scrape_leftwinglock(self, game):
        date_string = game.datetime.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('EST')).date().isoformat()
        
        url = "http://leftwinglock.com/starting-goalies/index.php?date=%s" % date_string
        result = urlfetch.fetch(url)
        lxml_html = lxml.html.fromstring(result.content)
        
        games_html = lxml_html.cssselect('.l-main .l-content .g-cols')
        
#         for game_html in games_html:
#             
        
        return
        
    def scrape_hockeyreference(self, game):
        return
        