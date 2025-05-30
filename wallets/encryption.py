import os
import base64
import binascii
from itertools import cycle
from typing import Optional

_KEY = os.getenv("WALLET_ENCRYPTION_KEY", "simplekey").encode()


def _xor(data: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, cycle(_KEY)))


def encrypt_key(plain: Optional[str]) -> Optional[str]:
    if plain is None:
        return None
    enc = _xor(plain.encode())
    return base64.b64encode(enc).decode()


def decrypt_key(enc: Optional[str]) -> Optional[str]:
    """Decrypt a value if it appears to be encoded, otherwise return as-is."""
    if enc is None:
        return None
    try:
        data = base64.b64decode(enc)
        dec = _xor(data)
        return dec.decode()
    except (binascii.Error, ValueError):
        # Value was not base64-encoded; treat as plain text
        return enc
