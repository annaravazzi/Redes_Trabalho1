import socket

class Client:
    def __init__(self):
        self.ip = ""
        self.port = -1
        self.udp_socket = None

    def create(self, ip, port):
        self.close()
        self.ip = ip
        self.port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
            except socket.error as e:
                print(f"Error receiving data: {e}")
        return None

if __name__ == "__main__":
    udp_client = Client()
    udp_client.create("localhost", 12345)
    udp_client.send(b"Hello, Server!")