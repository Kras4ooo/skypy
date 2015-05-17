import json
from codebase.server.taskexecutor import TaskExecutor
from codebase.utils.crypto import Crypto


class TaskManager:
    def __init__(self, client_data):
        self.data = None
        self.crypto = Crypto()
        self.task_executor = TaskExecutor()
        self.client_data = client_data

    def create_task(self, data):
        # self.data = self.crypto.decode(data)
        # TODO: Change this line
        self.data = data.decode('utf-8')
        self.data = json.loads(self.data)
        self.task_executor.execute(self.data, self.client_data)
