import MySQLdb
database = {
    'host': '127.0.0.1',
    'user': 'root',
    'passwd': 'parola',
    'db': 'skypy'
}
conn = MySQLdb.connect(**database)
cur = conn.cursor()
a = cur.execute("SELECT COUNT(id) FROM user WHERE username='dsa'")
print(cur.rowcount)
for r in cur:
    print(r)
cur.close()
conn.close()
