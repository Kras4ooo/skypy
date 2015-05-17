import socketserver
from codebase.server.taskmanager import TaskManager


class SkyPyServer(socketserver.BaseRequestHandler):
    members = []

    def handle(self):
        client_data = {
            'request': self.request,
            'client': self.client_address,
            'members': self.members
        }
        task_manager = TaskManager(client_data)
        self.members.append((self.request, self.client_address))
        while True:
            data = self.request.recv(1024)
            if not data:
                self.members.remove(self.client_address)
                return
            task_manager.create_task(data)
