# -*- coding: utf-8 -*-

from google.appengine.ext import vendor
vendor.add('lib')

# http://stackoverflow.com/a/42613280
import os, sys

on_appengine = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
if on_appengine and os.name == 'nt':
    sys.platform = "Not Windows"