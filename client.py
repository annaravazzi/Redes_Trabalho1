"""
Classe cliente para solicitar arquivos a um servidor via UDP.
"""
import checksum
from macros import Commands, Codes, TIMEOUT, MAX_PACKET_SIZE, DIR_CLIENT_FILES as DIR
from host import Host

class Client(Host):
    def __init__(self):
        super().__init__()
        self.filename = ""  # Arquivo atual sendo solicitado
        self.file_packets = {}  # Pacotes recebidos {index: data_chunk}
        self.num_packets = 0    # Número total de pacotes esperados
        self.close_comm = False # Flag para sair do loop de comunicação
        self.execute()

    def execute(self):
        """
        Loop principal
        """
        while True:
            # Detalhes do servidor e arquivo a ser solicitado
            print("Server IP address: ")
            ip = input()
            print("Server port: ")
            port = int(input())
            print("What file would you like?")
            self.filename = input()

            self.request_file(self.filename, ip, port)  # Request de arquivo
            self.wait_response(ip, port)    # Espera resposta (será interpretada em parse_response())

            # Se o arquivo não foi completamente recebido, solicita os pacotes faltantes (até completar o arquivo)
            # Nota: se a resposta do servidor for um erro, num_packets = 0, então o loop não é executado
            while not self.is_file_complete(self.num_packets):
                for i in range(self.num_packets):
                    if i not in self.file_packets:
                        print(f"Requesting missing packet {i}")
                        self.request_packet(self.filename, i, ip, port)
                # Reespera respostas
                self.close_comm = False
                self.wait_response(ip, port)

            # Reset para próxima iteração
            print("You may request another file.")
            self.filename = ""
            self.file_packets = {}
            self.num_packets = 0
            self.close_comm = False
    
    def request_file(self, filename, ip, port):
        """
        Manda uma requisição de arquivo ao servidor (GET_FILE <filename>).
        """
        msg = Commands.GET_FILE + f" {filename}"
        # msg = Commands.GET_WRONG + f" {filename}"  # Para testes
        # msg = Commands.GET_FILE  # Para testes
        # msg = ""
        print(f"Press enter to send {msg} to {ip}:{port}")
        input()
        self.send(ip, port, msg)
        

    def request_packet(self, filename, packet_index, ip, port):
        """
        Manda uma requisição de pacote ao servidor (GET_PACKET <filename> <packet_index>).
        """
        msg = Commands.GET_PACKET + f" {filename} {packet_index}"
        # msg = Commands.GET_PACKET + f" {filename} {self.num_packets + 1}"  # Para testes
        # msg = Commands.GET_PACKET + f" {filename}"  # Para testes
        print(f"Press enter to send {msg} to {ip}:{port}")
        input()
        self.send(ip, port, msg)

    def wait_response(self, ip, port):
        """
        Aguarda e processa respostas do servidor.
        """
        # Comunicação (loop) até que o arquivo seja completamente recebido ou ocorra timeout (ou outro erro)
        while not self.close_comm:
            self.udp_socket.settimeout(TIMEOUT) # Reseta timeout a cada iteração
            msg, server_addr = self.receive()
            msg = self.packet_damage(msg, "drop")
            # msg = self.packet_damage(msg, "bit_flip")

            # Ver host.receive()
            if msg == "TIMEOUT":
                print("ERROR: Timeout limit reached. Ending communication.")
                print("Press enter to continue.")
                input()
                return
            if msg == "CONN_RESET":
                print("ERROR: Server unavailable.")
                print("Press enter to continue.")
                input()
                return
            if msg == None:
                continue
            # Server desconhecido
            if server_addr != (ip, port):
                print(f"Received message from unknown server {server_addr}, expected {ip}:{port}. Discarding.")
                print("Press enter to continue.")
                input()
                return
            
            # Processa resposta
            self.parse_response(msg)

    def parse_response(self, msg):
        """
        Processa a resposta do servidor.
        Verifica checksum, interpreta código de resposta e armazena dados do pacote recebido.
        """
        cs, msg = self.get_checksum_msg(msg)    # Separa checksum da mensagem
        code = int.from_bytes(msg[0:1])     # Código de resposta (primeiro byte da mensagem)

        # Verifica integridade do checksum
        if not checksum.verify_checksum(msg, cs):
            print("ERROR: Checksum mismatch. Discarding response.")
            return
        
        if code == Codes.OK:    # OK = pacote recebido com sucesso
            # Extrai informações do pacote
            if len(msg) < 7:   # Mínimo de bytes para um pacote OK (1 code + 3 num_packets + 3 packet_index)
                print("ERROR: Incomplete packet received. Discarding.")
                print("Press enter to continue.")
                input()
                return
            self.num_packets = int.from_bytes(msg[1:4])
            packet_index = int.from_bytes(msg[4:7])
            data_chunk = msg[7:]
            # Armazena o pacote recebido
            if self.receive_packet(data_chunk, packet_index, self.num_packets): # Se o arquivo está completo (pacotes esperados = pacotes recebidos)
                print("File received successfully.")
                self.write_file(self.filename)
                self.close_comm = True

        else:   # Erro na requisição
            self.close_comm = True
            if code == Codes.BAD_REQUEST:
                print("Server response: BAD REQUEST")
            elif code == Codes.NOT_FOUND:
                print("Server response: FILE NOT FOUND")
            elif code == Codes.TOO_LARGE:
                print("Server response: FILE TOO LARGE")
            else:
                print("Unknown server response code.")

    def receive_packet(self, data_chunk, index, num_packets):
        """
        Armazena o pacote recebido se ainda não estiver armazenado.
        Retorna True se o arquivo estiver completo (todos os pacotes recebidos).
        """
        if len(self.file_packets) < num_packets:    # Ainda não recebeu todos os pacotes
            self.file_packets[index] = data_chunk   # Armazena o pacote no dicionário (sem repetição)
            print(f"Received packet {index}. Total packets received: {len(self.file_packets)}/{num_packets}")
        return self.is_file_complete(num_packets)
    
    def is_file_complete(self, num_packets):
        """
        Verifica se todos os pacotes do arquivo foram recebidos.
        Pacotes armazenados = pacotes esperados.
        """
        return len(self.file_packets) == num_packets
    
    def write_file(self, filename):
        """
        Escreve o arquivo recebido no diretório client_files/.
        """
        # Ordena os pacotes pelo índice (garante que os pacotes serão escritos na ordem correta)
        self.file_packets = dict(sorted(self.file_packets.items()))
        with open(DIR + filename, "wb") as f:
            for i in range(len(self.file_packets)):
                f.write(self.file_packets[i])
        print(f"File written to {filename}")   

    def packet_damage(self, packet, damage_type, error_rate=0.01):
        """
        Função de teste: danifica um pacote (perda de dados).
        Tipos de dano: "drop" (descarta o pacote), "bit_flip" (altera um bit aleatório).
        Taxa de erro: probabilidade de ocorrer o dano (0 a 1).
        """
        import random
        if random.random() > error_rate:
            return packet
        seq_num = int.from_bytes(packet[8:11]) if packet and len(packet) >= 11 else -1
        if damage_type == "drop":
            print(f"Simulating packet loss for packet {seq_num}")
            return None
        elif damage_type == "bit_flip":
            print(f"Simulating bit flip for packet {seq_num}")
            damaged_bit = random.randint(0, (8*len(packet))-1)
            try:
                return (int.from_bytes(packet) ^ (2**damaged_bit)).to_bytes(MAX_PACKET_SIZE)
            except UnicodeDecodeError:
                return (int.from_bytes(packet.decode()) ^ (2**damaged_bit)).to_bytes(MAX_PACKET_SIZE)
        return packet         
        

if __name__ == "__main__":
    udp_client = Client()