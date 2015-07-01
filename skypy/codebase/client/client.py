import os
import json
import socket
from threading import Thread
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtWidgets import QListWidgetItem
from codebase.common.member import Member
from codebase.common.message_format import MessageFormat
from codebase.utils.cryptodata import CryptoData


class Client(Thread):
    HOST, PORT = "localhost", 9999
    WINDOW = None

    def __init__(self, *args, **kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        self.members = {}
        self.username = None

        self.__set_my_member(kwargs['username'])
        self.__initialize_member()
        super(Client, self).__init__(*args, kwargs=kwargs)

    def __initialize_member(self):
        pub_key = self.members[self.username].public_key
        encode_pub_key = CryptoData.encode_base64(pub_key)

        data = MessageFormat.initialize_message_client(
            self.username,
            encode_pub_key
        )
        self.sock.sendall(data)

    def __set_my_member(self, username):
        self.username = username
        member = Member()
        member.username = username

        private_key, public_key = Client.get_or_generate_key()
        member.public_key = public_key
        member.private_key = private_key
        self.members[username] = member

    def __set_member(self, username, public_key=None):
        member = Member()
        member.username = username
        member.public_key = public_key
        self.members[username] = member

    @staticmethod
    def register_user(data):
        data['password'] = CryptoData.encode_only_rsa(
            data['password'],
            data['public_key']
        )
        message = MessageFormat.register_user_client(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Client.HOST, Client.PORT))
        sock.sendall(message)
        return sock

    @staticmethod
    def login_user(data):
        data['password'] = CryptoData.encode_only_rsa(
            data['password'],
            data['public_key']
        )
        message = MessageFormat.login_user_client(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Client.HOST, Client.PORT))
        sock.sendall(message)
        return sock

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
        data = json.loads(data)
        if 'initialize' in data:
            self.__initialize_messages(data)
            return True  # Initialize Member
        decrypt_data = CryptoData.decode(data, member.private_key)
        message = decrypt_data['message'].decode('utf-8')
        return message

    def __append_to_user_list(self, member):
        item = QStandardItem(member.username)
        self.WINDOW.model.appendRow(item)
        self.WINDOW.list_view.setModel(self.WINDOW.model)

    def __initialize_messages(self, data):
        if data['initialize']:
            if 'ask' in data:
                pub_key = self.members[self.username].public_key
                encode_pub_key = CryptoData.encode_base64(pub_key)

                data = MessageFormat.initialize_ask_message_client(
                    self.members[self.username].username,
                    data['user'],
                    encode_pub_key
                )
                self.sock.sendall(data)
                return
            from_user = data['from_user']
            pub_key = CryptoData.decode_base64(data['pub_key'])
            self.__set_member(from_user, pub_key)
            self.__append_to_user_list(self.members[from_user])

    def run(self):
        while True:
            try:
                data = self.sock.recv(1024)
                data = self.receive_message(data)
                print("Got data: ", data)
                if data is True:
                    continue
                item = QListWidgetItem(self.WINDOW.listWidget)
                item.setText(str(data))
            except socket.timeout:
                continue
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

    @staticmethod
    def get_or_generate_key():
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
                private_key, public_key = Client.generate_keys()
        else:
            private_key, public_key = Client.generate_keys()
        return private_key, public_key

    @staticmethod
    def generate_keys():
        private_key, public_key = CryptoData.generate_keys()
        os.mkdir("keys")
        private_file = open('keys/private.pem', 'wb')
        public_file = open('keys/public.pub', 'wb')
        private_file.write(private_key.exportKey())
        public_file.write(public_key.exportKey())

        return private_key.exportKey(), public_key.exportKey()
