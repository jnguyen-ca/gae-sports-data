# -*- coding: utf-8 -*-

"""
This module contains the various Google Cloud Datastore models 
used throughout the application.

"""

from google.appengine.ext import ndb
from datetime import datetime
import json


class ApplicationVariable(ndb.Model):
    """Entities for the purpose of holding various data used
    throughout the application that can be easily modified."""
    value = ndb.TextProperty()
    
    @classmethod
    def set_app_var(cls, key, value):
        if not isinstance(value, basestring) and value is not None:
            value = json.dumps(value, default=lambda x: x.isoformat() if isinstance(x, datetime) else x.__dict__)
        return cls(id=key, value=value).put()