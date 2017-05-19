# -*- coding: utf-8 -*-

"""Structured objects for scraped data"""

from datetime import datetime
import logging

import models
import constants

    
class Game(object):
    def __init__(self, league_id):
        """
        Args:
            league_id (str): valid league id
        """
        
        self._set_sport_and_league(league_id.upper())
        self._datetime = None
        self._teams = Teams(self)
    
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
    def __init__(self, game):
        """
        Args:
            game (Game)
        """
        
        self.game = game
        self._away = Team(game)
        self._home = Team(game)
    
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
    
    def __init__(self, game):
        """
        Args:
            game (Game)
        """
        self.game = game
        
        self._name = None
        
        self.score = None
        
        self.moneyline_open = None
        self.moneyline = None
        
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        name_id = self.get_team_id(self.game.sport, self.game.league, value)
        if name_id:
            self._name = name_id
        self._name = value
    
    @staticmethod
    def is_matching_team(sport, league, name1, name2):
        if name1.upper() == name2.upper():
            return True
        
        name1_key = Team.get_team_id(sport, league, name1)
        name2_key = Team.get_team_id(sport, league, name2)
        if (name1_key
            and name1_key == name2_key
        ):
            return True
        
        return False
    
    @staticmethod
    def get_team_id(sport, league, name):
        """Get the key name of a team stored in the datastore from any of its possible aliases
        
        Args:
            sport (str): a valid Game.sport
            league (str): a valid league id
            name (str): name of team
        Returns:
            str|None: key name of team, None if no match
        """
        team_names_app_var = models.ApplicationVariable.get_app_var(constants.APPVAR_TEAM_NAMES_KEY)
        if team_names_app_var:
            name = name.upper()
            try:
                for team_id, team_properties in team_names_app_var[sport][league].iteritems():
                    if (
                        name == team_id.upper()
                        or name in (name_alias.upper() for name_alias in team_properties['aliases'])
                    ):
                        return team_id
            except KeyError:
                logging.debug("%s > %s > %s team name doesn't exist" % (sport, league, name))
        return None