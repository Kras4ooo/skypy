import json
import os
import socket
import socketserver
import threading
import unittest
from codebase.server.server import SkyPyServer
from codebase.utils.cryptodata import CryptoData


class TestSkyPyServer(unittest.TestCase):
    def setUp(self):
        host, port = "localhost", 9999
        sock = (host, port)
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
        data = data.decode('utf-8')
        private_key = self.__get_private_key().decode('utf-8')
        decrypt_data = CryptoData.decode(data, private_key)
        message = decrypt_data['message'].decode('utf-8')
        return message

    def test_client_initialize(self):
        data = json.dumps({
            'public_key': 'test_key',
            'username': 'test',
            'to': 'initialize'
        })
        self.client.send(bytes(data, "utf-8"))

        received = self.client.recv(1024)
        received = received.decode('utf-8')
        received = json.loads(received)

        self.assertEqual(received['pub_key'], "test_key")

    def test_not_exist_method(self):
        data = json.dumps({
            'username': 'test',
            'to': 'not_exist'
        })
        self.client.send(bytes(data, "utf-8"))

        received = self.client.recv(1024)
        received = received.decode('utf-8')
        received = json.loads(received)

        self.assertEqual(received['error'], "AttributeError")

    def test_broadcast(self):
        host, port = "localhost", 9999
        sock = (host, port)

        client_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_two.connect(sock)

        data = {
            'username': 'test_one',
            'message': "hi test_two",
            'to': 'broadcast'
        }

        data = self.__encode_message(data)
        self.client.send(bytes(json.dumps(data), "utf-8"))

        data = {
            'username': 'test_two',
            'message': "hi test_one",
            'to': 'broadcast'
        }

        data = self.__encode_message(data)
        client_two.send(bytes(json.dumps(data), "utf-8"))

        received_two = client_two.recv(1024)
        received_one = self.client.recv(1024)

        self.assertEqual("hi test_one", self.__receive_message(received_one))
        self.assertEqual("hi test_two", self.__receive_message(received_two))

        client_two.close()
