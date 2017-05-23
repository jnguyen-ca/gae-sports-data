# -*- coding: utf-8 -*-

"""Responsible for any data retrieval that cannot be retrieved by game_info objects.
Requires existing data_object.Game objects filled out by game_info classes

"""


from google.appengine.api import urlfetch, memcache
from datetime import datetime, date
import time
import logging

from lxml import etree
import pytz

import data_objects
import constants


class VegasInsider(object):
    """Retrieve data from vegasinsider.com"""
    
    timezone = pytz.timezone('US/Eastern')
    
    def __init__(self, league_id):
        """
        Args:
            league_id (string): a valid league_id from constants.py
        """
        self.league_id = league_id
        
        # just in case app league id doesn't correspond to vi league id
        if self.league_id == constants.LEAGUE_ID_NHL:
            self.vi_league_id = 'nhl'
        elif self.league_id == constants.LEAGUE_ID_MLB:
            self.vi_league_id = 'mlb'
        else:
            raise ValueError('Invalid league id given')
            
    def fill_odds(self, games):
        """Scrapes odds from vegasinsider and fills corresponding games attributes
        Args:
            games (list): list of existing data_object.Game
        """
        
        odds_dict = self._scrape_odds()
        
        for game in games:
            
            if game.league != self.league_id:
                raise ValueError('mismatch league ids')
            
            vegas_odds = self._get_matching_odds(game, odds_dict['vegas'])
            if vegas_odds:
                game.teams.away.moneyline_open = vegas_odds['odds_team_away']
                game.teams.home.moneyline_open = vegas_odds['odds_team_home']
            #TODO: offshore
        
        return games
    
    def _get_matching_odds(self, game, odds_list):
        """Determine if game and odds_game refer to the same game
        Args:
            game (Game): 
            odds_list (list): list of odds from self._scrape_game_odds_tree
        Returns:
            dict: individual game from self._scrape_game_odds_tree
        """
        
        converted_game_datetime = game.datetime.replace(tzinfo=pytz.utc).astimezone(self.timezone)
        for odds_game in odds_list:
            time_difference = divmod((converted_game_datetime - odds_game['datetime']).total_seconds(), 60)
            # margin of error of 15 minutes
            if abs(time_difference[0]) < 15:
                if (data_objects.Team.is_matching_team(game.sport, game.league, game.teams.away.name, odds_game['team_away'])
                    and data_objects.Team.is_matching_team(game.sport, game.league, game.teams.home.name, odds_game['team_home'])):
                    return odds_game
        return None
    
    def _scrape_odds(self):
        """Makes requests to vegasinsider odds pages to get game odds
        
        Returns:
            dict: values are self._scrape_game_odds_tree()
        """
        if not memcache.add(type(self).__name__, True, 3):
            time.sleep(3)
        logging.info('Scraping VegasInsider for %s' % (self.vi_league_id))
            
        url = "http://www.vegasinsider.com/%s/odds/las-vegas/" % (self.vi_league_id)
        response = urlfetch.fetch(url)
        vegas_tree = etree.fromstring(response.content, etree.HTMLParser())

#         time.sleep(3)
#         url = "http://www.vegasinsider.com/%s/odds/offshore/" % (self.vi_league_id)
#         response = urlfetch.fetch(url)
#         offshore_tree = etree.fromstring(response.content, etree.HTMLParser())

        vegas_odds_tree = vegas_tree.xpath('//body/table//*[contains(@class, "main-content-cell")]/table//*[contains(@class, "frodds-data-tbl")]//tr')
        
        try:
            vegas_odds = self._scrape_game_odds_tree(vegas_odds_tree, 1)
#         offshore_odds = self._scrape_game_odds_tree(offshore_tree, 8)
        except IndexError as e:
            logging.exception(e)
            vegas_odds = {}
        
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