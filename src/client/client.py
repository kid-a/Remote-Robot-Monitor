import socket

class Client(object):

    def __init__(self, host, port):
        #Create a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Connect to the remote host and port
        self.sock.settimeout(10)
	self.sock.connect((host, port))

    def send(self, message):
        # Send a request to the host
        self.sock.send(message)
        # Get the host's response, no more than, say, 1,024 bytes
        response_data = self.sock.recv(1024)
        print response_data
        response_data.replace('\n','')
        response_data.replace('\r','')
        return response_data.split(';')

    def close(self):
        # Terminate
        self.sock.close()
