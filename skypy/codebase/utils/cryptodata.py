import base64
import json
import random
import string
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES


class CryptoData:
    @staticmethod
    def encode(data, pub_key):
        """
        Method encodes the message using the AES and RSA

        @type data: dict
        @param data: It contains data message
        @type pub_key: string
        @param pub_key: It contains the key which
        will be used to encrypt the password
        @rtype: dict
        @return:  returns dictionary containing the message
        and two coded variables containing passwords to encode the message.
        """
        # Encryption
        random_key_string = CryptoData._generate_random_string()
        random_val_string = CryptoData._generate_random_string()
        encryption_suite = AES.new(random_key_string,
                                   AES.MODE_CFB,
                                   random_val_string)

        pub_key = RSA.importKey(pub_key)

        data['message'] = encryption_suite.encrypt(data['message'])
        data['message'] = base64.b64encode(data['message']).decode('utf-8')

        data['key_string'] = pub_key.encrypt(random_key_string, 32)
        data['key_string'] = base64.b64encode(data['key_string'][0])
        data['key_string'] = data['key_string'].decode('utf-8')

        data['val_string'] = pub_key.encrypt(random_val_string, 32)
        data['val_string'] = base64.b64encode(data['val_string'][0])
        data['val_string'] = data['val_string'].decode('utf-8')

        return data

    @staticmethod
    def decode(data, private_key):
        """
        Method decode the message using the AES and RSA

        @type data: dict
        @param data: It contains data message
        @type private_key: string
        @param private_key: It contains the key which
        will be used to decrypt the password
        @rtype: dict
        @return:  It contains a dict with the decoded message
        """
        private_key = RSA.importKey(private_key)

        data = json.loads(data)
        data['key_string'] = base64.b64decode(data['key_string'])
        data['val_string'] = base64.b64decode(data['val_string'])
        data['message'] = base64.b64decode(data['message'])

        key_string = private_key.decrypt(data['key_string'])
        val_string = private_key.decrypt(data['val_string'])

        decryption_suite = AES.new(key_string, AES.MODE_CFB, val_string)
        data['message'] = decryption_suite.decrypt(data['message'])

        del data['key_string']
        del data['val_string']

        return data

    @staticmethod
    def _generate_random_string():
        """
        Generates random key length of 16 needed to encode the message

        @rtype key: bytes
        @return key: random key
        """
        size = 16
        alphabet = string.ascii_uppercase
        digits = string.digits
        key = ''.join(random.choice(alphabet + digits) for _ in range(size))
        key = bytes(key, 'utf-8')
        return key

    @staticmethod
    def generate_keys(bits=1024):
        """
        Generate an RSA keypair with an exponent of 65537 in PEM format
        param: bits The key length in bits
        Return private key and public key
        """
        new_key = RSA.generate(bits)
        public_key = new_key.publickey()
        private_key = new_key
        return private_key, public_key


"""
RSAPriKey, RSAPubKey = CryptoData.generate_keys()


data_test = {"message": "Zdravei PavkaZdravei Pavka"}
data_test = CryptoData.encode(data_test, RSAPubKey)
print(data_test)
data_test = CryptoData.decode(data_test, RSAPriKey)
print(data_test)
"""


"""
message = base64.b64encode('{"dsa":["fdsaf","ffdsa","dfsafdsa"]}'.encode('utf-8'))
print(message)
enc = RSAPubKey.encrypt(message, 32)
print(enc)
m = base64.b64decode(RSAPriKey.decrypt(enc)).decode("utf-8")
print(m)
print(json.loads(m)['dsa'][0])
"""