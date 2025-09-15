'''
Constants
'''
MAX_PACKET_SIZE = 1024
DATA_CHUNK_SIZE = 1013  # 1024 - 4 (checksum) - 1 (code) - 3 (num_packets) - 3 (packet_index)
TIMEOUT = 5    # seconds

'''
Client commands:
<checksum> GET_FILE <filename>
<checksum> GET_PACK <filename> <packet_index>
'''
class Commands:
    GET_FILE = "GET_FILE"
    GET_PACKET = "GET_PACK"

'''
Server response:
OK -> <checksum> 0 <num_packets> <packet_index> <data_chunk>
BAD_REQUEST -> <checksum> 1
NOT_FOUND -> <checksum> 2
TOO_LARGE -> <checksum> 3
'''
class Codes:
    OK = 0
    BAD_REQUEST = 1
    NOT_FOUND = 2
    TOO_LARGE = 3