import socket
from macros import *
import checksum

class Host():
    '''Base class for Client and Server, handling common UDP socket operations'''
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def execute(self):
        raise NotImplementedError("Not implemented in subclass")

    def encapsulate(self, msg):
        '''Encode and add checksum to the message'''
        if isinstance(msg, str):
            msg = msg.encode("utf-8")
        elif isinstance(msg, int):
            msg = msg.to_bytes(1)
        cs = checksum.calc_checksum(msg)
        return cs + msg
    
    def get_checksum_msg(self, msg):
        '''Separate checksum and message'''
        return msg[:4], msg[4:]

    def receive(self):
        '''Receive a message from the UDP socket'''
        try:
            content, sender_addr = self.udp_socket.recvfrom(MAX_PACKET_SIZE)
            return content, sender_addr
        except TimeoutError:
            print("No response from server, request timed out.")
            return None, None
        except Exception as e:
            print(f"Error receiving message: {e}")

    def send(self, ip, port, msg):
        '''Send a message to the specified IP and port'''
        msg = self.encapsulate(msg)
        try:
            self.udp_socket.sendto(msg, (ip, port))
        except Exception as e:
            print(f"Error sending message: {e}")
            

    