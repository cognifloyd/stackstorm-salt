# pylint: disable=no-member

from st2common.runners.base_action import Action
from requests import Request
from lib.utils import sanitize_payload


class SaltPackage(object):
    _expression_forms = [
        'glob',
        'grain',
        'pillar',
        'nodegroup',
        'list',
        'compound'
    ]

    def __init__(self, client='local'):
        self._data = {"eauth": "",
                      "username": "",
                      "password": "",
                      "client": "",
                      "fun": ""}

        self._data['client'] = client

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, key_value=[]):
        key, value = key_value
        self._data[key] = value


class SaltAction(Action):

    def __init__(self, config):
        super(SaltAction, self).__init__(config=config)
        self.url = self.config.get('api_url', None)
        self.eauth = self.config.get('eauth', None)
        self.username = self.config.get('username', None)
        self.password = self.config.get('password', None)

    def generate_package(self, client='local', cmd=None,
                         **kwargs):
        self.data = SaltPackage(client).data
        self.data['eauth'] = self.eauth
        self.data['username'] = self.username
        self.data['password'] = self.password
        if cmd:
            self.data['fun'] = cmd
        if client == 'local':
            self.data['tgt'] = kwargs.get('target', '*')
            self.data['tgt_type'] = kwargs.get('tgt_type', 'glob')
        if isinstance(kwargs.get('args', []), list) and len(kwargs.get('args', [])) > 0:
            self.data['arg'] = kwargs['args']
        if len(kwargs.get('data', {})) > 0:
            if kwargs['data'].get('kwargs', None) is not None:
                self.data['kwarg'] = kwargs['data']['kwargs']
        clean_payload = sanitize_payload(('username', 'password'), self.data)
        self.logger.info("[salt] Payload to be sent: {0}".format(clean_payload))

    def generate_request(self):
        req = Request('POST',
                      "{0}/run".format(self.url),
                      headers={'content-type': 'application/json',
                               'charset': 'utf-8'})
        return req.prepare()
