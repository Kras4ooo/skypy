import json


class MessageFormat:
    @staticmethod
    def initialize_message_client(username, pub_key):
        data = json.dumps({
            'public_key': pub_key,
            'username': username,
            'to': 'initialize'
        })
        data = bytes(data, 'utf-8')
        return data

    @staticmethod
    def initialize_ask_message_client(username, to_user, pub_key):
        data = json.dumps({
            'public_key': pub_key,
            'to_user': to_user,
            'username': username,
            'to': 'initialize_ask_key'
        })
        data = bytes(data, 'utf-8')
        return data

    @staticmethod
    def initialize_message_server(username, public_key):
        data = {
            'initialize': True,
            'pub_key': public_key,
            'from_user': username
        }
        return data

    @staticmethod
    def initialize_ask_message_server(username, public_key):
        data = {
            "initialize": True,
            "ask": True,
            'user': username,
            'pub_key': public_key
        }
        return data
