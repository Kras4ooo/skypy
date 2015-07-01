from codebase.server.db.db_connection import Database
from codebase.utils.singleton import Singleton


class Model(Database, metaclass=Singleton):
    def __init__(self):
        self.result = None
        super().__init__()

    def execute(self, query):
        self.cur.execute(query)
        self.result = self.cur


class User(Model):
    def __init__(self):
        self.username = None
        self.password = None
        self.first_name = None
        self.public_key = None

        self.db_name = 'user'
        super().__init__()

    def register_user(self, data):
        self.username = data['username']
        self.password = data['password']
        self.first_name = data['first_name']
        self.public_key = data['public_key']
        if self.__check_exist_user():
            return False
        self.__insert_user()
        return True

    def login_user(self, data):
        self.username = data['username']
        self.password = data['password']
        if self.__check_user():
            return True
        return False

    def __insert_user(self):
        query = "INSERT INTO {0} (first_name, username, password, public_key)" \
                " VALUES ('{1}', '{2}', '{3}', '{4}')".format(self.db_name,
                                                              self.first_name,
                                                              self.username,
                                                              self.password,
                                                              self.public_key)
        self.cur.execute(query)
        self.conn.commit()

    def __check_user(self):
        query = 'SELECT COUNT("{0}") FROM {1} WHERE username="{2}" AND ' \
                'password="{3}"'
        query = query.format('id', self.db_name, self.username, self.password)
        self.execute(query)
        for result in self.result:
            if result[0] != 0:
                return True
            return False

    def __check_exist_user(self):
        query = 'SELECT COUNT("{0}") FROM {1} WHERE username="{2}"'
        query = query.format('id', self.db_name, self.username)
        self.execute(query)
        for result in self.result:
            if result[0] != 0:
                return True
            return False
