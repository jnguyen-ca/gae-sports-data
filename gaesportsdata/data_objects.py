# -*- coding: utf-8 -*-


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
        
class NHLGame(Game):
    """Object to hold information about a NHL game"""
    
    def __init__(self):
        super(NHLGame, self).__init__()
        
        self.goalie_away = None
        self.goalie_home = None
        
class MLBGame(Game):
    """Object to hold information about a MLB game"""
    
    def __init__(self):
        super(MLBGame, self).__init__()
        
        self.pitcher_away = None
        self.pitcher_home = None