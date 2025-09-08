import socket

class Server():
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = ('', 0000)

    def bind_address(self, ip, port):
        self.server_addr = (ip, port)
        self.udp_socket.bind((ip, port))
        print(f"Server bound to {ip}:{port}")

    def receive(self, buffer_size=1024):
        data, client_addr = self.udp_socket.recvfrom(buffer_size)
        print(f"Received data from {client_addr}: {data.decode()}")
        return data.decode(), client_addr


if __name__ == "__main__":
    udp_server = Server()
    udp_server.bind_address("localhost", 12345)
    while True:
        udp_server.receive()