from Crypto.PublicKey import RSA


class Crypto:
    def encode(self, data):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    @staticmethod
    def generate_keys(bits=2048):
        """
        Generate an RSA keypair with an exponent of 65537 in PEM format
        param: bits The key length in bits
        Return private key and public key
        """
        new_key = RSA.generate(bits)
        public_key = new_key.publickey().exportKey("PEM")
        private_key = new_key.exportKey("PEM")
        return private_key, public_key

print(Crypto.generate_keys())
