# coding: utf-8
#
# python-hipchat-notifications
#
# This small library allows sending messages to Hipchat rooms
# using the Hipchat API v2.
#
# Copyright (C) 2016 TFMT UG (haftungsbeschränkt)
# https://github.com/tfmt/python-hipchat-notifications

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

    def put(self, path, **kwargs):
        """
        Wrapper for request session PUT request.
        :param path: Path
        :param kwargs: Keyword arguments
        :return: Request response
        """

        return self._request('put', path, **kwargs)

    def send_message(self, room_id, message):
        url = "/v2/room/{}/message".format(room_id)
        data = {"message":message}
        return self.post(url, data=json.dumps(data))

    def get_messages(self, id_or_email, max_results=75, reverse=True, start_index=0, include_deleted=True, date="recent", timezone="UTC", end_date=None, in_json=False):
        """
        Get private messages from a specified user.
        :param id_or_email: ID or email
        :param max_results: The maximum number of messages to return: 0 - 1000
        :param reverse: Reverse the output such that the oldest message is first - True or False
        :param start_index: The offset for the messages to return. Only valid with a non-recent data query.
        :param include_deleted: Include records about deleted messages into results (body of a message isn't returned).
        :param date: Either the latest date to fetch history for in ISO-8601 format, or 'recent' to fetch the latest 75 messages
        :param timezone: Your timezone. Must be a supported timezone.
        :param end_date: Either the earliest date to fetch history for in ISO-8601 format, or 'null' to disable this filter
        :param in_json: Gets messages as JSON if True
        :return: A list of all messages or an array of JSON objects
        """

        url = "/v2/room/{}/history".format(id_or_email)
        data = {"max-results":max_results, "reverse":reverse, "start-index":start_index, "include_deleted":include_deleted, "date":date, "timezone":timezone}
        if end_date != None:  data["end-date"] = end_date
        try:
            messages = json.loads(self.get(url, params=data).text)
            print messages
            messages["items"]
            if in_json:
                return messages
            all_messages = ""
            for message in messages:
                all_messages += "============================================================================================================\n"
                all_messages += " => {0} - {1} - {2}\n".format(message["from"]["name"].encode("utf-8"), message["id"], message["date"])
                all_messages += "============================================================================================================\n"
                all_messages += "{}\n".format(message["message"].encode("utf-8"))
                all_messages += "============================================================================================================\n\n"
            return all_messages
        except KeyError, e:
            try:
                errors = messages["error"]["message"]
                return errors
            except KeyError:
                return "KeyError: {}".format(e)

    def send_notification(self, room_id, **kwargs):
        """
        Send room notification.
        :param room_id: Room ID or name
        :param kwargs: Keyword arguments
        :return: Request response
        """
        url = '/v2/room/{!s}/notification'.format(room_id)
        return self.post(url, data=json.dumps(kwargs))

    def modify_user(self, name, show, mention_name, email, roles=None, title=None, presence=None, status=None, is_group_admin=None, timezone=None, password=None):

        url = "/v2/user/{}".format(email)
        data = {"name":name, "show":show, "mention_name":mention_name, "email":email}
        if roles != None:   data["roles"] = roles
        if title != None:   data["title"] = title
        if presence != None:   data["presence"] = presence
        if status != None:   data["status"] = status
        if is_group_admin != None:   data["is_group_admin"] = is_group_admin
        if timezone != None:   data["timezone"] = timezone
        if password != None:   data["password"] = password
        return self.put(url, data=json.dumps(data))

    def get_users(self, start_index=0, max_results=100, include_guests=False, include_deleted=False):
        """
        Get all users.
        :param start_index: The start index for the result set
        :param max_results: The maximum number of results.
        :param include_guests: Include active guest users in response. Otherwise, no guest users will be included.
        :param include_deleted: Include deleted users in response
        :return: A list of all users
        """

        try:
            float(start_index)
        except ValueError, e:
            return "ValueError: 'start_index' needs to be an integer"
        try:
            float(max_results)
        except ValueError, e:
            return "ValueError: 'max_results' needs to be an integer between 0 - 1000"
        if max_results <= 0 and max_results >=1000:
            return "Out of Range: 'max_results' needs to be an integer between 0 - 1000"

        query_parameters = {"start-index":start_index, "max-results":max_results, "include-guests":include_guests, "include-deleted":include_deleted}
        try:
            user_list = json.loads(self.get("/v2/user", params=query_parameters).text)["items"]
            all_users = ""
            for user in user_list:
                all_users += "===========================\n"
                for key in user:
                    all_users += "{0} - {1}\n".format(key, user[key])
                all_users += "===========================\n\n"
            return all_users
        except KeyError, e:
            return "KeyError: {}".format(json.loads(self.get("/v2/user", params=query_parameters).text))

    def get_user(self, id_or_email):
        """
        Get a specific user by id, email or mention name.
        :param id_or_email: The id, email address, or mention name (beginning with an '@') of the user to view.
        :return: Request response
        """

        url = "/v2/user/{}".format(id_or_email)
        return self.get(url)

    def get_rooms_by_user(self, id_or_email, start_index=0, max_results=100):

        query_parameters = {"start-index":start_index, "max-results":max_results}
        url="/v2/user/{}/preference/auto-join".format(id_or_email)
        return self.get(url, params=query_parameters)

    def send_private_message(self, id_or_email, message, notify=True, message_format="text"):
        """
        Send private message to a specified user.
        :param id_or_email: ID or email
        :param message: The message body, Valid length range: 1 - 10000
        :param notify: Whether this message should trigger a notification
        :param message_format: Determines how the message is treated by our server and rendered insde HipChat application, html or text
        :return: Request response
        """

        url = "/v2/user/{}/message".format(id_or_email)
        data = {"message":message, "notify":notify, "message_format":message_format}
        return self.post(url, data=json.dumps(data))

    def get_private_messages(self, id_or_email, max_results=75, reverse=True, start_index=0, include_deleted=True, date="recent", timezone="UTC", end_date=None, in_json=False):
        """
        Get private messages from a specified user.
        :param id_or_email: ID or email
        :param max_results: The maximum number of messages to return: 0 - 1000
        :param reverse: Reverse the output such that the oldest message is first - True or False
        :param start_index: The offset for the messages to return. Only valid with a non-recent data query.
        :param include_deleted: Include records about deleted messages into results (body of a message isn't returned).
        :param date: Either the latest date to fetch history for in ISO-8601 format, or 'recent' to fetch the latest 75 messages
        :param timezone: Your timezone. Must be a supported timezone.
        :param end_date: Either the earliest date to fetch history for in ISO-8601 format, or 'null' to disable this filter
        :param in_json: Gets messages as JSON if True
        :return: A list of all messages or an array of JSON objects
        """

        url = "/v2/user/{}/history".format(id_or_email)
        data = {"max-results":max_results, "reverse":reverse, "start-index":start_index, "include_deleted":include_deleted, "date":date, "timezone":timezone}
        if end_date != None:  data["end-date"] = end_date
        try:
            messages = json.loads(self.get(url, params=data).text)["items"]
            if in_json:
                return messages
            all_messages = ""
            for message in messages:
                all_messages += "============================================================================================================\n"
                all_messages += " => {0} - {1} - {2}\n".format(message["from"]["name"].encode("utf-8"), message["id"], message["date"])
                all_messages += "============================================================================================================\n"
                all_messages += "{}\n".format(message["message"].encode("utf-8"))
                all_messages += "============================================================================================================\n\n"
            return all_messages
        except KeyError, e:
            return "KeyError: {}".format(e)

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

