import struct

import numpy as np

MAGIC = b"KPGW"
HEADER_BYTES = len(MAGIC) + 4
HEADER_BITS = HEADER_BYTES * 8


def _to_bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def _from_bits(bits: np.ndarray) -> bytes:
    return np.packbits(bits).tobytes()


def _plane(img: np.ndarray, channel: int) -> np.ndarray:
    if img.ndim == 2:
        return img
    return img[:, :, channel]


def embed_bytes(img: np.ndarray, data: bytes, channel: int = 1) -> np.ndarray:
    if data is None:
        raise ValueError("data kosong")
    payload = MAGIC + struct.pack(">I", len(data)) + data
    bits = _to_bits(payload)

    out = np.array(img, copy=True)
    chan = _plane(out, channel)
    clear_mask = np.array(1, dtype=chan.dtype)
    rows, cols = np.unravel_index(np.arange(bits.size), chan.shape)
    chan[rows, cols] = (chan[rows, cols] & ~clear_mask) | bits
    return out


def extract_bytes(img: np.ndarray, channel: int = 1):
    chan = _plane(img, channel)
    flat = chan.ravel()

    if flat.size < HEADER_BITS:
        return None
    header_rows, header_cols = np.unravel_index(
        np.arange(HEADER_BITS), chan.shape
    )
    header = _from_bits(chan[header_rows, header_cols] & 1)
    if header[:len(MAGIC)] != MAGIC:
        return None

    length = struct.unpack(">I", header[len(MAGIC):])[0]
    total_bits = HEADER_BITS + length * 8
    if flat.size < total_bits:
        return None
    payload_rows, payload_cols = np.unravel_index(
        np.arange(HEADER_BITS, total_bits), chan.shape
    )
    payload = _from_bits(chan[payload_rows, payload_cols] & 1)
    return payload


def lsb_capacity(img: np.ndarray, channel: int = 1) -> int:
    plane = _plane(img, channel)
    return plane.shape[0] * plane.shape[1] // 8 - HEADER_BYTES