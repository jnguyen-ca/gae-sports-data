# -*- coding: utf-8 -*-

"""Responsible for any data retrieval that cannot be retrieved by game_info objects.
Requires existing data_object.Game objects filled out by game_info classes

"""


from google.appengine.api import urlfetch
from datetime import datetime, date
import time
import logging

from lxml import etree, html
import pytz

import constants
import testing_data


class VegasInsider(object):
    """Retrieve data from vegasinsider.com"""
    
    timezone = pytz.timezone('US/Eastern')
    
    def __init__(self, league_id, games):
        """
        Args:
            league_id (string): a valid league_id from constants.py
            games (list): list of existing data_object.Game
        """
        self.league_id = league_id
        self.games = games
        
        # just in case app league id doesn't correspond to vi league id
        if self.league_id == constants.LEAGUE_ID_NHL:
            self.vi_league_id = 'nhl'
        elif self.league_id == constants.LEAGUE_ID_MLB:
            self.vi_league_id = 'mlb'
            
    def fill_odds(self):
        """Scrapes odds from vegasinsider and fills corresponding games attributes"""
        
        odds_dict = self._scrape_odds()
        
        for game in self.games:
            game_info = {
                         'datetime' : game.datetime.replace(tzinfo=pytz.utc).astimezone(self.timezone),
                         'team_away' : game.team_away,
                         'team_home' : game.team_home,
                         }
            
            for index, odds_game in enumerate(odds_dict['vegas']):
                if self._matching_odds(game_info, odds_game):
                    game.moneyline_open_away = odds_game['odds_team_away']
                    game.moneyline_open_home = odds_game['odds_team_home']
                    #TODO: remove used from list
            # good chance pages were sorted the same so can check using index otherwise have to loop
#             if index in odds_dict['offshore'] and self._matching_odds(game_info, odds_dict['offshore'][index]):
#                 #TODO: fill it out
#                 pass
        
        return self.games
    
    def _matching_odds(self, game_info, odds_game):
        """Determine if game_info and odds_game refer to the same game
        Args:
            game_info (dict): with keys datetime, team_away, team_home
            odds_game (dict): individual game from self._scrape_game_odds_tree()
        Returns:
            boolean
        """
        # margin of error of 15 minutes
        time_difference = divmod((game_info['datetime'] - odds_game['datetime']).total_seconds(), 60)
        if abs(time_difference[0]) < 15:
            if (odds_game['team_away'] in game_info['team_away'] 
                and odds_game['team_home'] in game_info['team_home']):
                return True
        return False
    
    def _scrape_odds(self):
        """Makes requests to vegasinsider odds pages to get game odds
        
        Returns:
            dict: values are self._scrape_game_odds_tree()
        """
        logging.info('Scraping VegasInsider for %s' % (self.vi_league_id))
        
        url = "http://www.vegasinsider.com/%s/odds/las-vegas/" % (self.vi_league_id)
        response = urlfetch.fetch(url)
        vegas_tree = etree.fromstring(response.content, etree.HTMLParser())

#         time.sleep(3)
#         url = "http://www.vegasinsider.com/%s/odds/offshore/" % (self.vi_league_id)
#         response = urlfetch.fetch(url)
#         offshore_tree = etree.fromstring(response.content, etree.HTMLParser())

        vegas_odds_tree = vegas_tree.xpath('//body/table//*[contains(@class, "main-content-cell")]/table//*[contains(@class, "frodds-data-tbl")]//tr')
        
        vegas_odds = self._scrape_game_odds_tree(vegas_odds_tree, 1)
#         offshore_odds = self._scrape_game_odds_tree(offshore_tree, 8)
        
        return {
                'vegas' : vegas_odds, 
#                 'offshore' : offshore_odds
                }
    
    def _scrape_game_odds_tree(self, odds_tree, odds_column=1):
        """See self._scrape_odds()
        
        Args:
            odds_tree (lxml.etree): parsed odds page
            odds_column (int): the column number of the desired odds
        Returns:
            list: of dict indicating game and its odds
        """
        game_odds = []
        for game_row_element in odds_tree:
            row_info_element = game_row_element[0]
            
            # only rows with game datetime in first element are wanted
            try:
                row_datetime = ' '.join(row_info_element[0].text.split())
            except AttributeError:
                continue
            try:
                row_datetime = self.timezone.localize(
                                    datetime.strptime(row_datetime, '%m/%d %I:%M %p').replace(year=date.today().year)
                                )
            except ValueError:
                continue
            
            row_teams_element = row_info_element.findall('b')
            row_team_away = row_teams_element[0].findtext('a').strip()
            row_team_home = row_teams_element[1].findtext('a').strip()
            
            row_odds_element = game_row_element[odds_column]
            
            row_odds_team_away = row_odds_team_home = None
            if row_odds_element.find('a') is not None:
                row_odds = list(row_odds_element.find('a').itertext())
                row_odds_team_away = row_odds[1].strip()
                row_odds_team_home = row_odds[2].strip()
            
            game_odds.append({
                               'datetime' : row_datetime,
                               'team_away' : row_team_away,
                               'team_home' : row_team_home,
                               'odds_team_away' : row_odds_team_away,
                               'odds_team_home' : row_odds_team_home,
                               })
        
        return game_odds