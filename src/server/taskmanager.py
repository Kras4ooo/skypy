from src.server.taskexecutor import TaskExecutor
from src.utils.crypto import Crypto
import json


class TaskManager:
    def __init__(self, **kwargs):
        self.data = None
        self.crypto = Crypto()
        self.task_executor = TaskExecutor()
        self.kwargs = kwargs

    def create_task(self, data):
        self.data = self.crypto.decode(data)
        self.data = json.loads(self.data)
        self.task_executor.execute(self.data, self.kwargs)
