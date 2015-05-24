import json
import socket
from threading import Thread
from codebase.common.member import Member


class Client(Thread):
    def __init__(self, *args, **kwargs):
        host, port = "localhost", 9999
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.members = {}
        self.recv = None
        self.__set_member(kwargs['username'])
        super(Client, self).__init__(*args, **kwargs)

    def __set_member(self, username, public_key=None):
        member = Member()
        member.username = username
        member.public_key = public_key
        self.members[username] = member

    def add_member(self, data):
        new_user = data['username']
        public_key = data['public_key']
        self.__set_member(new_user, public_key)

    def send(self, message, to):
        message = Client.format_message(message)
        self.sock.send(message)

    def run(self):
        while 1:
            try:
                data = self.sock.recv(1024)
                self.recv = str(data)
                print("Got data: ", data)
            except socket.timeout:
                continue
            except:
                break
        self.sock.close()

    @staticmethod
    def format_message(message):
        data = json.dumps({
            'message': message,
            'username': 'ivan',
            'to': 'broadcast'
        })
        message = bytes(data, "utf-8")
        return message
