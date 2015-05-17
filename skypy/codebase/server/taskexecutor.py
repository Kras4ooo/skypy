class TaskExecutor:
    def __init__(self):
        self.client_data = None

    def execute(self, data, client_data):
        self.client_data = client_data
        self.analyze_input(data)

    def analyze_input(self, data):
        try:
            getattr(self, data['to'])(data['message'])
        except AttributeError as attr_err:
            print(attr_err)
            # TODO: Send to Sentry

    def broadcast_message(self, message):
        for member in self.client_data['members']:
            member['request'].sendall(bytes(message, 'utf-8'))
