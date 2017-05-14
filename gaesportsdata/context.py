# -*- coding: utf-8 -*-

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
def team_display_name():
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