"""
Pequena biblioteca para calcular e verificar checksums usando o algoritmo CRC32.
"""

import zlib

def calc_checksum(data):
    """
    Calcula o checksum CRC32 dos dados fornecidos (bytes).
    Retorna o checksum como bytes.
    """
    return (zlib.crc32(data) & 0xffffffff).to_bytes(4)    # 4 bytes

def verify_checksum(data, checksum):
    """
    Verifica se o checksum dos dados fornecidos corresponde ao checksum fornecido.
    """
    return calc_checksum(data) == checksum