import hashlib
import json
import struct

import numpy as np

from crypto.watermark import embed_bytes, extract_bytes
from crypto import reversible as rev
from crypto import aes

BLOCK = 8
HASH_BITS = 16
HASH_BYTES = HASH_BITS // 8
HASH_CHANNEL = 0
META_CHANNEL = 1
META_STRIP = 8
MASK_VALUE = 255
REV_MAGIC = b"RPEE01"
PARAM_STRIP = 16
MAX_ROUNDS = 16


def _plane(img: np.ndarray, channel: int) -> np.ndarray:
    if img.ndim == 2:
        return img
    return img[:, :, channel]


def _grid(img: np.ndarray):
    h, w = img.shape[:2]
    if img.ndim == 2:
        gh = max((h - META_STRIP) // BLOCK, 0)
    else:
        gh = h // BLOCK
    return gh, w // BLOCK


def block_protection_hashes(img: np.ndarray) -> np.ndarray:
    grid_h, grid_w = _grid(img)
    high = img >> 1
    hashes = np.zeros((grid_h, grid_w), dtype=np.uint16)
    for bi in range(grid_h):
        for bj in range(grid_w):
            block = high[
                bi * BLOCK : (bi + 1) * BLOCK,
                bj * BLOCK : (bj + 1) * BLOCK,
            ]
            digest = hashlib.sha256(block.tobytes()).digest()
            hashes[bi, bj] = int.from_bytes(digest[:HASH_BYTES], "big")
    return hashes


def embed_block_watermarks(img: np.ndarray) -> np.ndarray:
    out = np.array(img, copy=True)
    grid_h, grid_w = _grid(out)
    hashes = block_protection_hashes(out)
    chan = _plane(out, HASH_CHANNEL)
    clear_mask = np.array(1, dtype=chan.dtype)
    for bi in range(grid_h):
        for bj in range(grid_w):
            value = int(hashes[bi, bj])
            for k in range(HASH_BITS):
                row = bi * BLOCK + k // BLOCK
                col = bj * BLOCK + k % BLOCK
                bit = (value >> (HASH_BITS - 1 - k)) & 1
                chan[row, col] = (chan[row, col] & ~clear_mask) | np.uint8(bit)
    return out


def extract_block_watermarks(img: np.ndarray) -> np.ndarray:
    grid_h, grid_w = _grid(img)
    chan = _plane(img, HASH_CHANNEL)
    hashes = np.zeros((grid_h, grid_w), dtype=np.uint16)
    for bi in range(grid_h):
        for bj in range(grid_w):
            value = 0
            for k in range(HASH_BITS):
                row = bi * BLOCK + k // BLOCK
                col = bj * BLOCK + k % BLOCK
                value = (value << 1) | int(chan[row, col] & 1)
            hashes[bi, bj] = value
    return hashes


def localize_tamper(img: np.ndarray) -> tuple:
    grid_h, grid_w = _grid(img)
    current = block_protection_hashes(img)
    stored = extract_block_watermarks(img)
    tampered = current != stored

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    if tampered.any():
        for bi in range(grid_h):
            for bj in range(grid_w):
                if tampered[bi, bj]:
                    mask[
                        bi * BLOCK : (bi + 1) * BLOCK,
                        bj * BLOCK : (bj + 1) * BLOCK,
                    ] = MASK_VALUE
    return bool(tampered.any()), mask


def mark_tampered(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.array(img, copy=True)
    hit = mask > 0
    if out.ndim == 2:
        out[hit] = np.iinfo(out.dtype).max
    else:
        out[hit] = (out[hit] * 0.6).astype(np.uint8)
        out[..., 0][hit] = 255
    return out


def metadata_digest(metadata: bytes) -> bytes:
    return hashlib.sha256(metadata).digest()


def embed_metadata(img: np.ndarray, metadata: bytes) -> np.ndarray:
    digest = metadata_digest(metadata)
    out = np.array(img, copy=True)
    if out.ndim == 2:
        top = out.shape[0] - META_STRIP
        out[top:] = embed_bytes(out[top:], digest, channel=0)
    else:
        out = embed_bytes(out, digest, channel=META_CHANNEL)
    return out


def verify_metadata(img: np.ndarray, metadata: bytes) -> bool:
    digest = metadata_digest(metadata)
    if img.ndim == 2:
        top = img.shape[0] - META_STRIP
        extracted = extract_bytes(img[top:], channel=0)
    else:
        extracted = extract_bytes(img, channel=META_CHANNEL)
    if extracted is None:
        return False
    return extracted == digest


def protect_image(img: np.ndarray, metadata: bytes) -> np.ndarray:
    out = embed_block_watermarks(img)
    return embed_metadata(out, metadata)


def verify_image(img: np.ndarray, metadata: bytes) -> dict:
    has_tamper, mask = localize_tamper(img)
    return {
        "pixel_tamper": has_tamper,
        "mask": mask,
        "metadata_ok": verify_metadata(img, metadata),
    }


def _rev_region(img: np.ndarray) -> np.ndarray:
    return img[: img.shape[0] - PARAM_STRIP]


def _rev_grid(img: np.ndarray, block: int = 16):
    rows = img.shape[0] - PARAM_STRIP
    return rows // block, img.shape[1] // block


def _rev_hashes(img: np.ndarray, block: int = 16, hash_bits: int = 16) -> np.ndarray:
    grid_h, grid_w = _rev_grid(img, block)
    high = _rev_region(img) >> 1
    hb = hash_bits // 8
    hashes = np.zeros((grid_h, grid_w), dtype=np.uint16)
    for bi in range(grid_h):
        for bj in range(grid_w):
            blk = high[
                bi * block : (bi + 1) * block,
                bj * block : (bj + 1) * block,
            ]
            digest = hashlib.sha256(blk.tobytes()).digest()
            hashes[bi, bj] = int.from_bytes(digest[:hb], "big")
    return hashes


def _build_rev_payload(hashes: np.ndarray, metadata: bytes, block: int, hash_bits: int) -> bytes:
    grid_h, grid_w = hashes.shape
    n_blocks = grid_h * grid_w
    return (
        REV_MAGIC
        + bytes([block, hash_bits])
        + struct.pack(">H", n_blocks)
        + metadata_digest(metadata)
        + hashes.astype(">u2").tobytes()
    )


def _parse_rev_payload(data: bytes) -> tuple:
    offset = len(REV_MAGIC)
    if len(data) < offset + 2 + 2 + 32:
        raise ValueError("payload reversible tidak lengkap (header)")
    if data[:offset] != REV_MAGIC:
        raise ValueError("payload reversible tidak dikenal (magic salah)")
    block, hash_bits = data[offset], data[offset + 1]
    n_blocks = struct.unpack(">H", data[offset + 2 : offset + 4])[0]
    digest = data[offset + 4 : offset + 4 + 32]
    raw = data[offset + 4 + 32 :]
    need = n_blocks * (hash_bits // 8)
    if len(raw) < need:
        raise ValueError("payload reversible tidak lengkap (hash blok)")
    hashes = np.frombuffer(raw[:need], dtype=">u2").reshape(-1)
    return block, hash_bits, n_blocks, digest, hashes


def _pack_rounds(rounds: list) -> bytes:
    slim = [{"peak": r["peak"], "z": r["z"], "direction": r["direction"], "n_bits": r["n_bits"]} for r in rounds]
    return json.dumps(slim, separators=(",", ":")).encode()


def _unpack_rounds(data: bytes) -> list:
    return json.loads(data.decode())


def protect_image_rev(
    img: np.ndarray,
    metadata: bytes,
    block: int = 16,
    hash_bits: int = 16,
    max_rounds: int = MAX_ROUNDS,
    passphrase: str = None,
) -> np.ndarray:
    if img.ndim != 2:
        raise ValueError("jalur reversible hanya mendukung grayscale 2D")
    if img.shape[0] <= PARAM_STRIP:
        raise ValueError("ukuran citra terlalu kecil untuk PARAM_STRIP")
    payload = _build_rev_payload(_rev_hashes(img, block, hash_bits), metadata, block, hash_bits)
    if passphrase:
        payload = aes.encrypt(payload, passphrase)
    bits = rev._to_bits(payload)

    region = _rev_region(img)
    wm, rounds = rev.pee_embed_multi(region, bits, max_rounds)
    embedded = sum(r["n_bits"] for r in rounds)
    if embedded < len(bits):
        raise ValueError(
            f"payload {len(bits)} bit melebihi kapasitas reversible {embedded} bit "
            f"({max_rounds} round) - naikkan max_rounds, perbesar blok, atau kecilkan hash"
        )

    out = np.array(img, copy=True)
    out[: img.shape[0] - PARAM_STRIP] = wm
    strip = out[img.shape[0] - PARAM_STRIP :]
    out[img.shape[0] - PARAM_STRIP :] = embed_bytes(strip, _pack_rounds(rounds), channel=0)
    return out


def verify_image_rev(img: np.ndarray, metadata: bytes, passphrase: str = None) -> dict:
    result = {
        "pixel_tamper": True,
        "mask": np.zeros(img.shape[:2], dtype=np.uint8),
        "metadata_ok": False,
        "original_recovered": img,
        "error": None,
    }
    strip = img[img.shape[0] - PARAM_STRIP :]
    raw = extract_bytes(strip, channel=0)
    if raw is None:
        result["error"] = "param strip tidak ditemukan (mungkin terserang wholesale)"
        return result

    try:
        rounds = _unpack_rounds(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        result["error"] = f"param strip rusak: {exc}"
        return result

    region = _rev_region(img)
    try:
        bits = rev.pee_extract_multi(region, rounds)
        recovered_region = rev.pee_reverse_multi(region, rounds)
        payload = rev._from_bits(bits)
    except (ValueError, IndexError) as exc:
        result["error"] = f"ekstraksi reversible gagal: {exc}"
        return result

    recovered = np.array(img, copy=True)
    recovered[: img.shape[0] - PARAM_STRIP] = recovered_region

    if passphrase:
        try:
            payload = aes.decrypt(payload, passphrase)
        except ValueError as exc:
            result["error"] = f"dekripsi AES gagal (kemungkinan kunci salah): {exc}"
            result["original_recovered"] = recovered
            return result

    try:
        block, hash_bits, n_blocks, digest, stored = _parse_rev_payload(payload)
    except ValueError as exc:
        result["error"] = f"payload reversible rusak: {exc}"
        result["original_recovered"] = recovered
        return result

    current = _rev_hashes(recovered, block, hash_bits).ravel()[:n_blocks]
    stored = stored[: len(current)]
    tampered = current != stored

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    grid_h, grid_w = _rev_grid(img, block)
    for bi in range(grid_h):
        for bj in range(grid_w):
            k = bi * grid_w + bj
            if k < len(tampered) and tampered[k]:
                mask[
                    bi * block : (bi + 1) * block,
                    bj * block : (bj + 1) * block,
                ] = MASK_VALUE

    result.update(
        {
            "pixel_tamper": bool(tampered.any()),
            "mask": mask,
            "metadata_ok": digest == metadata_digest(metadata),
            "original_recovered": recovered,
        }
    )
    return result