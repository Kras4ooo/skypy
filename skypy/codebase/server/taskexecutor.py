from codebase.common.member import Member
from codebase.common.room import Room


class TaskExecutor:
    def __init__(self):
        self.client_data = None

    def execute(self, data, client_data):
        self.client_data = client_data
        self.analyze_input(data)

    def analyze_input(self, data):
        try:
            if 'room' in data:
                getattr(self, data['room']['option']['action'])(data)
            else:
                getattr(self, data['to'])(data)
        except AttributeError:
            try:
                getattr(self, data['to'])()
            except AttributeError as attr_err:
                print(attr_err)
                # TODO: Send to Sentry

    def initialize(self):
        # TODO: Return may be response to user for (ok message)
        return True

    @staticmethod
    def encode_message(message):
        return bytes(message, 'utf-8')

    def broadcast(self, data):
        message = TaskExecutor.encode_message(data['message'])
        for member in self.client_data['members']:
            member.request.sendall(message)

    def to_user(self, data):
        members = self.client_data['members']
        to_member = Member.find_member(data['to_user'], members)
        message = TaskExecutor.encode_message(data['message'])

        to_member.request.sendall(message)
        self.client_data['client'].request.sendall()

    # Rooms options
    def __create_room(self, room_option, message):
        room = Room()
        room.room_id = room_option['uid']
        room.members.append(self.client_data['client'])
        self.client_data['rooms'][room_option['uid']] = room
        self.client_data['client'].request.sendall(message)

    def create_room(self, data):
        room_option = data['room']['option']
        rooms = self.client_data['rooms']
        if Room.check_is_exist_room(room_option['uid'], rooms):
            message = TaskExecutor.encode_message("exist room")
            self.client_data['client'].request.sendall(message)
        else:
            message = TaskExecutor.encode_message("Yes")
            self.__create_room(room_option, message)

    def add_member_to_room(self, data):
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
        room_option = data['room']['option']
        message = TaskExecutor.encode_message(data['message'])
        current_room = self.client_data['rooms'][room_option['uid']]
        for member in current_room.members:
            member.request.sendall(message)
