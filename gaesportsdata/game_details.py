# -*- coding: utf-8 -*-

"""Responsible for any data retrieval that cannot be retrieved by game_info objects.
Requires existing data_object.Game objects filled out by game_info classes

"""


from google.appengine.api import urlfetch, memcache
from datetime import datetime, date
import time
import re
import logging

from bs4 import BeautifulSoup
from lxml import etree
import pytz

import data_objects
import constants


class VegasInsider(object):
    """Retrieve data from vegasinsider.com"""
    
    timezone = pytz.timezone('US/Eastern')
    
    @property
    def league(self):
        return self._league
    @league.setter
    def league(self, value):
        # just in case app league id doesn't correspond to vi league id
        if value == constants.LEAGUE_ID_NHL:
            self.vi_league = 'nhl'
        elif value == constants.LEAGUE_ID_MLB:
            self.vi_league = 'mlb'
        else:
            raise ValueError('Invalid league id given')
        
        self._league = value
    
    def fill_odds(self, games):
        """Scrapes odds from vegasinsider and fills corresponding games attributes
        Args:
            games (list): list of existing data_object.Game
        Returns:
            list
        """
        try:
            self.sport = games[0].sport
            self.league = games[0].league
        except IndexError:
            return games
        
        odds_dict = self._request_odds()
        
        for game in games:
            vegas_odds = self._get_matching_odds(game, odds_dict['vegas'])
            if vegas_odds:
                game.teams.away.moneyline_open = vegas_odds['odds_team_away']
                game.teams.home.moneyline_open = vegas_odds['odds_team_home']
            #TODO: offshore
        
        return games
    
    def _get_matching_odds(self, game, odds_list):
        """Determine if game and odds_game refer to the same game
        Args:
            game (Game): 
            odds_list (list): list of odds from self._scrape_game_odds_tree
        Returns:
            dict: individual game from self._scrape_game_odds_tree
        """
        
        converted_game_datetime = game.datetime.replace(tzinfo=pytz.utc).astimezone(self.timezone)
        for odds_game in odds_list:
            time_difference = divmod((converted_game_datetime - odds_game['datetime']).total_seconds(), 60)
            # margin of error of 15 minutes
            if abs(time_difference[0]) < 15:
                if (game.teams.away.name == odds_game['team_away']
                    and game.teams.home.name == odds_game['team_home']):
                    return odds_game
        return None
    
    def _request_odds(self):
        """Makes requests to vegasinsider odds pages to get game odds
        
        Returns:
            dict: values are self._scrape_game_odds_tree()
        """
        if not memcache.add(type(self).__name__, True, 3):
            time.sleep(3)
        logging.info('Scraping VegasInsider for %s' % (self.vi_league))
            
        url = "http://www.vegasinsider.com/%s/odds/las-vegas/" % (self.vi_league)
        response = urlfetch.fetch(url)

#         time.sleep(3)
#         url = "http://www.vegasinsider.com/%s/odds/offshore/" % (self.vi_league)
#         response = urlfetch.fetch(url)
#         offshore_tree = etree.fromstring(response.content, etree.HTMLParser())

        try:
            vegas_odds = self._scrape_game_odds_tree(response.content, 1)
#         offshore_odds = self._scrape_game_odds_tree(offshore_tree, 8)
        except IndexError as e:
            logging.exception(e)
            vegas_odds = {}
        
        return {
                'vegas' : vegas_odds, 
#                 'offshore' : offshore_odds
                }
    
    def _scrape_game_odds_tree(self, htmlstring, odds_column=1):
        """See self._request_odds()
        
        Args:
            htmlstring (string): response string
            odds_column (int): the column number of the desired odds
        Returns:
            list: of dict indicating game and its odds
        """
        
        tree = etree.fromstring(htmlstring, etree.HTMLParser())
        odds_tree = tree.xpath('//body/table//*[contains(@class, "main-content-cell")]/table//*[contains(@class, "frodds-data-tbl")]//tr')
        
        game_odds = []
        for game_row_element in odds_tree:
            row_info_element = game_row_element[0]
            
            # only rows with game datetime in first element are wanted
            try:
                row_datetime = ' '.join(row_info_element[0].text.split())
            except AttributeError:
                continue
            try:
                row_datetime = self.timezone.localize(
                                    datetime.strptime(row_datetime, '%m/%d %I:%M %p').replace(year=date.today().year)
                                )
            except ValueError:
                continue
            
            row_teams_element = row_info_element.findall('b')
            row_team_away = row_teams_element[0].findtext('a').strip()
            row_team_home = row_teams_element[1].findtext('a').strip()
            
            team_away = data_objects.Team.get_team_id(self.sport, self.league, row_team_away) or row_team_away
            team_home = data_objects.Team.get_team_id(self.sport, self.league, row_team_home) or row_team_home
            
            row_odds_element = game_row_element[odds_column]
            
            row_odds_team_away = row_odds_team_home = None
            if row_odds_element.find('a') is not None:
                row_odds = list(row_odds_element.find('a').itertext())
                row_odds_team_away = row_odds[1].strip()
                row_odds_team_home = row_odds[2].strip()
            
            game_odds.append({
                               'datetime' : row_datetime,
                               'team_away' : team_away,
                               'team_home' : team_home,
                               'odds_team_away' : row_odds_team_away,
                               'odds_team_home' : row_odds_team_home,
                               })
        
        return game_odds

class USAToday(object):
    """Retrieve data from usatoday.com"""

    
    def fill(self, games):
        """Fills game with data
        Args:
            games (list): list of existing data_object.Game
        """
        
        try:
            self.sport = games[0].sport
            self.league = games[0].league
        except IndexError:
            return games
        
        if self.league != constants.LEAGUE_ID_MLB:
            raise ValueError('usatoday only supports mlb')
        
        ratings = self._request()
        
        for game in games:
            if (not hasattr(game.teams.home, 'pitcher')
                and not hasattr(game.teams.away, 'pitcher')
            ):
                continue
            
            for rating in ratings:
                if (rating['team'] == game.teams.home.name
                    and game.teams.home.pitcher
                    and rating['name'] == game.teams.home.pitcher['name']
                ):
                    game.teams.home.pitcher = rating
                elif (rating['team'] == game.teams.away.name
                    and game.teams.away.pitcher
                    and rating['name'] == game.teams.away.pitcher['name']
                ):
                    game.teams.away.pitcher = rating
        
        return games
    
    def _request(self):
        """Sends the request
        Returns:
            list
        """
        if not memcache.add(type(self).__name__, True, 3):
            time.sleep(3)
        logging.info('Scraping %s' % (type(self).__name__))
            
        url = "https://www.usatoday.com/sports/mlb/sagarin/2017/team/"
        response = urlfetch.fetch(url)
        
        try:
            ratings = self._scrape(response.content)
        except (AttributeError, IndexError) as e:
            logging.exception(e)
            ratings = []
            
        return ratings
        
    def _scrape(self, htmlstring):
        """Parses the response into desired data
        Args:
            htmlstring (string): response string
        Returns:
            list
        """
        
        soup = BeautifulSoup(htmlstring, 'html5lib')
        results = []
        
        # len 4, index 3 contains content after <b>endfile</b> in div[class="sagarin-page"]
        ratings = soup.find('div', {'class' : 'sagarin-page'}).contents[3]
        # gets all the "yyyy x League Batters/Pitchers thru..." sections, should be 60 of them (2 for each team)
        ratings = ratings.find_all('pre')
        
        for rating_section in ratings:
            # get the first string iteration which will contain the section header (i.e. "yyyy x League Batters/Pitchers thru...")
            header = rating_section.strings.next()
            if 'batters' in header.lower():
                # only interested in pitchers atm
                continue
            
            # due to malformed html use regex on all text in section
            regex = re.compile('([ABC]\s+\d+)\s+(\w+), (\w+)\s+(\w{3}) ([RL])\W+(\d+\.\d+)')
            pitchers = regex.finditer(rating_section.get_text().replace('\n',''))
            
            for pitcher in pitchers:
                ranking = pitcher.group(1)
                last_name = pitcher.group(2)
                first_name = pitcher.group(3)
                team_abbr = pitcher.group(4)
                handedness = pitcher.group(5)
                npera_rating = pitcher.group(6)
                
                team_id = data_objects.Team.get_team_id(self.sport, self.league, team_abbr)
                
                results.append({
                                'ranking' : ' '.join(ranking.split()),
                                'name' : first_name+' '+last_name,
                                'team' : team_id,
                                'handedness' : handedness,
                                'npera' : npera_rating,
                                })
                
        return results