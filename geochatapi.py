'''
GeoChat API module

updated: December 15, 2009

TODO: Exception capturing.
'''

import logging
import urllib
import urllib2
import xml.etree.ElementTree as ET

BASE_API_URL = "http://geochat.instedd.org/api/"
# GeoChat requires this realm.
REALM = "Custom Basic Authentication"

# XML Namespaces
NS_GEO = "http://www.w3.org/2003/01/geo/wgs84_pos#"
NS_GEOCHAT = "http://geochat.instedd.org/api/1.0"
NS_ATOM = "http://www.w3.org/2005/Atom"

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
        response = self.post('groups/%s/messages.rss' % group, data)
        if response.code == 200:
            return True
        else:
            return False

    def get_user_groups(self, login=None):
        '''
        http://geochathelp.com/doku.php?id=api:apilistusergroups

        Returns the list of groups that a User belongs to.

        If the queried user is not the authenticated user, only the public 
        and shared private groups are returned. Only if the queried user is
        the logged in user, also the groups pending to join (Invited or
        PendingApproval) are listed. Items are ordered by last activity
        date. Most recent ones first.
        '''

        if not login:
            login = self.user

        response = self.get('users/%s/groups.rss' % login)
        if response.code == 200:
            rss = ET.fromstring(response.read())
        else:
            rss = None

        return rss

    def etree_find_ns(self, elem, ns, tag):
        '''
        Helper function.
        '''

        return elem.find('{%s}%s' % (ns, tag))

    def parse_messages(self, items):
        '''
        Get geochat messages ET element and return list of messages.
        '''

        def _parse_message(item):
            '''
            Helper function to parse each message.
            '''

            message = {}
            message['title'] = item.find('title').text
            message['author'] = item.find('author').text
            message['pubDate'] = item.find('pubDate').text
            message['guid'] = item.find('guid').text
            message['ThreadId'] = self.etree_find_ns(item, NS_GEOCHAT, 'ThreadId').text
            message['ResponseOf'] = self.etree_find_ns(item, NS_GEOCHAT, 'ResponseOf').text
            message['SenderAlias'] = self.etree_find_ns(item, NS_GEOCHAT, 'SenderAlias').text
            message['GroupAlias'] = self.etree_find_ns(item, NS_GEOCHAT, 'GroupAlias').text
            message['Route'] = self.etree_find_ns(item, NS_GEOCHAT, 'Route').text
            message['IsGroupBlast'] = self.etree_find_ns(item, NS_GEOCHAT, 'IsGroupBlast').text
            message['lat'] = self.etree_find_ns(item, NS_GEO, 'lat').text
            message['long'] = self.etree_find_ns(item, NS_GEO, 'long').text
            message['updated'] = self.etree_find_ns(item, NS_ATOM, 'updated').text

            return message

        messages = []
        for item in items:
            messages.append(_parse_message(item))

        return messages


    def get_group_messages(self, group, since=None, until=None, page=0):
        '''
        http://geochathelp.com/doku.php?id=api:apigetmessageinthegroup

        Returns the list of all Messages in the specified Group.
        '''

        data = {}
        if since:
            data['since'] = since
        if until:
            data['until'] = until
        if page:
            data['page'] = page

        response = self.get('groups/%s/messages.rss' % group, data)
        if response.code == 200:
            tree = ET.parse(response)
            elem = tree.getroot()
            msg = self.parse_messages(elem.findall('channel/item'))
            return msg
        else:
            return None
