"""
Classe base para Cliente e Servidor, lidando com operações comuns de socket UDP e encapsulamento de mensagens com checksum.
"""

import socket
from macros import MAX_PACKET_SIZE
import checksum
import errno

class Host():
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    def execute(self):
        """
        Método a ser implementado por subclasses (Client e Server).
        """
        raise NotImplementedError("Not implemented in subclass")

    def encapsulate(self, msg):
        """
        Codifica a mensagem e adiciona o checksum no início.
        """
        if isinstance(msg, str):
            msg = msg.encode("utf-8")
        elif isinstance(msg, int):
            msg = msg.to_bytes(1)
        cs = checksum.calc_checksum(msg)
        return cs + msg
    
    def get_checksum_msg(self, msg):
        """
        Separa o checksum (primeiros 4 bytes) da mensagem em si.
        """
        return msg[:4], msg[4:]

    def receive(self):
        """
        Recebe uma mensagem do socket UDP.
        """
        try:
            content, sender_addr = self.udp_socket.recvfrom(MAX_PACKET_SIZE)
            return content, sender_addr
        except TimeoutError:
            return "TIMEOUT", None
        except ConnectionResetError as e:
            if e.errno == errno.WSAECONNRESET:
                return "CONN_RESET", None
            else:
                print(f"Connection error: {e}")
                return None, None
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None, None

    def send(self, ip, port, msg):
        """
        Envia uma mensagem ao endereço IP e porta especificados.
        """
        msg = self.encapsulate(msg)
        try:
            self.udp_socket.sendto(msg, (ip, port))
        except Exception as e:
            print(f"Error sending message: {e}")

    def flush_buffer(self, timeout=None):
        """
        Esvazia o buffer do socket UDP.
        """
        self.udp_socket.settimeout(0.1)  # Timeout curto para esvaziar o buffer
        while True:
            msg, _ = self.receive()
            if msg == None or msg == "TIMEOUT":
                break
        self.udp_socket.settimeout(timeout)  # Reseta timeout  

    