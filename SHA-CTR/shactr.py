import binascii
import itertools
import os

from hashlib import sha512

key = os.urandom(32)


def xor(a: bytes, b: bytes) -> bytes:
    return bytes([(aa ^ bb) for (aa, bb) in zip(a, b)])


def encrypt(key: bytes, nonce: bytes, data: bytes) -> bytes:
    res = []
    block_size = 512 // 8
    for i, block in enumerate(itertools.batched(data, block_size)):
        counter = f"{i:010}".encode()
        keystream = sha512(key + nonce + counter).digest()
        res.append(xor(keystream, bytes(block)))
    return b''.join(res)


def get_ciphertext(nonce: bytes) -> bytes:
    data = open("flag.bmp", 'rb').read()
    return encrypt(key, nonce, data)


def main():
    for i in range(2):
        nonce = binascii.unhexlify(input("nonce:"))
        print(binascii.hexlify(get_ciphertext(nonce)).decode())


if __name__ == '__main__':
    main()
