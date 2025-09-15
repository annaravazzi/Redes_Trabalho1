import zlib

def calc_checksum(data):
    return (zlib.crc32(data) & 0xffffffff).to_bytes(4)    # 4 bytes

def verify_checksum(data, checksum):
    return calc_checksum(data) == checksum