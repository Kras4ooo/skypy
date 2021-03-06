import json
import socket
import struct

from codebase.common.member import Member
from codebase.common.message_format import MessageFormat
from codebase.common.room import Room
from codebase.server.db.models import User


class TaskExecutor:
    """
    TaskExecutor takes care that send and forward
    files/messages to the right people/groups.
    """
    def __init__(self):
        self.client_data = None

    def execute(self, data, client_data):
        """
        The method takes care that the data to be forwarded to the parser,
        processed and sent to carry out the necessary functionality

        @type data: dict
        @param data: dictionary data to whom and what should be sent
        @type client_data: dict
        @param client_data: dictionary of customer data sender
        """
        self.client_data = client_data
        self.analyze_input(data)

    def analyze_input(self, data):
        """
        Analyze the data sent from the socket
        and by referring to the correct method for processing.

        @type data: dict
        @param data: data for analysis
        """
        try:
            if 'room' in data:
                getattr(self, data['room']['option']['action'])(data)
            else:
                getattr(self, data['to'])(data)
        except AttributeError as attr_err:
            # TODO REMOVE print(attr_err)
            message = {"error": "AttributeError"}
            message = TaskExecutor.encode_message(message)
            self.client_data['request'].sendall(message)
            # TODO: Send to Sentry
        except socket.error:
            message = {"error": "socket.error"}
            message = TaskExecutor.encode_message(message)
            self.client_data['request'].sendall(message)

    @staticmethod
    def encode_message(message):
        """
        Coded message to byte code

        @type message: dict
        @param message: message
        """
        message = bytes(json.dumps(message), 'utf-8')
        message = struct.pack("i", len(message)) + message
        return message

    def sendall(self, client, message):
        if self.__ignore_sender_user(client):
            client.request.sendall(message)

    def delete_user(self):
        user = User()
        delete_user = self.client_data['client'].username
        user.set_logout(delete_user)
        message = MessageFormat.delete_user_server(delete_user)
        message = TaskExecutor.encode_message(message)
        for member in self.client_data['members']:
            self.sendall(member, message)

    def register_user(self, data):
        user = User()
        response = user.register_user(data)
        message = MessageFormat.register_user_server(response)
        message = TaskExecutor.encode_message(message)
        self.client_data['request'].sendall(message)

    def login_user(self, data):
        user = User()
        response = user.login_user(data)
        message = MessageFormat.login_user_server(response)
        message = TaskExecutor.encode_message(message)
        self.client_data['request'].sendall(message)

    def initialize(self, data):
        """
        At the beginning of each user sends its public key to all the others
        and wants accordingly and their public keys.

        @type data: dict
        @param data: data which contains public key
        """
        public_key = data['public_key']
        username = self.client_data['client'].username
        self.client_data['client'].activated = True
        data = {'username': username, 'public_key': public_key}

        message = MessageFormat.initialize_message_server(**data)
        ask_public_key = MessageFormat.initialize_ask_message_server(**data)

        message = TaskExecutor.encode_message(message)
        ask_public_key = TaskExecutor.encode_message(ask_public_key)

        for member in self.client_data['members']:
            self.sendall(member, message)
            self.sendall(member, ask_public_key)

    def initialize_ask_key(self, data):
        members = self.client_data['members']
        member = Member.find_member(data['to_user'], members)
        send_message = MessageFormat.initialize_message_server(
            self.client_data['client'].username,
            data['public_key']
        )
        message = TaskExecutor.encode_message(send_message)
        member.request.sendall(message)

    def broadcast(self, data):
        """
        The method takes care to send a message to all participants in the chat

        @type data: dict
        @param data: dictionary containing the message that will be sent
        to all participants in the chat.
        """
        message = TaskExecutor.encode_message(data['message_settings'])
        for member in self.client_data['members']:
            self.sendall(member, message)

    def to_user(self, data):
        """
        The method takes care to send a message to the particular user
        in the chat

        @type data: dict
        @param data: dictionary containing the message that will be sent
        to the particular user.
        """
        members = self.client_data['members']
        to_member = Member.find_member(data['to_user'], members)
        message = TaskExecutor.encode_message(data['message_settings'])
        to_member.request.sendall(message)

    # Rooms options
    def __create_room(self, room_option, message):
        """
        Method takes care that create room

        @type room_option: dict
        @param room_option: meta data to create the room
        @type message: bytes
        @param message: the message which will be sent
        """
        room = Room()
        room.room_id = room_option['uid']
        room.members.append(self.client_data['client'])
        self.client_data['rooms'][room_option['uid']] = room
        self.client_data['client'].request.sendall(message)

    def create_room(self, data):
        """
        Method takes care to create room if it does not exist
        and to send the message to all participants in the room.

        @type data: dict
        @param data: It contains data for the room
        """
        room_option = data['room']['option']
        rooms = self.client_data['rooms']
        if Room.check_is_exist_room(room_option['uid'], rooms):
            message = TaskExecutor.encode_message("exist room")
            self.client_data['client'].request.sendall(message)
        else:
            message = TaskExecutor.encode_message("Yes")
            self.__create_room(room_option, message)

    def add_member_to_room(self, data):
        """
        Method takes care to add a member to a group

        @type data: dict
        @param data: It contains data room
        """
        room_option = data['room']['option']
        rooms = self.client_data['rooms']
        message = TaskExecutor.encode_message("True")
        if Room.check_is_exist_room(room_option['uid'], rooms):
            current_room = self.client_data['rooms'][room_option['uid']]
            current_room.members.append(self.client_data['client'])
            self.client_data['client'].request.sendall(message)
        else:
            self.__create_room(room_option, message)

    def to_room_message(self, data):
        """
        Sends a message to an existing group

        @type data: dict
        @param data: It contains data for the room and message
        """
        room_option = data['room']['option']
        message = TaskExecutor.encode_message(data['message'])
        current_room = self.client_data['rooms'][room_option['uid']]
        for member in current_room.members:
            member.request.sendall(message)

    def __ignore_sender_user(self, member):
        if (member.request != self.client_data['request']
            or member.activated is False):
            return True
        return False
