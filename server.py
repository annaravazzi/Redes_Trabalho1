from host import Host
import checksum
from macros import *
from time import sleep

class Server(Host):
    def __init__(self, ip, port):
        super().__init__()      # Initialize Host class
        self.bind_address(ip, port)
        self.execute()   # Start server loop

    def bind_address(self, ip, port):
        '''Bind the UDP socket to the specified IP and port'''
        self.server_addr = (ip, port)
        self.udp_socket.bind((ip, port))
        print(f"Server bound to {ip}:{port}")
    
    def execute(self):
        '''Main server loop to receive and handle incoming requests'''
        while True:
            msg, client_addr = self.receive()
            self.parse_request(msg, client_addr)
    
    def parse_request(self, msg, client_addr):
        '''Parse and handle incoming client requests'''
        # try:
        cs, msg = self.get_checksum_msg(msg)    # Separate checksum and message

        if not checksum.verify_checksum(msg, cs):
            self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
            print("Checksum mismatch. Discarding request.")
            return  # Discard message and return to the main loop
    
        command = msg.decode().split(' ')[0] # Get first word (command)

        if command == Commands.GET_FILE:    # Request file
            filename = msg.decode().split(' ')[1]
            print(f"Client requested file {filename}")
            self.send_file(filename, client_addr)

        elif command == Commands.GET_PACKET:  # Request specific packet
            filename = msg.decode().split(' ')[1]
            packet_index = int(msg.decode().split(' ')[2])
            print(f"Client requested packet {packet_index} of file {filename}")
            self.send_file(filename, client_addr, packet_index)

        else:
            self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
            print("Unknown command. Discarding.")
            return  # Discard message and return to the main loop
                
        # except (IndexError, ValueError):
        #     self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
        #     print("Malformed request. Discarding.")
        #     return


    def send_file(self, filename, client_addr, packet=None):
        '''Send the requested file or specific packet to the client'''

        file, _ = self.load_file(filename)

        if not file:
            self.send(client_addr[0], client_addr[1], Codes.NOT_FOUND)
            return

        chunks, num_chunks = self.segment_file(file)

        if num_chunks > 16777215:  # More than 16777215 packets (3 bytes)
            self.send(client_addr[0], client_addr[1], Codes.TOO_LARGE)
            print("File too large to send (> ~16GB).")
            return

        if packet:   # Send specific packet
            if packet < 0 or packet >= num_chunks:
                self.send(client_addr[0], client_addr[1], Codes.BAD_REQUEST)
                print("Packet index invalid.")
                return
            
            self.send_packet(num_chunks, packet, chunks[packet], client_addr)
            sleep(0.01)  # Small delay to avoid packet loss

            print(f"Sent packet {packet} to {client_addr}")

        else:        # Send all packets
            for i, chunk in zip(range(num_chunks), chunks):
                self.send_packet(num_chunks, i, chunk, client_addr)
                sleep(0.01)  # Small delay to avoid packet loss
                
            print(f"Sent {num_chunks} packets to {client_addr}")

    def load_file(self, filename):
        '''Load the specified file from disk'''
        try:
            with open("server_files/" + filename, "rb") as file:
                content = file.read()
                file.close()
            return content, len(content)
        except FileNotFoundError:
            print("File not found.")
            return None, 0

    def segment_file(self, file_content, chunk_size=DATA_CHUNK_SIZE):
        '''Segment the file content into chunks of specified size'''
        segments = [file_content[i:i+chunk_size] for i in range(0, len(file_content), chunk_size)]
        num_segments = len(segments)
        return segments, num_segments
    
    def send_packet(self, num_chunks, packet, chunk, client_addr):
        '''Send a single packet to the client'''
        response = Codes.OK.to_bytes(1) + num_chunks.to_bytes(3) + packet.to_bytes(3) + chunk
        self.send(client_addr[0], client_addr[1], response)
    

if __name__ == "__main__":
    print("Set server port: ")
    port = int(input())
    udp_server = Server("localhost", port)

    # udp_server.send_file("Algoritmos_Teoria_e_Pratica_Co.pdf", ("", 0000))
    # content, _ = udp_server.load_file("Algoritmos_Teoria_e_Pratica_Co.pdf")
    # print(f"File size: {len(content)}")
    # segments = udp_server.segment_file(content)
    # print(f"Number of chunks: {len(segments)}")
    # print(f"Last packet size: {len(segments[len(segments)-1])}")
    # total = (len(segments)-1)*CHUNK_SIZE+len(segments[len(segments)-1])
    # print(f"Total: {total}")
    # udp_server.bind_address("localhost", SERVER_PORT)   # Open socket
    # while True:
    #     # Wait for incoming messages
    #     udp_server.receive()