import socketserver


class SkyPyServer(socketserver.BaseRequestHandler):
    members = []

    def handle(self):
        close = 0
        self.members.append((self.request, self.client_address))
        while not close:
            _data = self.request.recv(1024)
            if not _data:
                # EOF, client closed, just return
                self.members.remove(self.client_address)
                return
            print("Received from %s: %s" % (self.client_address, _data))
            self.request.sendall(_data)
            if 'quit' in str(_data):
                close = 1
            if 'ss' in str(_data):
                print(self.members[1][1])
                self.members[1][0].sendto(_data, self.members[1][1])

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), SkyPyServer)
    server.serve_forever()
