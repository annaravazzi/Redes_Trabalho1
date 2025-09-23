"""
Constantes
"""
MAX_PACKET_SIZE = 1024
DATA_CHUNK_SIZE = 1013  # 1024 - 4 (checksum) - 1 (code) - 3 (num_packets) - 3 (packet_index)
MAX_NUM_PACKETS = 16777215  # 2^24 - 1 (3 bytes for num_packets and packet_index)
TIMEOUT = 5    # seconds
DELAY = 0.01  # seconds
DIR_SERVER_FILES = "server_files/"
DIR_CLIENT_FILES = "client_files/"

"""
Comandos do Cliente:
<checksum> GET_FILE <filename>
<checksum> GET_PACK <filename> <packet_index>
"""
class Commands:
    GET_FILE = "GET_FILE"
    GET_PACKET = "GET_PACK"

    GET_WRONG = "GET_WRONG"  # Para testes

"""
Respostas do servidor:
OK          -> <checksum> 0 <num_packets> <packet_index> <data_chunk>
BAD_REQUEST -> <checksum> 1
NOT_FOUND   -> <checksum> 2
TOO_LARGE   -> <checksum> 3
"""
class Codes:
    OK = 0
    BAD_REQUEST = 1
    NOT_FOUND = 2
    TOO_LARGE = 3

    UNKNOWN = 4  # Para testes