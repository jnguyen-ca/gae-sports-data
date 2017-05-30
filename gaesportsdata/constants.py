# -*- coding: utf-8 -*-

LEAGUE_ID_NHL = 'NHL'
LEAGUE_ID_MLB = 'MLB'
LEAGUE_ID_NBA = 'NBA'

# contains all league ids for looping
LEAGUE_SPORT_MAP = {}

import calendar, datetime
def _set_league_sport_map(league, sport, start_month=None, end_month=None):
    '''Set league to sport mapping only if current date within range'''
    if not start_month or not end_month:
        # year-round league
        LEAGUE_SPORT_MAP[league] = sport
        return
    
    month_to_num = dict((v,k) for k,v in enumerate(calendar.month_name))
    start_month_num = month_to_num[start_month]
    end_month_num = month_to_num[end_month]
    
    current_month_num = datetime.datetime.utcnow().month
    
    if start_month_num <= current_month_num <= end_month_num:
        LEAGUE_SPORT_MAP[league] = sport
        return
        
    if end_month_num < start_month_num:
        # range wraps around year
        if start_month_num <= current_month_num or current_month_num <= end_month_num:
            LEAGUE_SPORT_MAP[league] = sport
            
    return
        
_set_league_sport_map(LEAGUE_ID_NHL, 'Hockey', 'September', 'June')
_set_league_sport_map(LEAGUE_ID_MLB, 'Baseball', 'March', 'November')
_set_league_sport_map(LEAGUE_ID_NBA, 'Basketball', 'October', 'June')

APPVAR_TEAM_NAMES_KEY = 'Team Names'

# contains valid appvar keys that will be displayed
# and can be modified by admins on the frontend
APPVAR_DISPLAY_LIST = [
                       APPVAR_TEAM_NAMES_KEY,
                       ]