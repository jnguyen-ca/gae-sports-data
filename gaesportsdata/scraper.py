# -*- coding: utf-8 -*-

"""Handles all scraping requests"""

from datetime import datetime, timedelta

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
        if value not in constants.LEAGUE_SPORT_MAP:
            return ValueError('invalid league')
        self._league = value
        
        self.game_list = models.ApplicationVariable.get_app_var(self.league)

    def fill_game_list(self, start_date, end_date):
        """
        Args:
            start_date (string): date string in iso 8601 format, defaults to current utc date
            end_date (string): date string in iso 8601 format, defaults to 1 day from start_date
        Returns:
            list of data_objects.Game
        """
        if not start_date:
            start_date = datetime.utcnow()
        
        if not end_date:
            if not isinstance(start_date, datetime):
                start_date = datetime.strptime(start_date,'%Y-%m-%d')
            end_date = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        
        if (self.league in [
                               constants.LEAGUE_ID_MLB,
                               constants.LEAGUE_ID_NHL,
                               ]
        ):
            info = game_info.MLBAMAPI(self.league, start_date, end_date)
        elif self.league == constants.LEAGUE_ID_NBA:
            info = game_info.NBA(self.league, start_date, end_date)
            
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
            VI.fill(self.game_list)
            models.ApplicationVariable.set_app_var(self.league, self.game_list)
            
        return self.game_list
    
    def fill_pitchers(self):
        if self.league == constants.LEAGUE_ID_MLB:
            usa = game_details.USAToday()
            usa.fill(self.game_list)
            models.ApplicationVariable.set_app_var(self.league, self.game_list)
            
        return self.game_list