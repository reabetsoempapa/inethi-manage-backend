import struct
import zlib
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rest_framework.parsers import BaseParser


# TODO: AES-GCM key is hard-coded for now
aesgcm = AESGCM(bytes.fromhex("1d5f4f08478db1ab4b0caa05e3e65d11"))


class InformParser(BaseParser):
    """Parser for unifi's encrypted inform data."""

    # Unifi sends binary data
    media_type = 'application/x-binary'

    @staticmethod
    def parse_inform(data: bytes) -> dict:
        """Parse data from the inform request."""
        headers, payload = data[:40], data[40:]
        magic, version, hardware, flags, iv, payload_version, payload_len = struct.unpack("!II6sh16sII", headers)
        assert magic == 1414414933 and payload_version == 1 and flags == 11
        decrypted = aesgcm.decrypt(iv, payload, headers)
        decompressed = zlib.decompress(decrypted)
        return json.loads(decompressed)

    def parse(self, stream, media_type=None, parser_context=None):
        """Return data as-is so that it can be forwarded to unifi."""
        return stream.read()
