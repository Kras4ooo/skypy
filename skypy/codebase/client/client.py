import os
import json
import socket
from threading import Thread

from PyQt5.QtWidgets import QListWidgetItem
from codebase.common.member import Member
from codebase.utils.cryptodata import CryptoData


class Client(Thread):
    def __init__(self, *args, **kwargs):
        host, port = "localhost", 9999
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.members = {}
        self.window = kwargs['window']
        self.username = None

        self.__set_my_member(kwargs['username'])
        super(Client, self).__init__(*args, kwargs=kwargs)

    def __set_my_member(self, username):
        self.username = username
        member = Member()
        member.username = username

        public_key, private_key = self.__get_or_generate_key()
        member.public_key = public_key
        member.private_key = private_key
        self.members[username] = member

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
        message = self.format_message(message)
        self.sock.send(message)

    def receive_message(self, data):
        data = data.decode('utf-8')
        member = self.members[self.username]
        decrypt_data = CryptoData.decode(data, member.private_key)
        return decrypt_data

    def run(self):
        while True:
            try:
                data = self.sock.recv(1024)
                print("Got data: ", data)
                item = QListWidgetItem(self.window.listWidget)
                item.setText(str(data))
            except socket.timeout:
                continue
            except Exception as ex:
                print(ex)
                break
        self.sock.close()

    def format_message(self, message):
        data = {
            'message': message,
            'username': 'ivan',
            'to': 'broadcast'
        }
        data = self.encode_message(data)
        message = bytes(json.dumps(data), "utf-8")
        return message

    def encode_message(self, data):
        data['message_settings'] = {'message': data['message']}
        del data['message']
        pub_key = self.members[self.username].public_key
        message_settings = data['message_settings']
        data['message_settings'] = CryptoData.encode(message_settings, pub_key)
        return data

    def __get_or_generate_key(self):
        path_dir = os.path.isdir("keys")
        if path_dir:
            private_key_path = os.path.isfile('keys/private.pem')
            public_key_path = os.path.isfile('keys/public.pub')
            if private_key_path and public_key_path:
                with open('keys/private.pem', 'rb') as private_file:
                    private_key = private_file.read()
                with open('keys/public.pub', 'rb') as public_file:
                    public_key = public_file.read()
            else:
                private_key, public_key = self.__generate_keys()
        else:
            private_key, public_key = self.__generate_keys()
        return private_key, public_key

    def __generate_keys(self):
        private_key, public_key = CryptoData.generate_keys()
        os.mkdir("keys")
        private_file = open('keys/private.pem', 'wb')
        public_file = open('keys/public.pub', 'wb')
        private_file.write(private_key.exportKey())
        public_file.write(public_key.exportKey())

        return private_key.exportKey(), public_key.exportKey()
