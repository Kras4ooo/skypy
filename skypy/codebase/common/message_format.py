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
    def register_user_client(data):
        data = json.dumps({
            'first_name': data['first_name'],
            'username': data['username'],
            'password': data['password'],
            'public_key': data['public_key'],
            'to': 'register_user'
        })
        data = bytes(data, 'utf-8')
        return data

    @staticmethod
    def login_user_client(data):
        data = json.dumps({
            'username': data['username'],
            'password': data['password'],
            'to': 'login_user'
        })
        data = bytes(data, 'utf-8')
        return data

    @staticmethod
    def to_all_client(username, message):
        data = {
            'username': username,
            'message': message,
            'to': 'broadcast'
        }
        return data

    @staticmethod
    def to_user_client(username, message, to_user):
        data = {
            'username': username,
            'message': message,
            'to': 'to_user',
            'to_user': to_user
        }
        return data

    @staticmethod
    def to_user_send_file_client(username, file_bytes,
                                 to_user, file_extension,
                                 is_ready):
        data = {
            'username': username,
            'message': file_bytes,
            'to': 'to_user',
            'to_user': to_user,
            'is_ready': is_ready,
            'ext': file_extension
        }
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
            'initialize': True,
            'ask': True,
            'user': username,
            'pub_key': public_key
        }
        return data

    @staticmethod
    def register_user_server(is_success):
        data = {
            'is_success': is_success
        }
        return data

    @staticmethod
    def login_user_server(is_correct):
        data = {
            'is_correct': is_correct
        }
        return data

    @staticmethod
    def delete_user_server(username):
        data = {
            'delete_user_name': username
        }
        return data
