import socket

class Server:
    def __init__(self):
        self.ip = ""
        self.port = -1
        self.udp_socket = None

    def create(self, ip, port):
        self.close()
        self.ip = ip
        self.port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((ip, port))

    def close(self):
        if self.udp_socket:
            self.udp_socket.close()
        self.ip = ""
        self.port = -1
        self.udp_socket = None

    def send(self, msg):
        if self.udp_socket:
            self.udp_socket.sendto(msg, (self.ip, self.port))

    def receive(self, buffer_size=1024):
        if self.udp_socket:
            try:
                data, addr = self.udp_socket.recvfrom(buffer_size)
                return data
            except:
                return None
        return None
    
if __name__ == "__main__":
    udp_server = Server()
    udp_server.create("localhost", 12345)
    while True:
        data = udp_server.receive()
        if data:
            print(f"Received message: {data}")