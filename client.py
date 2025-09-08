import socket

class Client():
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = ('', 0000)

    def send(self, ip, port, msg):
        try:
            self.server_addr = (ip, port)
            self.udp_socket.sendto(msg.encode(), self.server_addr)
            print(f"Sent message {msg.encode()} to {ip}:{port}")
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    udp_client = Client()
    udp_client.send("localhost", 12345, "Hello, Server!")