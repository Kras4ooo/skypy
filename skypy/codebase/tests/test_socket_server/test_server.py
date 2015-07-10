from errno import ECONNRESET
import json
import os
import random
import socket
import socketserver
import string
import threading
import unittest
import struct
from codebase.server.server import SkyPyServer
from codebase.utils.cryptodata import CryptoData


class TestSkyPyServer(unittest.TestCase):
    def setUp(self):
        self.host, self.port = "localhost", 9998
        sock = (self.host, self.port)
        self.server = socketserver.ThreadingTCPServer(sock, SkyPyServer)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(sock)

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def __encode_message(self, data):
        data['message_settings'] = {'message': data['message']}
        del data['message']
        pub_key = self.__get_pub_key().decode("utf-8")
        message_settings = data['message_settings']
        data['message_settings'] = CryptoData.encode(message_settings, pub_key)
        return data

    def __get_pub_key(self):
        pub_key = os.path.join(
            os.path.dirname(__file__),
            '..{0}test_keys{0}public.pub'.format(os.path.sep)
        )
        with open(pub_key, 'rb') as public_file:
            public_key = public_file.read()
        return public_key

    def __get_private_key(self):
        private_key = os.path.join(
            os.path.dirname(__file__),
            '..{0}test_keys{0}private.pem'.format(os.path.sep)
        )
        with open(private_key, 'rb') as private_file:
            private_key = private_file.read()
        return private_key

    def __receive_message(self, data):
        data = json.loads(data)
        private_key = self.__get_private_key().decode('utf-8')
        decrypt_data = CryptoData.decode(data, private_key)
        message = decrypt_data['message'].decode('utf-8')
        return message

    def __data_pack(self, message):
        message = struct.pack("i", len(message)) + message
        return message

    def __receive(self, cs):
        try:
            size = struct.unpack("i", cs.recv(struct.calcsize("i")))
            data = ""
            while len(data) < size[0]:
                msg = cs.recv(size[0] - len(data))
                if not msg:
                    return None
                data += msg.decode('utf-8')
        except OSError as e:
            print(e)
            return False
        return data

    def __generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def test_client_initialize(self):
        data = json.dumps({
            'public_key': 'test_key',
            'username': 'test',
            'to': 'initialize'
        })

        sock = (self.host, self.port)

        client_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_two.connect(sock)

        data_two = json.dumps({
            'public_key': 'test_key',
            'username': 'test',
            'to': 'initialize'
        })

        client_two.send(self.__data_pack(bytes(data_two, "utf-8")))
        self.client.send(self.__data_pack(bytes(data, "utf-8")))

        received = self.__receive(self.client)
        received = json.loads(received)
        client_two.close()

        self.assertEqual(received['pub_key'], "test_key")
        received = self.__receive(self.client)

    def test_not_exist_method(self):
        data = json.dumps({
            'username': 'test',
            'to': 'not_exist'
        })
        self.client.send(self.__data_pack(bytes(data, "utf-8")))

        received = self.__receive(self.client)
        received = json.loads(received)

        self.assertEqual(received['error'], "AttributeError")

    def test_register_user(self):
        data = json.dumps({
            'first_name': self.__generator(),
            'username': self.__generator(),
            'password': self.__generator(),
            'public_key': self.__generator(),
            'to': 'register_user'
        })
        self.client.send(self.__data_pack(bytes(data, "utf-8")))

        received = self.__receive(self.client)
        received = json.loads(received)
        self.assertTrue(received['is_success'])

    def test_login_user(self):
        data = json.dumps({
            'username': 'username',
            'password': 'password',
            'to': 'login_user'
        })
        self.client.send(self.__data_pack(bytes(data, "utf-8")))

        received = self.__receive(self.client)
        received = json.loads(received)
        self.assertTrue(received['is_correct'])

    def test_register_user_false(self):
        data = json.dumps({
            'first_name': "first_name",
            'username': "username",
            'password': "password",
            'public_key': "public_key",
            'to': 'register_user'
        })
        self.client.send(self.__data_pack(bytes(data, "utf-8")))

        received = self.__receive(self.client)
        received = json.loads(received)
        self.assertFalse(received['is_success'])

    def test_login_user_false(self):
        data = json.dumps({
            'username': 'username',
            'password': 'password1',
            'to': 'login_user'
        })
        self.client.send(self.__data_pack(bytes(data, "utf-8")))

        received = self.__receive(self.client)
        received = json.loads(received)
        self.assertFalse(received['is_correct'])

    def test_broadcast(self):
        sock = (self.host, self.port)

        client_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_two.connect(sock)

        data_one = {
            'username': 'test_one',
            'message': "hi test_two",
            'to': 'broadcast'
        }

        data_one = self.__encode_message(data_one)
        self.client.send(self.__data_pack(bytes(json.dumps(data_one), "utf-8")))

        data_two = {
            'username': 'test_two',
            'message': "hi test_one",
            'to': 'broadcast'
        }

        data_two = self.__encode_message(data_two)
        client_two.send(self.__data_pack(bytes(json.dumps(data_two), "utf-8")))

        received_one = self.__receive(self.client)
        self.__receive(client_two)
        received_two = self.__receive(client_two)

        self.assertEqual("hi test_two", self.__receive_message(received_one))
        self.assertEqual("hi test_one", self.__receive_message(received_two))

        client_two.close()

    def test_to_user(self):
        sock = (self.host, self.port)

        client_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_two.connect(sock)

        data_one = {
            'username': 'test_one',
            'message': "hi test_two",
            'to': 'to_user',
            'to_user': 'test_one'
        }

        data_one = self.__encode_message(data_one)
        self.client.send(self.__data_pack(bytes(json.dumps(data_one), "utf-8")))

        data_two = {
            'username': 'test_two',
            'message': "hi test_one",
            'to': 'to_user',
            'to_user': 'test_two'
        }

        data_two = self.__encode_message(data_two)
        client_two.send(self.__data_pack(bytes(json.dumps(data_two), "utf-8")))
        received_one = self.__receive(self.client)
        received_two = self.__receive(client_two)

        self.assertEqual("hi test_two", self.__receive_message(received_one))
        self.assertEqual("hi test_one", self.__receive_message(received_two))

        client_two.close()
