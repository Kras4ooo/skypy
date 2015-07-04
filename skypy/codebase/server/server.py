import socketserver
import errno
import struct
from codebase.common.member import Member
from codebase.server.taskmanager import TaskManager


class SkyPyServer(socketserver.BaseRequestHandler):
    members = []
    rooms = {}

    def __init__(self, *args, **kwargs):
        self.member = None
        super().__init__(*args, **kwargs)

    def handle(self):
        self.__set_member()
        # TODO: Remove print(self.members)
        client_data = self.__get_client_data()
        task_manager = TaskManager(client_data)
        while True:
            data = self.__receive_data()
            if not data:
                # TODO: Remove print("Remove")
                task_manager.delete_user_task()
                self.__remove_member()
                return
            task_manager.create_task(data)

    def __set_member(self):
        member = Member()
        member.client_address = self.client_address
        member.request = self.request

        self.member = member
        self.members.append(member)

    def __receive(self):
        try:
            size = struct.unpack("i", self.request.recv(struct.calcsize("i")))
            data = ""
            while len(data) < size[0]:
                msg = self.request.recv(size[0] - len(data))
                if not msg:
                    return None
                data += msg.decode('utf-8')
        except OSError as e:
            return False
        return data

    def __receive_data(self):
        try:
            data = self.__receive()
        except OSError as ex:
            if ex.errno == errno.ECONNRESET:
                self.__remove_member()
                return b''
            raise
        return data

    def __get_client_data(self):
        return {
            'request': self.request,
            'client': self.member,
            'members': self.members,
            'rooms': self.rooms
        }

    def __remove_member(self):
        for counter, member in enumerate(self.members[:]):
            if member.client_address == self.client_address:
                self.members.remove(self.members[counter])
