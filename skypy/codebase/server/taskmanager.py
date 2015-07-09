import json
from codebase.server.taskexecutor import TaskExecutor
from codebase.utils.cryptodata import CryptoData


class TaskManager:
    """
    This class serves as a traffic cop.
    It sends the tasks to be performed on TaskExecutor and cares to know
    if you get an exception it to be handled properly
    and can be logged and forwarded for analysis.
    """
    def __init__(self, client_data):
        self.data = None
        self.crypto = CryptoData()
        self.task_executor = TaskExecutor()
        self.client_data = client_data

    def create_task(self, data):
        """
        Create task

        @type data: byte
        @param data: data for task
        """
        self.data = json.loads(data)
        self.client_data['client'].username = self.data['username']
        self.task_executor.execute(self.data, self.client_data)

    def delete_user_task(self):
        """
        Delete User
        """
        self.task_executor.delete_user()

    def fail_task(self):
        pass

    def pending_task(self):
        pass

    def log_task(self):
        pass

    def send_failed_task(self):
        pass
