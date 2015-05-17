import socketserver
import errno
from codebase.server.taskmanager import TaskManager


class SkyPyServer(socketserver.BaseRequestHandler):
    members = []

    def handle(self):
        client_data = self.__get_client_data()
        task_manager = TaskManager(client_data)
        self.__add_member()
        while True:
            data = self.receive_data()
            if not data:
                print("Remove")
                self.__remove_member()
                return
            task_manager.create_task(data)

    def __get_client_data(self):
        return {
            'request': self.request,
            'client': self.client_address,
            'members': self.members
        }

    def __add_member(self):
        self.members.append({
            'request': self.request,
            'client': self.client_address
        })

    def __remove_member(self):
        for counter, member in enumerate(self.members[:]):
            if member.get('client') == self.client_address:
                self.members.remove(self.members[counter])

    def receive_data(self):
        try:
            data = self.request.recv(1024)
        except OSError as ex:
            if ex.errno == errno.ECONNRESET:
                self.__remove_member()
                return b''
            raise
        return data
