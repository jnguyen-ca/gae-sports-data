# -*- coding: utf-8 -*-

"""
This module contains the various Google Cloud Datastore models 
used throughout the application.

"""

from google.appengine.ext import ndb

import jsonpickle


class ApplicationVariable(ndb.Model):
    """Entities for the purpose of holding various data used
    throughout the application that can be easily modified."""
    value = ndb.TextProperty()
    
    @classmethod
    def get_app_var(cls, key, default=None):
        return jsonpickle.decode(ndb.Key(cls, key).get().value)
    
    @classmethod
    def set_app_var(cls, key, value):
        if not isinstance(value, basestring) and value is not None:
            value = jsonpickle.encode(value)
        return cls(id=key, value=value).put()