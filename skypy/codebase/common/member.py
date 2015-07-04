class Member:
    def __init__(self):
        self.__client_address = None
        self.__request = None
        self.__username = None
        self.__public_key = None
        self.__private_key = None
        self.__activated = False

    @property
    def client_address(self):
        return self.__client_address

    @client_address.setter
    def client_address(self, value):
        self.__client_address = value

    @property
    def request(self):
        return self.__request

    @request.setter
    def request(self, value):
        self.__request = value

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value

    @property
    def public_key(self):
        return self.__public_key

    @public_key.setter
    def public_key(self, value):
        value = value.decode('utf-8')
        self.__public_key = value

    @property
    def private_key(self):
        return self.__private_key

    @private_key.setter
    def private_key(self, value):
        value = value.decode('utf-8')
        self.__private_key = value

    @property
    def activated(self):
        return self.__activated

    @activated.setter
    def activated(self, value):
        self.__activated = value

    @staticmethod
    def find_member(search_member, members):
        for member in members:
            if member.username == search_member:
                return member

    @staticmethod
    def find_member_dict(search_member, members):
        for key, value in members.items():
            if value.username == search_member:
                return key
