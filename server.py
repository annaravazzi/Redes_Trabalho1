"""
Classe servidor para responder a requisições de arquivos de clientes via UDP.
"""
from host import Host
import checksum
from macros import Commands, Codes, DATA_CHUNK_SIZE, DELAY, MAX_NUM_PACKETS, DIR_SERVER_FILES as DIR
from time import sleep

class Server(Host):
    def __init__(self, ip, port):
        super().__init__()
        self.bind_address(ip, port)
        self.execute()

    def bind_address(self, ip, port):
        """
        Associa o socket UDP ao endereço IP e porta especificados.
        """
        self.server_addr = (ip, port)
        self.udp_socket.bind((ip, port))
        print(f"Server bound to {ip}:{port}")
    
    def execute(self):
        """
        Loop principal do servidor, esperando por requisições de clientes.
        """
        while True:
            msg, client_addr = self.receive()   # Espera por mensagens (sem timeout)
            if msg == "CONN_RESET":
                continue
            elif msg == None:
                continue
            # self.send(client_addr[0], client_addr[1], Codes.UNKNOWN)  # Para testes
            # self.send(client_addr[0], client_addr[1], "")  # Para testes
            # self.send(client_addr[0], client_addr[1], Codes.OK)  # Para testes
            # continue
            self.parse_request(msg, client_addr)    # Interpreta e responde à requisição
    
    def parse_request(self, msg, client_addr):
        """
        Processa a requisição do cliente e envia a resposta apropriada.
        """
        # Checa se existe checksum e mensagem no padrão esperado
        try:
            cs, msg = self.get_checksum_msg(msg)
            command = msg.decode().split(' ')[0]    # Comando (primeira palavra da mensagem)
        except IndexError:
            self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
            print("ERROR: Unable to extract checksum and/or message. Discarding.")
            return

        # msg = (msg.decode() + " extra").encode()  # Para testes
        # Verifica integridade do checksum
        if not checksum.verify_checksum(msg, cs):
            self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
            print("ERROR: Checksum mismatch. Discarding request.")
            return
    
        if command == Commands.GET_FILE:  # Requisitar arquivo completo
            try:
                filename = msg.decode().split(' ')[1]
                print(f"Client requested file {filename}")
                self.send_file(filename, client_addr)
            except IndexError:
                self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
                print("ERROR: Filename missing. Discarding.")
                return

        elif command == Commands.GET_PACKET:  # Requisitar pacote específico
            try:
                filename = msg.decode().split(' ')[1]
                packet_index = int(msg.decode().split(' ')[2])
            except IndexError:
                self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
                print("ERROR: Filename/packet index missing. Discarding.")
                return
            print(f"Client requested packet {packet_index} of file {filename}")
            self.send_file(filename, client_addr, packet_index)

        else:
            self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
            print("ERROR: Unknown command. Discarding.")
            return

    def send_file(self, filename, client_addr, packet=None):
        """
        Envia o arquivo solicitado ao cliente, seja completo ou um pacote específico.
        """
        file, _ = self.load_file(filename)  # Carrga o arquivo em bytes

        # Arquivo não encontrado
        if not file:
            self.send(client_addr[0], client_addr[1], Codes.NOT_FOUND)
            print("ERROR: File not found.")
            return

        chunks, num_chunks = self.segment_file(file)

        # Arquivo muito grande
        if num_chunks > MAX_NUM_PACKETS:
            self.send(client_addr[0], client_addr[1], Codes.TOO_LARGE)
            print("ERROR: File too large.")
            return

        # Se um pacote específico foi requisitado
        if packet:
            # Índice fora do intervalo
            if packet < 0 or packet >= num_chunks:
                self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
                print("ERROR: Packet index invalid.")
                return
            
            # Envia apenas o pacote requisitado
            self.send_packet(num_chunks, packet, chunks[packet], client_addr)

            print(f"Sent packet {packet} to {client_addr}")

        else:
            # Envia todos os pacotes do arquivo
            for i, chunk in zip(range(num_chunks), chunks):
                self.send_packet(num_chunks, i, chunk, client_addr)
                
            print(f"Sent {num_chunks} packets to {client_addr}")

    def load_file(self, filename):
        """
        Carrega o arquivo do diretório server_files/.
        Retorna o conteúdo do arquivo em bytes e seu tamanho.
        """
        try:
            with open(DIR + filename, "rb") as file:
                content = file.read()
                file.close()
            return content, len(content)
        except FileNotFoundError:
            return None, 0

    def segment_file(self, file_content, chunk_size=DATA_CHUNK_SIZE):
        """
        Segmenta o conteúdo do arquivo em pedaços de tamanho chunk_size.
        Retorna uma lista de pedaços e o número total de pedaços.
        """
        segments = [file_content[i:i+chunk_size] for i in range(0, len(file_content), chunk_size)]
        num_segments = len(segments)
        return segments, num_segments
    
    def send_packet(self, num_chunks, packet, chunk, client_addr):
        """
        Envia um pacote ao cliente
        """
        response = Codes.OK.to_bytes(1) + num_chunks.to_bytes(3) + packet.to_bytes(3) + chunk
        self.send(client_addr[0], client_addr[1], response)
        sleep(DELAY)     # Delay para evitar buffer overflow
    

if __name__ == "__main__":
    print("Set server port: ")
    port = int(input())
    udp_server = Server("127.0.0.1", port)