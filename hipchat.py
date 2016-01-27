# coding: utf-8
#
# python-hipchat-notifications
#
# This small library allows sending messages to Hipchat rooms
# using the Hipchat API v2.
#
# Copyright (C) 2016 TFMT UG (haftungsbeschränkt)
# https://github.com/tfmt/python-hipchat-notifications

import json
import requests

__version__ = '0.1'


class AuthorizationError(ValueError):
    pass


class Hipchat(object):
    def __init__(self, token, server_url=None):
        """
        Initialize session.

        :param token: API Token
        :param server_url: Server URL (uses default HipChat cloud URL if not specified)
        """

        self.token = token
        self.server_url = server_url or 'https://www.hipchat.com'
        self.http_session = requests.Session()
        self.http_session.headers.update({
            'Authorization': 'Bearer {}'.format(token),
            'User-agent': 'python-hipchat-notifications/{} (https://github.com/tfmt/python-hipchat-notifications)'
                .format(__version__),
            'Content-type': 'application/json'
        })

    def get(self, path, **kwargs):
        """
        Wrapper for request session GET request.

        :param path: Path
        :param kwargs: Keyword arguments
        :return: Request response
        """

        return self._request('get', path, **kwargs)

    def post(self, path, **kwargs):
        """
        Wrapper for request session POST request.

        :param path: Path
        :param kwargs: Keyword arguments
        :return: Request response
        """

        return self._request('post', path, **kwargs)

    def send_notification(self, room_id, **kwargs):
        """
        Send room notification.

        :param room_id: Room ID or name
        :param kwargs: Keyword arguments
        :return: Request response
        """
        url = '/v2/room/{!s}/notification'.format(room_id)
        return self.post(url, data=json.dumps(kwargs))

    def _request(self, method, path, **kwargs):
        """
        Provide actual HTTP request and parse response for error check
        purposes.

        :param method: HTTP method to be used (lowercase)
        :param path: Absolute path
        :param kwargs: Keyword arguments
        :return: Request response
        """

        method = getattr(self.http_session, method)

        if not path.startswith('/v2/'):
            raise ValueError('path must be a valid Hipchat API v2 resource')

        try:
            response = method(self.server_url + path, **kwargs)
        except requests.RequestException:
            raise
        else:
            if response.status_code == 401:
                raise AuthorizationError(response.text)
            else:
                return response
