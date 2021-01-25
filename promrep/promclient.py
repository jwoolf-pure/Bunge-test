import requests
import urllib
from datetime import datetime, timedelta
import sys

headers = {
     'Content-Type': 'application/x-www-form-urlencoded'
}

now = datetime.now()
delta = timedelta(weeks=1)
newtime = now - delta

ts = newtime.timestamp()



class PromClient:

    def __init__(self, url):
       self.url = url

    def query(self, q, **kwargs):

        time = kwargs.get('time', None)
        path = '/api/v1/query'

        enc = {'query': q}

        if time:
            enc['time'] = time
        else:
            eline = None

        eline = urllib.parse.urlencode(enc)
        path = path + '?' + eline
        uri = self.url + path

        response = requests.get(uri, headers=headers)
        return response

    def query_range(self, q, **kwargs):

        start = kwargs.get('start', None)
        end = kwargs.get('end', None)
        step = kwargs.get('step', None)

        path = '/api/v1/query_range'
        enc = { 'query': q }

        if start:
            enc['start'] = start
        if end:
            enc['end'] = end
        if step:
            enc['step'] = step

        eline = urllib.parse.urlencode(enc)
        path = path + '?' + eline
        uri = self.url + path

        print(uri)

        response = requests.get(uri, headers=headers)
        return response

