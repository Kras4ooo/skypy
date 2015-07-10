import json
import os
import unittest
import base64

from codebase.utils.cryptodata import CryptoData


class TestCryptoData(unittest.TestCase):
    def setUp(self):
        pub_key = os.path.join(
            os.path.dirname(__file__),
            '..{0}test_keys{0}public.pub'.format(os.path.sep)
        )
        private_key = os.path.join(
            os.path.dirname(__file__),
            '..{0}test_keys{0}private.pem'.format(os.path.sep)
        )
        with open(pub_key) as f:
            self.public_key = f.read()
        with open(private_key) as f:
            self.private_key = f.read()
        self.data = {"message": "Test"}
        self.new_data = CryptoData.encode(self.data, self.public_key)

    def test_generate_keys(self):
        private_key, public_key = CryptoData.generate_keys()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)

    def test_encode(self):
        self.assertIn('key_string', self.new_data.keys())
        self.assertIn('val_string', self.new_data.keys())
        self.assertIn('message', self.new_data.keys())

    def test_encode_is_base64(self):
        self.assertTrue(base64.b64decode(self.new_data['key_string']))

    def test_decode(self):
        self.new_data = CryptoData.decode(self.new_data, self.private_key)
        self.assertNotIn('key_string', self.new_data.keys())
        self.assertNotIn('val_string', self.new_data.keys())

    def test_encode_base64(self):
        self.new_data = CryptoData.encode_base64("test")
        self.assertEqual("dGVzdA==", self.new_data)

    def test_decode_base64(self):
        self.new_data = CryptoData.decode_base64("dGVzdA==")
        self.assertEqual("test", self.new_data.decode("utf-8"))

    def test_encode_only_rsa(self):
        self.new_data = CryptoData.encode_only_rsa("test", self.public_key)
        self.assertEqual("RFbBUM7z6xheG5BpB2DC8Ua7SXwgc6IEg75"
                         "hu4Pbm3cPZeTC1KSjOGJJ85qLXN0Z/fRzyZVOV"
                         "D3iMzhB2JiSpyghv2W1nkiWwlhe6MD9EMKA2+6Si"
                         "u6Wa1PB4I2BFJiptiZVdhTFf0o+GtwPC3GyK3YKi"
                         "3B+TmxnD5fnJZHVOE4=", self.new_data)
