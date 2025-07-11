# SHA-CTR

On the first request we send an empty nonce. `example_flag.bmp` has the same first block as the target file so we can XOR it with the output and get the hash that was used to encrypt the first block. Then using length extension attack we can predict hashes that were used to encrypt the target file in the second request by changing the nonce.

**First request**
```
nonce: ''
counter0: hash(key + '0000000000') - we get the hash from it
```
**Second request**
```
nonce: '0000000000' + padding
counter0: ignore (we already have this block)
counter1: hash(key + '0000000000' + padding + '0000000001') - it was extented by '0000000001'
counter2: hash(key + '0000000000' + padding + '0000000002') - it was extented by '0000000002'
... and so on
```
For each counter we can predict the hash, therefor, decrypt all the output.

Entire solution:
```py
import binascii
import struct
from binascii import unhexlify, hexlify
import itertools
from pwn import *


K = [
    0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
    0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
    0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
    0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
    0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
    0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
    0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
    0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
    0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
    0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
    0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
    0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
    0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
    0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
    0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
    0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
    0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
    0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
    0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817
]


def _rotr(x, n): return (x >> n) | (x << (64 - n)) & 0xFFFFFFFFFFFFFFFF
def _sigma0(x): return _rotr(x, 1) ^ _rotr(x, 8) ^ (x >> 7)
def _sigma1(x): return _rotr(x, 19) ^ _rotr(x, 61) ^ (x >> 6)
def _capsigma0(x): return _rotr(x, 28) ^ _rotr(x, 34) ^ _rotr(x, 39)
def _capsigma1(x): return _rotr(x, 14) ^ _rotr(x, 18) ^ _rotr(x, 41)
def _ch(x, y, z): return (x & y) ^ (~x & z)
def _maj(x, y, z): return (x & y) ^ (x & z) ^ (y & z)


def _sha512_process_block(block, h_vars):
    w = list(struct.unpack('>16Q', block)) + [0] * 64
    for i in range(16, 80):
        w[i] = (_sigma1(w[i-2]) + w[i-7] + _sigma0(w[i-15]) +
                w[i-16]) & 0xFFFFFFFFFFFFFFFF
    a, b, c, d, e, f, g, h = h_vars
    for i in range(80):
        t1 = (h + _capsigma1(e) + _ch(e, f, g) +
              K[i] + w[i]) & 0xFFFFFFFFFFFFFFFF
        t2 = (_capsigma0(a) + _maj(a, b, c)) & 0xFFFFFFFFFFFFFFFF
        h, g, f, e, d, c, b, a = g, f, e, (
            d + t1) & 0xFFFFFFFFFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFFFFFFFFFF
    return [(x + y) & 0xFFFFFFFFFFFFFFFF for x, y in zip(h_vars, [a, b, c, d, e, f, g, h])]


def perform_length_extension(signature_hex, original_data, data_to_add, key_length):
    original_message_len = key_length + len(original_data)
    padding = b'\x80' + b'\x00' * \
        ((112 - (original_message_len + 1) % 128) % 128)
    padding += struct.pack('>QQ', 0, original_message_len * 8)
    forged_message = original_data + padding + data_to_add
    h_vars = list(struct.unpack('>8Q', binascii.unhexlify(signature_hex)))
    total_len_bits = (original_message_len +
                      len(padding) + len(data_to_add)) * 8
    final_data = data_to_add + b'\x80'
    final_data += b'\x00' * ((112 - len(final_data) % 128) % 128)
    final_data += struct.pack('>QQ', 0, total_len_bits)
    for i in range(0, len(final_data), 128):
        h_vars = _sha512_process_block(final_data[i:i+128], h_vars)
    forged_signature = struct.pack('>8Q', *h_vars)
    return forged_signature.hex(), forged_message


def xor(a: bytes, b: bytes) -> bytes:
    return bytes([(aa ^ bb) for (aa, bb) in zip(a, b)])


HOST = 'shactr.ecsc25.hack.cert.pl'
PORT = 5203


r = remote(HOST, PORT)
r.recvuntil(b'nonce:')
r.sendline(b'')
c1 = r.recvline().decode().strip()
c1 = unhexlify(c1)

r.recvuntil(b'nonce:')
payload_bytes = b'0000000000\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01P'
payload_hex = binascii.hexlify(payload_bytes)
r.sendline(payload_hex)
c2 = r.recvall().decode().strip()
c2 = unhexlify(c2)

exb = open('example_flag-d7336f0da14038be1398a47a53b17e38dc35c214.bmp', 'rb').read()[:64]

c1_1block = c1[:64]
sig = hexlify(xor(c1_1block, exb))

dec = [exb]
block_size = 512 // 8
for i, block in enumerate(itertools.batched(c2, block_size)):
    if i == 0:
        continue
    counter = f"{i:010}".encode()

    forged_signature, _ = perform_length_extension(
        signature_hex=sig,
        original_data=b'0'*10,
        data_to_add=counter,
        key_length=32
    )

    dec.append(xor(bytes.fromhex(forged_signature), bytes(block)))

open('flag.bmp', 'wb').write(b''.join(dec))
```

Flag is saved into file `flag.bmp`


![alt text](image.png)