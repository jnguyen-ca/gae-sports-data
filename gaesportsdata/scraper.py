# -*- coding: utf-8 -*-

"""Handles all scraping requests"""


import game_info
import game_details
import constants

class Scraper(object):
    """Creates scraping/api objects based on league and calls relevant functions
    to get desired data
    """
    
    def __init__(self, league_id):
        """
        Args:
            league_id (string): a valid league_id
        """
        self.league_id = league_id

    def get_game_list(self, start_date, end_date):
        """
        Args:
            start_date (datetime|string): date string in iso 8601 format
            end_date (datetime|string): date string in iso 8601 format
        Returns:
            list of data_objects.Game
        """
        if (self.league_id in [
                               constants.LEAGUE_ID_MLB,
                               constants.LEAGUE_ID_NHL,
                               ]
        ):
            info = game_info.MLBAMAPI(self.league_id, start_date, end_date)
            
        return info.game_list
    
    def fill_game_odds(self, game_list):
        """
        Args:
            game_list (list): list of data_objects.Game (see self.get_game_list())
        Returns:
            list of data_objects.Game with filled game odds
        """
        if not game_list:
            return game_list
        
        if (self.league_id in [
                               constants.LEAGUE_ID_MLB,
                               constants.LEAGUE_ID_NHL,
                               ]
        ):
            VI = game_details.VegasInsider(self.league_id)
            game_list = VI.fill_odds(game_list)
            
        return game_list