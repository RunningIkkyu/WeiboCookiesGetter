import requests
from setting import API_URL

class GetProxy(object):
    """ Class to get proxy from given API"""
    def __init__(self, api=API_URL):
        self.url = api

    def getproxy(self):
        """ 
        get one proxy 
        :return : a dict of proxy which can be used by request module
        """
        proxies = {}
        resp = requests.get(self.url)
        if resp.ok:
            proxy = resp.text
            proxies['http'] = 'http://' + proxy
            proxies['https'] = 'https://' + proxy
            return proxies
        return None
