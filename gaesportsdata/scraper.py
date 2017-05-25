# -*- coding: utf-8 -*-

"""Handles all scraping requests"""


import game_info
import game_details
import models
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
        
        self.league = league_id

    @property
    def league(self):
        return self._league
    @league.setter
    def league(self, value):
        if self.league not in constants.LEAGUE_ID_LIST:
            return ValueError('invalid league')
        self._league = value
        
        self.game_list = models.ApplicationVariable.get_app_var(self.league)

    def fill_game_list(self, start_date, end_date):
        """
        Args:
            start_date (datetime|string): date string in iso 8601 format
            end_date (datetime|string): date string in iso 8601 format
        Returns:
            list of data_objects.Game
        """
        if (self.league in [
                               constants.LEAGUE_ID_MLB,
                               constants.LEAGUE_ID_NHL,
                               ]
        ):
            info = game_info.MLBAMAPI(self.league, start_date, end_date)
            self.game_list = info.game_list
            models.ApplicationVariable.set_app_var(self.league, self.game_list)
            
        return self.game_list
    
    def fill_game_odds(self):
        """
        Returns:
            list of data_objects.Game with filled game odds
        """
        if (self.league in [
                               constants.LEAGUE_ID_MLB,
                               constants.LEAGUE_ID_NHL,
                               ]
        ):
            VI = game_details.VegasInsider()
            VI.fill_odds(self.game_list)
            models.ApplicationVariable.set_app_var(self.league, self.game_list)
            
        return self.game_list
    
    def fill_pitchers(self):
        if self.league == constants.LEAGUE_ID_MLB:
            usa = game_details.USAToday()
            usa.fill(self.game_list)
            models.ApplicationVariable.set_app_var(self.league, self.game_list)
            
        return self.game_list