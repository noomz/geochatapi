'''
GeoChat API module

updated: December 15, 2009

TODO: Exception capturing.
'''

import logging
import urllib
import urllib2

from xml.etree.ElementTree import fromstring

BASE_API_URL = "http://geochat.instedd.org/api/"
# GeoChat requires this realm.
REALM = "Custom Basic Authentication"

class Geochat(object):
    '''Geochat API Implementation for appengine only.'''

    def __init__(self, user, password):
        '''
        Prepare basic authentication.
        '''

        self.user = user
        self.password = password
        self._build_opener()

    def _build_opener(self):
        '''
        Build urllib2 opener for GeoChat API.
        '''

        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(REALM,
                                  BASE_API_URL,
                                  self.user,
                                  self.password)

        self._opener = urllib2.build_opener(auth_handler)

    def get(self, resource, data={}):
        '''
        Helper function to GET http method.
        '''

        data = urllib.urlencode(data)
        request = BASE_API_URL + resource + '?' + data
        return self._opener.open(request)

    def post(self, resource, data={}):
        '''
        Helper function to POST http method.
        '''

        data = urllib.urlencode(data)
        return self._opener.open(BASE_API_URL, data)

    def send_group(self, group, message):
        '''
        http://geochathelp.com/doku.php?id=api:apisendmessagetogroup

        Sends a Message on behalf of the authenticated User to a specific
        Group. The User must be a member of the Group.
        '''

        data = {'message':message}
        response = self.post('/api/groups/%s/messages.rss' % group, data)
        if response.status_code == 200:
            return True
        else:
            return False

    def get_user_groups(self, login):
        '''
        http://geochathelp.com/doku.php?id=api:apilistusergroups

        Returns the list of groups that a User belongs to.

        If the queried user is not the authenticated user, only the public 
        and shared private groups are returned. Only if the queried user is
        the logged in user, also the groups pending to join (Invited or
        PendingApproval) are listed. Items are ordered by last activity
        date. Most recent ones first.
        '''

        response = self.get('/api/users/%s/groups.rss' % login)
        rss = fromstring(response.content) if response.status_code == 200 else None
        return rss
