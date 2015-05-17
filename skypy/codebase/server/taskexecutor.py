from codebase.common.member import Member


class TaskExecutor:
    def __init__(self):
        self.client_data = None

    def execute(self, data, client_data):
        self.client_data = client_data
        self.analyze_input(data)

    def analyze_input(self, data):
        try:
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

    def broadcast(self, data):
        message = data['message']
        for member in self.client_data['members']:
            member.request.sendall(bytes(message, 'utf-8'))

    def to_user(self, data):
        members = self.client_data['members']
        to_member = Member.find_member(data['to_user'], members)
        message = data['message']

        to_member.request.sendall(bytes(message, 'utf-8'))
        self.client_data['client'].request.sendall(bytes(message, 'utf-8'))

