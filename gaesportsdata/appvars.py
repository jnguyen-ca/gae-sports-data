# -*- coding: utf-8 -*-

"""Handles Application Variable (appvars) ajax requests"""

from google.appengine.api import users
import re
import ast
import json
import cgi
import logging
import pprint

import flask

import models
import constants


def handle_request():
    if not users.is_current_user_admin():
        flask.abort(403)
    
    app_var_id = flask.request.form['app-var-id']
    logging.info(app_var_id)
    if app_var_id not in constants.APPVAR_DISPLAY_LIST:
        flask.abort(400)
    
    request_type = flask.request.form['request-type']
    request_value = flask.request.form['request-value']
    logging.info('Request : (%s), AppVar : (%s)' % (request_type, app_var_id))
    
    if request_type == 'add-edit-entry':
        app_var = models.ApplicationVariable.get_app_var(app_var_id)
    else:
        flask.abort(400)
    
    try:
        # leave numeric strings alone but evaluate lists and dicts
        if not request_value.isnumeric():
            request_value = ast.literal_eval(request_value)
            
            # convert everything to unicode
            if isinstance(request_value, str):
                request_value = request_value.decode('utf-8')
            elif isinstance(request_value, list):
                request_value = [x.decode('utf-8') if isinstance(x, str) else x for x in request_value]
            elif isinstance(request_value, dict):
                request_value = {k.decode('utf8'): v.decode('utf8') for k, v in request_value.items()}
    except (SyntaxError, ValueError):
        flask.response = flask.jsonify({'message' : 'Incorrect formatting provided. Please provide valid Python literal structure.'})
        flask.response.status_code(400)
        return flask.response
    except AttributeError:
        flask.response = flask.jsonify({'message' : 'Currently nested dicts are not supported. Please do 1 level at a time.'})
        flask.response.status_code=400
        return flask.response
    
    try:
        key_list = re.findall('\[([^\]]+)\]', flask.request.form['dict-ancestor-keys'])
        key_list = [key.strip() for key in key_list]
        entry_key = flask.request.form['dict-entry-key']
        entry_level = flask.request.form['dict-entry-level']
    except KeyError:
        entry_key = None
        
    if entry_key:
        key_list.append(entry_key)
        logging.info('Setting dict entry: %s' % (str(key_list)))
        set_in_dict(app_var, key_list, request_value)
        
        models.ApplicationVariable.set_app_var(app_var_id, app_var)
        
        display_dict_entry = flask.get_template_attribute('macros.html', 'display_dict_entry')
        return display_dict_entry(entry_key, request_value, int(entry_level))
    else:
        # TODO: haven't finished yet
        flask.abort(400)
        
    display = flask.get_template_attribute('macros.html', 'display')
    return display(request_value)

def get_from_dict(dictionary, key_list):
    """Get a dictionary entry via a list of keys
    https://stackoverflow.com/questions/14692690/access-python-nested-dictionary-items-via-a-list-of-keys/14692747#14692747
    """
    return reduce(lambda d, k: d[k], key_list, dictionary)

def set_in_dict(dictionary, key_list, value):
    """Set a value for a dictionary entry via a list of keys
    https://stackoverflow.com/questions/14692690/access-python-nested-dictionary-items-via-a-list-of-keys/14692747#14692747
    """
    get_from_dict(dictionary, key_list[:-1])[key_list[-1]] = value
    
def del_in_dict(dictionary, key_list):
    """Delete a element in a dictionary entry via a list of keys
    """
    get_from_dict(dictionary, key_list[:-1]).pop(key_list[-1], None)