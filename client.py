import checksum
from macros import *
from host import Host

class Client(Host):
    def __init__(self):
        super().__init__()   # Initialize Host class
        self.filename = ""  # Current file being requested
        self.file_packets = {}  # Dictionary to store received packets {index: data_chunk}
        self.num_packets = 0    # Total number of packets expected
        self.close_comm = False # Flag to close communication loop
        self.execute()

    def execute(self):
        '''Main client loop to request files and handle responses'''
        while True:
            # Get server details and filename from user
            print("Server IP address: ")
            ip = input()
            print("Server port: ")
            port = int(input())
            print("What file would you like?")
            self.filename = input()

            self.request_file(self.filename, ip, port)  # Request the file from the server
            self.wait_response(ip, port)

            # If, by the end of communication, the file is not complete, request missing packets
            while not self.is_file_complete(self.num_packets):
                print("File incomplete, requesting missing packets...")
                # Request missing packets
                for i in range(self.num_packets):
                    if i not in self.file_packets:
                        print(f"Requesting missing packet {i}")
                        self.request_packet(self.filename, i, ip, port)
                # Wait for the server to respond with the missing packets
                self.close_comm = False
                self.wait_response(ip, port)

            # Reset for next file request
            self.filename = ""
            self.file_packets = {}
            self.num_packets = 0
            self.close_comm = False
    
    def request_file(self, filename, ip, port):
        '''Send a file request to the server'''
        msg = Commands.GET_FILE + f" {filename}"
        self.send(ip, port, msg)

    def request_packet(self, filename, packet_index, ip, port):
        '''Send a specific packet request to the server'''
        msg = Commands.GET_PACKET + f" {filename} {packet_index}"
        self.send(ip, port, msg)

    def wait_response(self, ip, port):
        '''Wait for responses from the server until communication is closed'''
        while not self.close_comm:
            self.udp_socket.settimeout(TIMEOUT) # Set timeout for receiving
            msg, server_addr = self.receive()
            if msg is None:
                print("No response received, ending wait.")
                return
            # Unknown server
            if server_addr != (ip, port):
                print(f"Received message from unknown server {server_addr}, expected {ip}:{port}. Discarding.")
                return
            self.parse_response(msg)

    def parse_response(self, msg):
        try:
            cs, msg = self.get_checksum_msg(msg)

            if not checksum.verify_checksum(msg, cs):
                print("Checksum mismatch. Discarding response.")
                return

            code = int.from_bytes(msg[0:1])
            if code == Codes.OK:
                self.num_packets = int.from_bytes(msg[1:4])
                packet_index = int.from_bytes(msg[4:7])
                data_chunk = msg[7:]
                print(f"Server response OK. Receiving packet {packet_index}. Number of packets to receive: {self.num_packets}")
                if self.receive_packet(data_chunk, packet_index, self.num_packets):
                    print("File received successfully.")
                    self.write_file(self.filename)
                    self.close_comm = True
                else:
                    print("File reception incomplete.")
            else:
                self.close_comm = True
                if code == Codes.BAD_REQUEST:
                    print("Server response: BAD REQUEST")
                elif code == Codes.NOT_FOUND:
                    print("Server response: FILE NOT FOUND")
                elif code == Codes.TOO_LARGE:
                    print("Server response: FILE TOO LARGE")
                else:
                    print("Unknown server response code.")

        except (IndexError, ValueError):
            print("Malformed response from server. Discarding.")

    def receive_packet(self, data_chunk, index, num_packets):
        if len(self.file_packets) < num_packets:
            self.file_packets[index] = data_chunk
            print(f"Received packet {index}. Total packets received: {len(self.file_packets)}/{num_packets}")
        return self.is_file_complete(num_packets)
    
    def is_file_complete(self, num_packets):
        return len(self.file_packets) == num_packets
    
    def write_file(self, filename):
        self.file_packets = dict(sorted(self.file_packets.items()))  # Sort packets by index
        with open("client_files/" + filename, "wb") as f:
            for i in range(len(self.file_packets)):
                f.write(self.file_packets[i])
        print(f"File written to {filename}")
    
        


if __name__ == "__main__":
    udp_client = Client()