# -*- coding: utf-8 -*-

"""Structured objects for scraped data"""

from datetime import datetime

import constants

    
class Game(object):
    def __init__(self, league_id):
        """
        Args:
            league_id (str): valid league id
        """
        
        self._set_sport_and_league(league_id.upper())
        self._datetime = None
        self._teams = Teams()
    
    @property
    def sport(self):
        return self._sport
    
    @property
    def league(self):
        return self._league
    
    @property
    def datetime(self):
        return self._datetime
    @datetime.setter
    def datetime(self, value):
        if not isinstance(value, datetime):
            raise ValueError('Must be datetime')
        self._datetime = value
        
    @property
    def teams(self):
        return self._teams
    @teams.setter
    def teams(self, value):
        if not isinstance(value, Teams):
            raise ValueError('Must be Teams')
        self._teams = value
        
    def _set_sport_and_league(self, league_id):
        if league_id not in constants.LEAGUE_ID_LIST:
            raise ValueError('Invalid league ID')
        
        self._league = league_id
        if league_id == constants.LEAGUE_ID_NHL:
            self._sport = 'Hockey'
        elif league_id == constants.LEAGUE_ID_MLB:
            self._sport = 'Baseball'
        
class Teams(object):
    def __init__(self):
        self._away = Team()
        self._home = Team()
    
    @property
    def away(self):
        return self._away
    @away.setter
    def away(self, value):
        if not isinstance(value, Team):
            raise ValueError('Must be Team object')
        self._away = value
        
    @property
    def home(self):
        return self._home
    @home.setter
    def home(self, value):
        if not isinstance(value, Team):
            raise ValueError('Must be Team object')
        self._home = value

class Team(object):
    """Hold detailed information about teams"""
    
    def __init__(self):
        self.name = None
        
        self.score = None
        
        self.moneyline_open = None
        self.moneyline = None