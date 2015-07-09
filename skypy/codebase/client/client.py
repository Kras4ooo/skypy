import random
import string
from PyQt5 import QtCore
import os
import json
import socket
from threading import Thread
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QFont, QIcon

from PyQt5.QtWidgets import QListWidgetItem
import struct
import errno
from codebase.common.member import Member
from codebase.common.message_format import MessageFormat
from codebase.utils.cryptodata import CryptoData


class Client(QtCore.QThread):
    HOST, PORT = "localhost", 9999
    WINDOW = None
    add_tab_signal = QtCore.pyqtSignal(str)
    USERNAME_FILES = {}

    def __init__(self, *args, **kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        self.members = {}
        self.username = None

        self.__set_my_member(kwargs['username'])
        self.__initialize_member()
        super(Client, self).__init__(kwargs['parent'])

    def __initialize_member(self):
        pub_key = self.members[self.username].public_key
        encode_pub_key = CryptoData.encode_base64(pub_key)

        data = MessageFormat.initialize_message_client(
            self.username,
            encode_pub_key
        )
        data = Client.format_message_encode(data)
        self.sock.sendall(data)

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
                data = Client.format_message_encode(data)
                self.sock.sendall(data)
                return
            from_user = data['from_user']
            pub_key = CryptoData.decode_base64(data['pub_key'])
            self.__set_member(from_user, pub_key)
            self.__append_to_user_list(self.members[from_user])

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
        data = Client.format_message_encode(message)
        sock.sendall(data)
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
        data = Client.format_message_encode(message)

        sock.sendall(data)
        return sock

    @staticmethod
    def check_text(message):
        if message.find('(!python)') != -1:
            return True
        return False

    def add_member(self, data):
        new_user = data['username']
        public_key = data['public_key']
        self.__set_member(new_user, public_key)

    def __append_to_user_list(self, member):
        item = QStandardItem(member.username)
        self.WINDOW.model.appendRow(item)
        self.WINDOW.list_view.setModel(self.WINDOW.model)

    def __delete_user(self, data):
        delete_username = data['delete_user_name']
        member = Member.find_member_dict(delete_username, self.members)
        if member in self.members:
            del self.members[member]
            list_model = self.WINDOW.list_view.model()
            item = list_model.findItems(delete_username, Qt.MatchExactly)
            index = item[0].index().row()
            self.WINDOW.list_view.model().removeRow(index)

    def __receive_file(self, data):
        if data['is_ready'] is False:
            if data['type'] not in self.USERNAME_FILES:
                self.__set_file_text(data)
                desktop_file = os.path.expanduser("~/Desktop/")
                filename_path = self.__create_media_folder(desktop_file)
                filename = self.__create_file(filename_path, data)
                self.USERNAME_FILES[data['type']] = {}
                self.USERNAME_FILES[data['type']]['file_name'] = filename
            path = self.USERNAME_FILES[data['type']]['file_name']
            with open(path, 'ab') as f:
                f.write(data['message'])
            return
        path = self.USERNAME_FILES[data['type']]['file_name']
        self.__set_text_after_save_file(data, path)
        del self.USERNAME_FILES[data['type']]

    def __set_file_text(self, data):
        tab = self.set_data_to_correct_tab(data['type'])
        font = QFont()
        font.setStyle(QFont.StyleItalic)
        item = QListWidgetItem(tab.children()[0])
        item.setFont(font)
        item.setText("%s: Send file" % self.members[data['username']].username)

    def __set_text_after_save_file(self, data, path):
        tab = self.set_data_to_correct_tab(data['type'])
        font = QFont()
        font.setWeight(QFont.Bold)
        item = QListWidgetItem(tab.children()[0])
        item.setFont(font)
        message = "the file was saved on the following path: %s" % path
        item.setText("%s: %s" % (self.members[data['username']].username,
                                 message))

    def __create_media_folder(self, path):
        directory_name = "skypy-media/"
        path += directory_name
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                return path
            return path
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def __create_file(self, path, data):
        chars = string.ascii_uppercase + string.digits
        size = 6
        random_string = ''.join(random.choice(chars) for _ in range(size))
        filename = data['type'] + '_' + random_string + data['ext']
        path += filename
        return path

    def receive_message(self, data):
        member = self.members[self.username]
        data = json.loads(data)
        if 'initialize' in data:
            self.__initialize_messages(data)
            return True  # Initialize Member
        if 'is_ready' in data:
            decrypt_data = CryptoData.decode(data, member.private_key)
            decrypt_data['message'] = decrypt_data['message']
            self.__receive_file(decrypt_data)
            return True
        if 'delete_user_name' in data:
            self.__delete_user(data)
            return True  # Delete Member
        if 'error' in data:
            print(data)
            return True
        decrypt_data = CryptoData.decode(data, member.private_key)
        decrypt_data['message'] = decrypt_data['message'].decode('utf-8')
        return decrypt_data

    def receive(self):
        try:
            size = struct.unpack("i", self.sock.recv(struct.calcsize("i")))
            data = ""
            while len(data) < size[0]:
                msg = self.sock.recv(size[0] - len(data))
                if not msg:
                    return None
                data += msg.decode('utf-8')
        except OSError as e:
            return False
        return data

    def run(self):
        while True:
            try:
                data = self.receive()
                data = self.receive_message(data)
                print("Got data: ", data)
                if data is True:
                    continue
                tab = self.set_data_to_correct_tab(data['type'])
                item = QListWidgetItem(tab.children()[0])
                message = str(data['message'])
                check_for_icon = Client.check_text(message)
                item.setText("%s: %s" % (self.members[data['username']].username, message))
                if check_for_icon is True:
                    path = os.path.dirname(os.path.abspath(__file__))
                    item.setIcon(QIcon(path + "/pictures/python.jpg"))
            except socket.timeout:
                continue
        self.sock.close()

    def format_message(self, data, is_file=False):
        data = self.encode_message(data, is_file)
        message = bytes(json.dumps(data), "utf-8")
        return message

    def add_tab(self, username, is_set=True):
        self.add_tab_signal.emit(username)
        return is_set

    def set_data_to_correct_tab(self, username, is_set=False):
        count_tabs = self.WINDOW.tab_widget.count()
        for count in range(count_tabs):
            tab = self.WINDOW.tab_widget.widget(count)
            if tab.objectName() == username:
                return tab
        if is_set is False:
            is_set = self.add_tab(username)
        return self.set_data_to_correct_tab(username, is_set)

    @staticmethod
    def format_message_encode(message):
        message = struct.pack("i", len(message)) + message
        return message

    def encode_message(self, data, is_file=False):
        data['message_settings'] = {'message': data['message']}
        del data['message']
        pub_key = self.members[self.username].public_key
        message_settings = data['message_settings']
        data['message_settings'] = CryptoData.encode(message_settings, pub_key)
        data['message_settings']['username'] = data['username']
        if data['to'] == 'broadcast':
            data['message_settings']['type'] = 'broadcast'
        elif is_file:
            data['message_settings']['type'] = data['username']
            data['message_settings']['is_ready'] = data['is_ready']
            data['message_settings']['ext'] = data['ext']
        else:
            data['message_settings']['type'] = data['username']
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

    def send(self, message, tab, is_file=False):
        tab_text = tab.objectName()
        if tab_text == 'broadcast':
            self.send_to_all(message)
        elif is_file is True:
            self.send_file(message, tab_text)
        else:
            self.send_to_user(message, tab_text)

    def send_to_user(self, message, to):
        message = MessageFormat.to_user_client(self.username, message, to)
        message = self.format_message(message)
        data = Client.format_message_encode(message)
        self.sock.sendall(data)

    def send_to_all(self, message):
        message = MessageFormat.to_all_client(self.username, message)
        message = self.format_message(message)
        data = Client.format_message_encode(message)
        self.sock.sendall(data)

    def send_file(self, file, to):
        SendFile.file = file
        SendFile.to = to
        SendFile.client = self
        SendFile().start()

class SendFile(Thread):
    file = None
    to = None
    client = None

    def __init__(self, *args, **kwargs):
        super(SendFile, self).__init__(*args, kwargs=kwargs)

    def run(self):
        _, file_extension = os.path.splitext(self.file[0])
        f = open(self.file[0], 'rb')
        length = f.read(10024)
        while length:
            message = MessageFormat.to_user_send_file_client(self.client.username,
                                                             length,
                                                             self.to,
                                                             file_extension,
                                                             False)
            message = self.client.format_message(message, True)
            data = Client.format_message_encode(message)
            self.client.sock.sendall(data)
            length = f.read(10024)
        message = MessageFormat.to_user_send_file_client(self.client.username,
                                                         "fin",
                                                         self.to,
                                                         file_extension,
                                                         True)
        f.close()
        message = self.client.format_message(message, True)
        data = Client.format_message_encode(message)
        self.client.sock.sendall(data)
