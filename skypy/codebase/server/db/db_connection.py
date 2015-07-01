import MySQLdb


database = {
    'host': '127.0.0.1',
    'user': 'root',
    'passwd': 'parola',
    'db': 'skypy'
}


class Database:
    def __init__(self):
        self.conn = MySQLdb.connect(**database)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()
