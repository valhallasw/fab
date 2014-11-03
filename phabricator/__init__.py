#!/usr/bin/env python

import hashlib
import json
import requests
import time


class Phabricator:
    def __init__(self, host, user, cert):
        self.host = host
        self.user = user
        self.cert = cert
        self.phab_session = {}
        self.token = int(time.time())
        self.signature = hashlib.sha1(str(self.token) + self.cert).hexdigest()
        self.req_session = requests.Session()

    @property
    def connect_params(self):
        return {
            'client': 'phab-bz',
            'clientVersion': 0,
            'clientDescription': 'A script for importing Bugzilla bugs into Phabricator',
            'user': self.user,
            'host': self.host,
            'authToken': self.token,
            'authSignature': self.signature,
        }

    def connect(self):
        req = self.req_session.post('%s/api/conduit.connect' % self.host, data={
            'params': json.dumps(self.connect_params),
            'output': 'json',
            '__conduit__': True,
        })

        # Parse out the response (error handling ommitted)
        result = json.loads(req.content)['result']
        self.phab_session = {
            'sessionKey': result['sessionKey'],
            'connectionID': result['connectionID'],
        }

    def request(self, method, params=None):
        if params is None:
            params = {}
        if not self.phab_session:
            self.connect()
        url = '%s/api/%s' % (self.host, method)
        params['__conduit__'] = self.phab_session
        req = self.req_session.post(url, data={
            'params': json.dumps(params),
            'output': 'json',
        })
        return json.loads(req.content)['result']
