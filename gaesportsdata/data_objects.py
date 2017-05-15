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
        if not team_names_app_var:
            team_names_app_var = Team.__set_default_team_names_app_var()
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
    
################################################################################
#####TODO: get rid of this, TEMPORARY until app var editing is developed
    @staticmethod
    def __set_default_team_names_app_var():
        team_names_app_var = {
                              'Baseball' : {
                                        'MLB' : {
                                                'Houston Astros' : {'aliases' : [
                                                                                 'Houston'
                                                                                 ],
                                                                    'display':'Astros'},
                                                'New York Yankees' : {'aliases' : [
                                                                                   'N.Y. Yankees'
                                                                                   ],
                                                                      'display':'Yankees'},
                                                'Seattle Mariners' : {'aliases' : [
                                                                                   'Seattle'
                                                                                   ],
                                                                      'display':'Mariners'},
                                                'Toronto Blue Jays' : {'aliases' : [
                                                                                    'Toronto'
                                                                                    ],
                                                                       'display':'Blue Jays'},
                                                'Atlanta Braves' : {'aliases' : [
                                                                                 'Atlanta'
                                                                                 ],
                                                                    'display':'Braves'},
                                                'Miami Marlins' : {'aliases' : [
                                                                                'Miami'
                                                                                ],
                                                                   'display':'Marlins'},
                                                'Minnesota Twins' : {'aliases' : [
                                                                                  'Minnesota'
                                                                                  ],
                                                                     'display':'Twins'},
                                                'Cleveland Indians' : {'aliases' : [
                                                                                    'Cleveland'
                                                                                    ],
                                                                       'display':'Indians'},
                                                'Philadelphia Phillies' : {'aliases' : [
                                                                                        'Philadelphia'
                                                                                        ],
                                                                           'display':'Phillies'},
                                                'Washington Nationals' : {'aliases' : [
                                                                                       'Washington'
                                                                                       ],
                                                                          'display':'Nationals'},
                                                'Tampa Bay Rays' : {'aliases' : [
                                                                                 'Tampa Bay'
                                                                                 ],
                                                                    'display':'Rays'},
                                                'Boston Red Sox' : {'aliases' : [
                                                                                 'Boston'
                                                                                 ],
                                                                    'display':'Red Sox'},
                                                'New York Mets' : {'aliases' : [
                                                                                'N.Y. Mets'
                                                                                ],
                                                                   'display':'Mets'},
                                                'Milwaukee Brewers' : {'aliases' : [
                                                                                    'Milwaukee'
                                                                                    ],
                                                                       'display':'Brewers'},
                                                'San Diego Padres' : {'aliases' : [
                                                                                   'San Diego'
                                                                                   ],
                                                                      'display':'Padres'},
                                                'Chicago White Sox' : {'aliases' : [
                                                                                    'Chi. White Sox'
                                                                                    ],
                                                                       'display':'White Sox'},
                                                'Baltimore Orioles' : {'aliases' : [
                                                                                    'Baltimore'
                                                                                    ],
                                                                       'display':'Orioles'},
                                                'Kansas City Royals' : {'aliases' : [
                                                                                     'Kansas City'
                                                                                     ],
                                                                        'display':'Royals'},
                                                'Chicago Cubs' : {'aliases' : [
                                                                               'Chi. Cubs'
                                                                               ],
                                                                  'display':'Cubs'},
                                                'St Louis Cardinals' : {'aliases' : [
                                                                                      'St. Louis','St. Louis Cardinals'
                                                                                      ],
                                                                         'display':'Cardinals'},
                                                'Oakland Athletics' : {'aliases' : [
                                                                                    'Oakland'
                                                                                    ],
                                                                       'display':'Athletics'},
                                                'Texas Rangers' : {'aliases' : [
                                                                                'Texas'
                                                                                ],
                                                                   'display':'Rangers'},
                                                'Los Angeles Dodgers' : {'aliases' : [
                                                                                      'L.A. Dodgers'
                                                                                      ],
                                                                         'display':'Dodgers'},
                                                'Colorado Rockies' : {'aliases' : [
                                                                                   'Colorado'
                                                                                   ],
                                                                      'display':'Rookies'},
                                                'Detroit Tigers' : {'aliases' : [
                                                                                 'Detroit'
                                                                                 ],
                                                                    'display':'Tigers'},
                                                'Los Angeles Angels' : {'aliases' : [
                                                                                     'L.A. Angels'
                                                                                     ],
                                                                        'display':'Angels'},
                                                'Cincinnati Reds' : {'aliases' : [
                                                                                  'Cincinnati'
                                                                                  ],
                                                                     'display':'Reds'},
                                                'San Francisco Giants' : {'aliases' : [
                                                                                       'San Francisco'
                                                                                       ],
                                                                          'display':'Giants'},
                                                'Pittsburgh Pirates' : {'aliases' : [
                                                                                     'Pittsburgh'
                                                                                     ],
                                                                        'display':'Pirates'},
                                                'Arizona Diamondbacks' : {'aliases' : [
                                                                                       'Arizona'
                                                                                       ],
                                                                          'display':'Diamondbacks'},
                                                 }
                                        },
                              'Hockey' : {
                                        'NHL' : {
                                                 'Nashville Predators' : {'aliases' : ['Nashville'],
                                                                          'display' : 'Predators'
                                                                          },
                                                 'Anaheim Ducks' : {'aliases':['Anaheim'],'display':'Ducks'},
                                                 'Ottawa Senators' : {'aliases':['Ottawa'],'display':'Senators'},
                                                 'Pittsburgh Penguins' : {'aliases':['Pittsburgh'],'display':'Penguins'},
                                                 }
                                        }
                              }
        models.ApplicationVariable.set_app_var(constants.APPVAR_TEAM_NAMES_KEY, team_names_app_var)
        return team_names_app_var
    # end TODO
################################################################################