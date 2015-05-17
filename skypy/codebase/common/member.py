class Member:
    def __init__(self):
        self.__client_address = None
        self.__request = None
        self.__username = None

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

    @staticmethod
    def find_member(search_member, members):
        for member in members:
            if member.username == search_member:
                return member
