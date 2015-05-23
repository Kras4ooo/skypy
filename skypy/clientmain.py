import json
import socket

HOST, PORT = "localhost", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect to server and send data
sock.connect((HOST, PORT))

# Receive data from the server and shut down
data = json.dumps({'message': 'initialize', 'username': 'ivan', 'room': {'option': {'uid': 123, 'action': 'create_room'}}})
# data = json.dumps({'message': 'initialize', 'username': 'ivan', 'to_user': 'username', 'to': 'initialize'})
# json.dumps({'message': message, 'username': 'ivan', 'to_user': 'username', 'to': 'to_user'})
sock.send(bytes(data, "utf-8"))
while True:
    message = input("->")
    while len(message) == 0:
        message = input("->")
    data = json.dumps({'message': 'initialize', 'username': 'ivan', 'room': {'option': {'uid': 123, 'action': 'create_room'}}})
    sock.send(bytes(data, "utf-8"))
    received = str(sock.recv(100024), "utf-8")
    print("Received: {}".format(received))
