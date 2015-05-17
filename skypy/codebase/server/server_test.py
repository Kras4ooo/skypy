import socketserver


class SkyPyServer(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    list_members = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self):
        close = 0
        self.list_members.append((self.request, self.client_address))
        print(len(self.list_members))
        while not close:
            _data = self.request.recv(1024)
            if not _data:
                # EOF, client closed, just return
                self.list_members.remove(self.client_address)
                return
            print("Received from %s: %s" % (self.client_address, _data))
            self.request.sendall(_data)
            if 'quit' in str(_data):
                close = 1
            if 'ss' in str(_data):
                print(self.list_members[1][1])
                self.list_members[1][0].sendto(_data, self.list_members[1][1])

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), SkyPyServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
