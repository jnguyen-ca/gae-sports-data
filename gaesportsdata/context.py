# -*- coding: utf-8 -*-

from google.appengine.api import users

import pytz

from . import app
import models
import constants

@app.template_filter()
def convert_datetime(s):
    """Convert to my local time (MST)"""
    mst_datetime = s.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('MST7MDT'))
    return mst_datetime.date().strftime('%B %d'), mst_datetime.time().strftime('%I:%M %p')

@app.context_processor
def team_processor():
    def _team_display_name(sport, league, name):
        """Change to shorter name for display"""
        team_names_app_var = models.ApplicationVariable.get_app_var(constants.APPVAR_TEAM_NAMES_KEY)
        if team_names_app_var:
            try:
                name = team_names_app_var[sport][league][name]['display']
            except KeyError:
                pass
        return name
    return dict(team_display_name=_team_display_name)

@app.context_processor
def sys_processor():
    def _get_app_var(key):
        if key in constants.APPVAR_DISPLAY_LIST:
            return models.ApplicationVariable.get_app_var(key)
        return None
    
    def _is_logged_in():
        if users.get_current_user():
            return True
        return False
    
    def _is_admin():
        return users.is_current_user_admin()
    
    def _login_link(endpoint):
        return users.create_login_url(endpoint)
        
    return dict(get_app_var=_get_app_var,
                is_logged_in=_is_logged_in,
                is_admin=_is_admin,
                login_link=_login_link)