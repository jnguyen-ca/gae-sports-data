# -*- coding: utf-8 -*-

"""Contains structured object for each sport for easier data manipulation"""

from datetime import datetime

import constants


def create_object(league_id=None, values=None):
    """
    Args:
        league_id (str): valid league id
        values (dict): starting values
    Returns:
        Game: appropriate object
    """
    if not league_id and (not values or 'league' not in values):
        raise ValueError('No league ID given')
    elif league_id and values and 'league' in values and league_id != values['league']:
        raise ValueError('Conflicting league IDs given')
    elif not league_id:
        league_id = values['league']
    
    if league_id == constants.LEAGUE_ID_NHL:
        game = NHLGame()
    elif league_id == constants.LEAGUE_ID_MLB:
        game = MLBGame()
    
    if values:
        game.__dict__ = values
        game.datetime = datetime.strptime(game.datetime,'%Y-%m-%dT%H:%M:%S')
    return game
    
class Game(object):
    
    GAME_STATUS_SCHEDULED = 'Scheduled'
    GAME_STATUS_PENDING = 'In Progress'
    GAME_STATUS_FINAL = 'Final'
    
    GAME_TYPE_REGULAR = 'R'
    GAME_TYPE_PLAYOFFS = 'P'
    
    def __init__(self):
        self.datetime = None
        
        self.sport = None
        self.league = None
        
        self.team_away = None
        self.team_home = None
        
        self.score_away = None
        self.score_home = None
        
        self.type = None
        self.status = None
        self.period = None
        
        self.moneyline_open_away = None
        self.moneyline_open_home = None
        self.moneyline_away = None
        self.moneyline_home = None
        
class NHLGame(Game):
    """Object to hold information about a NHL game"""
    
    def __init__(self):
        super(NHLGame, self).__init__()
        
        self.sport = 'Hockey'
        self.league = constants.LEAGUE_ID_NHL
        
        self.goalie_away = None
        self.goalie_home = None
        
class MLBGame(Game):
    """Object to hold information about a MLB game"""
    
    def __init__(self):
        super(MLBGame, self).__init__()
        
        self.sport = 'Baseball'
        self.league = constants.LEAGUE_ID_MLB
        
        self.pitcher_away = None
        self.pitcher_home = None