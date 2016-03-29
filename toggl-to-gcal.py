#!/usr/bin/python3

'''
toggl-to-gcal

A simple script for uploading Toggl entries into a Google calendar.

Requirements

- Python 3
- Toggl account
   - you need the API token from My Profile
- Google account
- Google calendar
   - you need to get Calendar Address of the calendar from the settings of the calendar
- Google project with OAuth 2.0 client ID
   - https://developers.google.com/google-apps/calendar/quickstart/python#prerequisites
   - you need the client_secret.json file

1. Set the timezone in toggl-to-gcal.py
2. Enter the Toggl token and Calendar address
3. Cope the client_secret.json file to the folder with the script
4. run python3 toggl-to-gcal.py YYYY-MM-DD to copy the entriens from Toggl to Google Calendar

Tomas Barton, tommz9@gmail.com
'''
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode

import pickle

import datetime
import iso8601

import sys

from gpush import push_entries

timezone = '-07'

# Toggl
api_token = 'FILL HERE'

# Google calendar
calendar_id = 'FILL HERE'


def get_project_details(pid):
    url = 'https://www.toggl.com/api/v8/projects/{}'.format(pid)
    headers = {'content-type': 'application/json'}
    print('getting project from toggl')
    r = requests.get(url, headers=headers,
                     auth=HTTPBasicAuth(api_token, 'api_token'))
    return r.json()['data']


def get_client_details(cid):
    url = 'https://www.toggl.com/api/v8/clients/{}'.format(cid)
    headers = {'content-type': 'application/json'}
    print('getting client from toggl')
    r = requests.get(url, headers=headers,
                     auth=HTTPBasicAuth(api_token, 'api_token'))
    return r.json()['data']


def get_entries(day):
    '''
    Get the list of entries for one particular day from Toggl
    '''

    url = 'https://www.toggl.com/api/v8/time_entries'
    headers = {'content-type': 'application/json'}

    isoday_start = day + 'T00' + timezone
    isoday_end = day + 'T23:59:59' + timezone
    isoday_start = iso8601.parse_date(isoday_start).isoformat()
    isoday_end = iso8601.parse_date(isoday_end).isoformat()

    query = {
        'start_date': isoday_start,
        'end_date': isoday_end
    }

    url += '?' + urlencode(query)
    r = requests.get(url, headers=headers,
                     auth=HTTPBasicAuth(api_token, 'api_token'))
    return r.json()


class Cache:
    ''' Cache for client and project details. To avoid multiple queries to
    API of Toggle while translating the client and project id to name.

    Can be serialized to file and used in the following runs
    '''

    def __init__(self, file='cache'):

        self.cache_file = file

        # try to load the cache from a file
        try:
            with open(file, 'rb') as f:
                self.projects, self.clients = pickle.load(f)
        except (FileNotFoundError, pickle.PickleError):
            # Just reset the cache
            self.projects = {}
            self.clients = {}

    def get_client(self, cid):
        try:
            client = self.clients[cid]
        except KeyError:
            client = get_client_details(cid)
            self.clients[cid] = client

        return client

    def get_project(self, pid):
        try:
            project = self.projects[pid]
        except KeyError:
            project = get_project_details(pid)
            self.projects[pid] = project

        return project

    def serialize(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump((self.projects, self.clients), f)


def decode_entries(entries, cache):
    ''' 
    Translates Toggl entry to a more readable format
    '''
    decoded = []
    for entry in entries:
        e = {}
        e['id'] = entry['id']
        e['start'] = entry['start']
        e['stop'] = entry['stop']
        e['duration'] = entry['duration']

        try:
            e['description'] = entry['description']
        except KeyError:
            e['description'] = ''

        project = cache.get_project(entry['pid'])
        client = cache.get_client(project['cid'])

        e['project'] = project['name']
        e['client'] = client['name']

        decoded.append(e)
    return decoded

if __name__ == '__main__':

	# Tak one parameter - the day which will be processed
    if len(sys.argv) != 2:
        print('The first argument is a date with YYY-MM-DD format')
        sys.exit(1)

    # Get the entries for one day from Toggl
    entries = get_entries(sys.argv[1])

    # Cache saves the project and client descriptions to disk
    cache = Cache()

    # Replace project id and client id with the names
    entries = decode_entries(entries, cache)

    # Save updated cache to the disk
    cache.serialize()

    # Send events to the calendar
    push_entries(entries, calendar_id)
