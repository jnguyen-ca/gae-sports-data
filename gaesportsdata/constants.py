# -*- coding: utf-8 -*-

LEAGUE_ID_NHL = 'NHL'
LEAGUE_ID_MLB = 'MLB'
LEAGUE_ID_NBA = 'NBA'

# contains all league ids for looping
LEAGUE_SPORT_MAP = {
                    LEAGUE_ID_NHL : 'Hockey',
                    LEAGUE_ID_MLB : 'Baseball',
                    LEAGUE_ID_NBA : 'Basketball',
                    }

APPVAR_TEAM_NAMES_KEY = 'Team Names'

# contains valid appvar keys that will be displayed
# and can be modified by admins on the frontend
APPVAR_DISPLAY_LIST = [
                       APPVAR_TEAM_NAMES_KEY,
                       ]