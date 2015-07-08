import socketserver
from codebase.server.server import SkyPyServer

if __name__ == "__main__":
    HOST, PORT = "localhost", 9998
    server = socketserver.ThreadingTCPServer((HOST, PORT), SkyPyServer)
    server.serve_forever()
