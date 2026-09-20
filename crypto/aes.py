import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"AES1"
BLOCK_SIZE = 16
PBKDF2_ITERATIONS = 200000
SALT_SIZE = 16
IV_SIZE = 16


def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def _pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len


def _unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("padding tidak valid")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("padding tidak valid")
    return data[:-pad_len]


def encrypt(plaintext: bytes, passphrase: str) -> bytes:
    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(IV_SIZE)
    key = derive_key(passphrase, salt)
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(_pad(plaintext)) + encryptor.finalize()
    return MAGIC + salt + iv + ciphertext


def decrypt(payload: bytes, passphrase: str) -> bytes:
    if not payload.startswith(MAGIC):
        raise ValueError("bukan file hasil enkripsi (magic AES1 tidak cocok)")
    salt = payload[len(MAGIC):len(MAGIC) + SALT_SIZE]
    iv = payload[len(MAGIC) + SALT_SIZE:len(MAGIC) + SALT_SIZE + IV_SIZE]
    ciphertext = payload[len(MAGIC) + SALT_SIZE + IV_SIZE:]
    if len(ciphertext) == 0 or len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("panjang ciphertext tidak valid")
    key = derive_key(passphrase, salt)
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return _unpad(plaintext)


def encrypt_file(src_path: str, dst_path: str, passphrase: str) -> None:
    with open(src_path, "rb") as f:
        data = f.read()
    with open(dst_path, "wb") as f:
        f.write(encrypt(data, passphrase))


def decrypt_file(src_path: str, dst_path: str, passphrase: str) -> None:
    with open(src_path, "rb") as f:
        payload = f.read()
    with open(dst_path, "wb") as f:
        f.write(decrypt(payload, passphrase))