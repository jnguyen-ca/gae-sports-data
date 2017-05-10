# -*- coding: utf-8 -*-

from datetime import datetime
import pytz

from . import app


@app.template_filter()
def convert_datetime(s):
    mst_datetime = datetime.strptime(s,'%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.utc).astimezone(pytz.timezone('MST7MDT'))
    return mst_datetime.date().strftime('%B %d'), mst_datetime.time().strftime('%I:%M %p')
